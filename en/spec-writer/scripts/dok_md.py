# -*- coding: utf-8 -*-
"""JSON içeriğini tek Markdown dosyasına ya da Obsidian vault klasörüne döker. Yalnız standart kütüphane."""
import os
import re
import shutil

KIMLIK = re.compile(r"(?<![\w-])([A-Z]{1,5})-\d{2,3}(?!\d)")


def h(v):
    return str(v if v is not None else "").replace("|", "\\|").replace("\n", "<br>")


def tablo(basliklar, satirlar):
    out = ["| " + " | ".join(h(x) for x in basliklar) + " |", "|" + "|".join("---" for _ in basliklar) + "|"]
    out += ["| " + " | ".join(h(c) for c in s) + " |" for s in satirlar]
    return "\n".join(out)


def guvenli(ad):
    return re.sub(r'[\\/:*?"<>|#^\[\]]', "-", ad.replace(" / ", " - ")).replace("  ", " ").strip()


def ust_bilgi(belge, ctx):
    a = (belge.get("bolumler", {}).get("1.1", {}).get("alanlar") or {})
    m = belge.get("meta") or {}
    turler = ", ".join(ctx["tur_ad"].get(t, t) for t in belge.get("turler") or [])
    return a.get("gel_id") or "FS-TS", a.get("baslik") or "", [
        ("Sürüm", m.get("surum", "")), ("Tarih", m.get("tarih", "")), ("Hazırlayan", m.get("hazirlayan", "")), ("Durum", m.get("durum", "")),
        ("Müşteri / proje", m.get("musteri", "")), ("Geliştirme türleri", turler), ("Profil", belge.get("profil", ""))]


def bolum_govdesi(v, seviye="###"):
    out = []
    if v["durum"] != "gecerli":
        return [f"Geçerli değil – {v['gerekce']}", ""]
    if v["alanlar"]:
        out += [tablo(["Alan", "Değer"], v["alanlar"]), ""]
    if v["satirlar"]:
        out += [tablo(v["sutunlar"], v["satirlar"]), ""]
    if v["mermaid"]:
        out += ["```mermaid", v["mermaid"], "```", ""]
    return out


def denetim_eki(ctx):
    out = list(ctx["ozet"]) + [""]
    if ctx["bulgular"]:
        out += [tablo(["Önem", "Kural", "Konum", "Bulgu"], [[b["sev"], b["kural"], b["yol"], b["mesaj"]] for b in ctx["bulgular"][:60]]), ""]
    else:
        out += ["Mekanik denetimde bulgu yok.", ""]
    out.append("Gösterge yalnız mekanik kurallardan hesaplanır ve varsayılan parametrelere dayanır; kalite (LLM) puanını gerçek puanlama motoru ölçer.")
    return out


def tek_dosya(belge, ctx, hedef):
    kimlik, baslik, meta = ust_bilgi(belge, ctx)
    out = [f"# FS-TS · {kimlik} — {baslik}", "", tablo(["Alan", "Değer"], meta), ""]
    if belge.get("surum_gecmisi"):
        out += ["## Sürüm geçmişi", "", tablo(["Sürüm", "Tarih", "Yazan", "Değişiklik"], belge["surum_gecmisi"]), ""]
    if belge.get("onaylar"):
        out += ["## Onaylar", "", tablo(["Rol", "Ad soyad", "Tarih"], belge["onaylar"]), ""]
    for g in ctx["gorunum"]:
        out += [f"## {g['no']} {g['ad']}", ""]
        for v in g["bolumler"]:
            out += [f"### {v['no']} {v['baslik']}", ""] + bolum_govdesi(v)
    out += ["## Ek A: Mekanik denetim özeti", ""] + denetim_eki(ctx)
    with open(hedef, "w", encoding="utf-8") as f:
        f.write("\n".join(out).rstrip() + "\n")


def vault(belge, ctx, hedef):
    kimlik, baslik, meta = ust_bilgi(belge, ctx)
    os.makedirs(hedef, exist_ok=True)
    not_adi = {v["no"]: guvenli(f"{v['no']} {v['baslik']}") for g in ctx["gorunum"] for v in g["bolumler"]}
    ev = {}  # kimlik -> bölüm no
    for g in ctx["gorunum"]:
        for v in g["bolumler"]:
            for s in v["satirlar"]:
                if s and KIMLIK.fullmatch(str(s[0])) and v["no"] not in ("3.7", "5.4", "6.2"):
                    ev.setdefault(s[0], v["no"])

    def yaz(yol, satirlar):
        tam = os.path.join(hedef, yol)
        os.makedirs(os.path.dirname(tam), exist_ok=True)
        with open(tam, "w", encoding="utf-8") as f:
            f.write("\n".join(satirlar).rstrip() + "\n")

    harita = ["---", "tags: [fs-ts-harita]", "---"]
    if ctx.get("logo"):
        os.makedirs(os.path.join(hedef, "assets"), exist_ok=True)
        shutil.copy(ctx["logo"], os.path.join(hedef, "assets", "logo.png"))
        harita.append("![[logo.png|180]]")
    harita += ["", f"# FS-TS · {kimlik} — {baslik}", "", tablo(["Alan", "Değer"], meta), ""]
    for g in ctx["gorunum"]:
        harita += [f"## {g['no']} {g['ad']}", ""]
        satirlar = []
        for v in g["bolumler"]:
            durum = "Yazıldı" if v["durum"] == "gecerli" else "Geçerli değil"
            satirlar.append([f"[[{not_adi[v['no']]}\\|{v['no']}]]", h(v["baslik"]), v["agirlik"], v["sinif"], durum, len(v["satirlar"])])
            atif = sorted({ev[m.group(0)] for s in v["satirlar"] for c in s for m in KIMLIK.finditer(str(c)) if m.group(0) in ev} - {v["no"]},
                          key=lambda n: [int(x) for x in n.split(".")])
            govde = ["---", f'id: "{v["no"]}"', f'baslik: "{v["baslik"]}"', f'grup: "{g["no"]} {g["ad"]}"', f"agirlik: {v['agirlik']}",
                     f"sinif: {v['sinif']}", f"gecerli: {'Evet' if v['durum'] == 'gecerli' else 'Hayır'}",
                     "atif: [" + ", ".join(f'"[[{not_adi[n]}]]"' for n in atif) + "]", f"tags: [fs-ts, {v['sinif'].lower()}]", "---",
                     f"# {v['no']} {v['baslik']}", ""] + bolum_govdesi(v)
            if atif:
                govde += ["**Atıf yapılan bölümler:** " + " · ".join(f"[[{not_adi[n]}|{n}]]" for n in atif), ""]
            govde += ["---", "← [[00 Harita]]"]
            yaz(os.path.join(f"{g['no']} {g['ad']}", not_adi[v["no"]] + ".md"), govde)
        harita += ["| No | Başlık | Ağırlık | Sınıf | Durum | Satır |", "|---|---|---|---|---|---|"]
        harita += ["| " + " | ".join(str(c) for c in s) + " |" for s in satirlar] + [""]
    if belge.get("surum_gecmisi"):
        harita += ["## Sürüm geçmişi", "", tablo(["Sürüm", "Tarih", "Yazan", "Değişiklik"], belge["surum_gecmisi"]), ""]
    if belge.get("onaylar"):
        harita += ["## Onaylar", "", tablo(["Rol", "Ad soyad", "Tarih"], belge["onaylar"]), ""]
    harita += ["Denetim özeti: [[Ek A Mekanik denetim özeti]]"]
    yaz("00 Harita.md", harita)
    yaz("Ek A Mekanik denetim özeti.md", ["# Ek A: Mekanik denetim özeti", ""] + denetim_eki(ctx) + ["", "← [[00 Harita]]"])


def uret(belge, ctx, hedef, bicim):
    (tek_dosya if bicim == "md" else vault)(belge, ctx, hedef)
