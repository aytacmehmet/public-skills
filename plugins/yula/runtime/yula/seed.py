"""Bounded, verified seed extraction into explicitly selected external storage."""
from __future__ import annotations

import hashlib
import os
import uuid
import zipfile
from contextlib import contextmanager
from pathlib import Path

from .common import PLUGIN, YulaError, data_root, file_hash, load_json, require_hash

MAX_SEED_BYTES = 2 * 1024**3
MAX_ARCHIVE_BYTES = 100 * 1024**2


def archive_info():
    manifest = load_json(PLUGIN / "data/manifest.json")
    package = manifest.get("distribution", {})
    if (package.get("format"), package.get("path"), package.get("member")) != (
            "zip", "yula.sqlite.zip", "yula.sqlite"):
        raise YulaError("SEED_FORMAT", "Expected the single-member Yula seed ZIP.")
    size = manifest.get("bytes")
    archive_size = package.get("bytes")
    if (type(size) is not int or not 0 < size <= MAX_SEED_BYTES or
            type(archive_size) is not int or not 0 < archive_size < MAX_ARCHIVE_BYTES):
        raise YulaError("SEED_SIZE", "Packaged seed exceeds its distribution bounds.")
    require_hash(manifest.get("sha256"))
    require_hash(package.get("sha256"))
    archive = PLUGIN / "data/yula.sqlite.zip"
    if not archive.is_file() or archive.stat().st_size != archive_size:
        raise YulaError("SEED_CORRUPT", "Packaged seed archive is missing or has an unexpected size.")
    if file_hash(archive) != package["sha256"]:
        raise YulaError("SEED_CORRUPT", "Packaged seed archive differs from its manifest.")
    return manifest, archive


@contextmanager
def unpack_seed(staging_root):
    """Never extract archive paths or mutate the installed plugin; always clean staging."""
    manifest, archive = archive_info()
    root = data_root(str(staging_root))
    root.mkdir(parents=True, exist_ok=True)
    destination = root / ("seed-" + uuid.uuid4().hex + ".tmp")
    try:
        try:
            with zipfile.ZipFile(archive) as bundle:
                members = bundle.infolist()
                if len(members) != 1 or members[0].filename != "yula.sqlite":
                    raise YulaError("SEED_FORMAT", "Seed ZIP must contain only yula.sqlite.")
                member = members[0]
                if (member.is_dir() or member.flag_bits & 1 or
                        member.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
                    raise YulaError("SEED_FORMAT", "Unsupported seed ZIP entry.")
                if member.file_size != manifest["bytes"]:
                    raise YulaError("SEED_SIZE", "Seed size differs from its manifest.")
                size, sha = 0, hashlib.sha256()
                with bundle.open(member) as source, destination.open("xb") as target:
                    while chunk := source.read(1024 * 1024):
                        size += len(chunk)
                        if size > manifest["bytes"]:
                            raise YulaError("SEED_SIZE", "Expanded seed exceeds its declared size.")
                        sha.update(chunk)
                        target.write(chunk)
                    target.flush()
                    os.fsync(target.fileno())
                if size != manifest["bytes"] or sha.hexdigest() != manifest["sha256"]:
                    raise YulaError("SEED_CORRUPT", "Expanded SQLite differs from its manifest.")
        except (zipfile.BadZipFile, EOFError, RuntimeError) as exc:
            raise YulaError("SEED_CORRUPT", "Seed ZIP cannot be decoded or failed its CRC.") from exc
        yield destination
    finally:
        destination.unlink(missing_ok=True)
