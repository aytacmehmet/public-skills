from __future__ import annotations

import json
import os
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import VERSION

from .common import YulaError, atomic_json, digest, encode, file_hash, load_json, now, official_url


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise YulaError("REDIRECT_REJECTED", "Configure the verified final source URL; redirects are not followed.")


class Fetcher:
    """Bounded HTTPS GET. Complete response checkpoints are reusable; partial bytes are never trusted."""
    def __init__(self, cache, timeout=25, retries=2):
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.timeout = min(30, max(1, int(timeout)))
        self.retries = min(2, max(0, int(retries)))
        self.opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=ssl.create_default_context()))

    def get(self, url, max_bytes=32 * 1024 * 1024, immutable=False, auth_env=None, origin=None, use_cache=True):
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or parsed.username or parsed.password:
            raise YulaError("SOURCE_URL", "Sources require HTTPS without embedded credentials.")
        actual_origin = f"https://{parsed.netloc}"
        if origin:
            if actual_origin != origin or not parsed.path.startswith("/sap/bc/adt/"):
                raise YulaError("SAP_ORIGIN", "SAP reads must stay on the configured ADT origin.")
        elif not official_url(url):
            raise YulaError("SOURCE_ORIGIN", "Online sources must use an official SAP origin.")
        # Authenticated SAP payloads never enter the shared HTTP cache.
        cacheable = use_cache and not origin and not auth_env
        key = digest(url.encode())
        body_path, meta_path = self.cache / (key + ".body"), self.cache / (key + ".json")
        meta = None
        if cacheable and body_path.exists() and meta_path.exists():
            candidate = load_json(meta_path)
            if body_path.stat().st_size <= max_bytes and file_hash(body_path) == candidate.get("sha256"):
                meta = candidate
        if immutable and meta:
            return body_path.read_bytes(), meta
        headers = {"User-Agent": "yula/"+VERSION+" source-maintenance", "Accept": "application/json, application/xml, text/plain, */*"}
        if meta and meta.get("etag"):
            headers["If-None-Match"] = meta["etag"]
        if meta and meta.get("lastModified"):
            headers["If-Modified-Since"] = meta["lastModified"]
        if auth_env:
            secret = os.environ.get(auth_env)
            if not secret:
                raise YulaError("AUTH_MISSING", "The configured authorization environment variable is unset.", variable=auth_env)
            if "\n" in secret or "\r" in secret:
                raise YulaError("AUTH_INVALID", "Invalid authorization value.")
            headers["Authorization"] = secret
        for attempt in range(self.retries + 1):
            try:
                request = urllib.request.Request(url, headers=headers, method="GET")
                with self.opener.open(request, timeout=self.timeout) as response:
                    declared = response.headers.get("Content-Length")
                    if declared and int(declared) > max_bytes:
                        raise YulaError("SOURCE_TOO_LARGE", "Response exceeds this adapter's bound.")
                    body = response.read(max_bytes + 1)
                    if len(body) > max_bytes:
                        raise YulaError("SOURCE_TOO_LARGE", "Response exceeds this adapter's bound.")
                    if declared and len(body) != int(declared):
                        raise YulaError("SOURCE_INCOMPLETE", "Response length does not match Content-Length.")
                    meta = {"sha256": digest(body), "fetchedAt": now(), "etag": response.headers.get("ETag"),
                            "lastModified": response.headers.get("Last-Modified"), "bytes": len(body)}
                if cacheable:
                    import uuid
                    tmp = body_path.with_suffix("." + uuid.uuid4().hex + ".tmp")
                    try:
                        tmp.write_bytes(body); os.replace(tmp, body_path)
                    finally:
                        tmp.unlink(missing_ok=True)
                    atomic_json(meta_path, meta)
                return body, meta
            except urllib.error.HTTPError as exc:
                if exc.code == 304 and meta:
                    return body_path.read_bytes(), {**meta, "checkedAt": now()}
                retry = exc.code in (408, 429, 500, 502, 503, 504)
                if not retry or attempt == self.retries:
                    raise YulaError("SOURCE_HTTP", "Source request failed.", status=exc.code) from None
            except (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError):
                if attempt == self.retries:
                    raise YulaError("SOURCE_UNREACHABLE", "Source request failed or timed out; active data is unchanged.") from None
            time.sleep(min(2 ** attempt, 2))
        raise YulaError("SOURCE_UNREACHABLE", "Source request failed.")

    def json(self, url, **options):
        body, meta = self.get(url, **options)
        try:
            return json.loads(body), meta
        except (ValueError, UnicodeError):
            raise YulaError("SOURCE_FORMAT", "Expected valid UTF-8 JSON.") from None
