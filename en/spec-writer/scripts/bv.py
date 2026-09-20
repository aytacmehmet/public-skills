#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Belirtim Yazmanı (Spec Writer) çekirdek aracı. Yalnız standart kütüphane kullanır.

Komutlar: bilgi · iskelet · eksik · denetle · yama · ozet · dok
Kullanım: python scripts/bv.py <komut> --help
"""
import argparse
import datetime
import json
import os
import re
import sys

for _akis in (sys.stdout, sys.stderr):  # Windows konsolu varsayılan kod sayfasında Türkçe karakterlerde çöküyor
    if hasattr(_akis, "reconfigure"):
        _akis.reconfigure(encoding="utf-8", errors="replace")

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(KOK, "assets", "tanim.json"), encoding="utf-8"))
BOLUM = {b["no"]: b for b in T["bolumler"]}
GRUP = {g["no"]: g["ad"] for g in T["gruplar"]}
TUR_AD = {t["kod"]: t["ad"] for t in T["tur_tanimlari"]}
PAR = T["parametreler"]
ISARET = T["isaretler"]
YOK = ISARET["yok"]
ONEKLER = sorted({p for b in T["bolumler"] for c in b["sutunlar"][:1] for p in c.get("kimlik", [])}, key=len, reverse=True)
KIMLIK_RE = re.compile(r"(?<![\w-])(" + "|".join(ONEKLER) + r")-\d{2,3}(?!\d)")
YER_TUTUCU_RE = [re.compile(p, re.I) for p in T["yer_tutucu_kaliplari"]]
NK = T["nesne_kaliplari"]
OZEL_RE = [re.compile(p) for p in NK["ozel"]]
STD_RE = [re.compile(p) for p in NK["standart"]]
STD_GENIS_RE = [re.compile(p) for p in NK.get("standart_genis", [])]
APP_RE = [re.compile(p) for p in NK["uygulama"]]


def kucuk(s):
    return s.replace("İ", "i").replace("I", "ı").lower()


# Kısa kalıplar tam sözcük olarak, uzun kalıplar Türkçe ek alabilecek biçimde aranır ("gerekli kontrol" → "gerekli kontroller").
YUVARLAK_RE = [(f, re.compile(r"(?<!\w)" + re.escape(kucuk(f.strip())) + (r"(?!\w)" if len(f.strip()) <= 4 else "")))
               for f in T["yuvarlak_ifadeler"]]


# ----------------------------------------------------------------------------- temel
def yukle(yol):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def kaydet(belge, yol):
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(belge, f, ensure_ascii=False, indent=1)


def bolum_durumu(b, turler, profil):
    """'gecerli' | 'tur_disi' | 'profil_disi'"""
    if b["turler"] != ["*"] and turler and not set(b["turler"]) & set(turler):
        return "tur_disi"
    if b["sinif"] == "Bonus" and profil != "tam":
        acilis = b.get("bonus_acilis", [])
        if "*" in acilis:
            return "gecerli"
        if profil == "standart" and set(acilis) & set(turler):
            return "gecerli"
        return "profil_disi"
    return "gecerli"


def tur_metni(b):
    return "tüm türler" if b["turler"] == ["*"] else "yalnız " + ", ".join(TUR_AD[t] for t in b["turler"])


def isaretli(metin):
    return ISARET["karar"] in metin or ISARET["bilgi"] in metin


def hucreler(belge):
    """(bolum_no, json_yolu, metin) üretir."""
    for no, ic in belge.get("bolumler", {}).items():
        if not isinstance(ic, dict) or ic.get("gecerli") is False:
            continue
        for k, v in (ic.get("alanlar") or {}).items():
            yield no, f"/bolumler/{no}/alanlar/{k}", v if isinstance(v, str) else ""
        for i, satir in enumerate(ic.get("satirlar") or []):
            if isinstance(satir, list):
                for j, v in enumerate(satir):
                    yield no, f"/bolumler/{no}/satirlar/{i}/{j}", v if isinstance(v, str) else ""


YOKSAY = set(NK["haric"])


def nesneler(metin, genis=False):
    """(özel, standart, uygulama) nesne adı kümeleri. 'NESNE.alan' biçimindeki alan adları nesne sayılmaz.
    genis=True: BAdI gibi büyük harfli, alt çizgili adlar da aranır; yalnız nesne adı taşıyan sütunlarda kullanılır."""
    ozel, std, app = set(), set(), set()
    bul_ = lambda r: [m.group(0) for m in r.finditer(metin) if m.start() == 0 or metin[m.start() - 1] != "."]
    for r in OZEL_RE:
        ozel.update(bul_(r))
    for r in STD_RE + (STD_GENIS_RE if genis else []):
        std.update(x for x in bul_(r) if x not in ozel and not x.startswith(("Z", "Y")))
    for r in APP_RE:
        app.update(bul_(r))
    return ozel - YOKSAY, std - YOKSAY, app - YOKSAY


def kimlik_tablosu(belge):
    """kimlik -> (bolum_no, satir_index); ayrıca yinelenenler."""
    tablo, yinelenen = {}, []
    for no, ic in belge.get("bolumler", {}).items():
        b = BOLUM.get(no)
        if not b or not isinstance(ic, dict) or not b["sutunlar"] or not b["sutunlar"][0].get("kimlik"):
            continue
        for i, satir in enumerate(ic.get("satirlar") or []):
            if isinstance(satir, list) and satir and isinstance(satir[0], str):
                if satir[0] in tablo:
                    yinelenen.append((satir[0], no, i))
                tablo[satir[0]] = (no, i)
    return tablo, yinelenen


def komsuluk(belge):
    """Kimlikler arası yönsüz atıf grafiği."""
    tablo, _ = kimlik_tablosu(belge)
    g = {k: set() for k in tablo}
    for no, ic in belge.get("bolumler", {}).items():
        if not isinstance(ic, dict):
            continue
        b = BOLUM.get(no)
        kendi = bool(b and b["sutunlar"] and b["sutunlar"][0].get("kimlik"))
        for satir in ic.get("satirlar") or []:
            if not isinstance(satir, list) or not satir:
                continue
            anilan = {m.group(0) for h in satir[1 if kendi else 0:] if isinstance(h, str) for m in KIMLIK_RE.finditer(h)}
            if kendi and satir[0] in g:
                for a in anilan:
                    if a in g:
                        g[satir[0]].add(a)
                        g[a].add(satir[0])
            elif not kendi:  # kimliği olmayan satır (3.7, 4.2, 5.4, 7.2): andıklarını birbirine bağlar
                for a in anilan:
                    for c in anilan:
                        if a != c and a in g and c in g:
                            g[a].add(c)
    return g


def turet_62(belge):
    """6.2 İzlenebilirlik matrisi: REQ başına tek satır."""
    g = komsuluk(belge)
    sirala = lambda ks: ", ".join(sorted(ks)) or YOK
    on = lambda ks, p: {k for k in ks if k.rsplit("-", 1)[0] == p}
    satirlar = []
    for req in sorted(k for k in g if k.startswith("REQ-")):
        sc = on(g[req], "SC")
        step = on(g[req], "STEP") | {s for c in sc for s in on(g[c], "STEP")}
        cevre = set().union(*[g[s] for s in step]) if step else set()
        tc = on(g[req], "TC") | {t for c in sc for t in on(g[c], "TC")}
        kapsama = "Tam" if sc and step and tc else "Kısmi" if step or tc else "Yok"
        satirlar.append([req, sirala(sc), sirala(step), sirala(on(cevre, "OBJ")), sirala(on(cevre | g[req], "MAP")),
                         sirala(on(cevre | g[req], "MSG")), sirala(tc), kapsama])
    return satirlar


def birlestir_54(belge):
    b = BOLUM["5.4"]
    kaynak = {s[0]: s for s in (belge.get("bolumler", {}).get("5.1", {}).get("satirlar") or []) if isinstance(s, list) and s}
    adlar = [b["sutunlar"][0]["ad"]] + [e[0] for e in b["birlestir"]["ekle"]] + [c["ad"] for c in b["sutunlar"][1:]]
    satirlar = []
    for s in belge.get("bolumler", {}).get("5.4", {}).get("satirlar") or []:
        k = kaynak.get(s[0], [])
        satirlar.append([s[0]] + [k[i] if len(k) > i else YOK for _, i in b["birlestir"]["ekle"]] + list(s[1:]))
    return adlar, satirlar


# ----------------------------------------------------------------------------- denetim
def denetle(belge, proje=None, girdi_metni=""):
    """Bulgu listesi, motor kurallarının bölüm bazında sonucu ve sayılan bölümler.
    'acik' bulgular bir karar/bilgi bekleyen hücreden doğar: gösterge için kural kalır ama düzeltilecek kusur değildir."""
    proje = proje or {}
    YOKSAY.clear(); YOKSAY.update(NK["haric"]); YOKSAY.update(belge.get("nesne_degil") or [])
    bulgular, kural_sonuc = [], {}
    turler, profil = belge.get("turler") or [], belge.get("profil") or "standart"
    icerik = belge.get("bolumler") or {}

    def bul(sev, kural, yol, mesaj, no=None, acik=False):
        bulgular.append({"sev": sev, "kural": kural, "yol": yol, "mesaj": mesaj, "bolum": no, "acik": acik})

    def kal(no, kural):
        kural_sonuc.setdefault(no, {})[kural] = False

    def hal(h):
        """'dolu' | 'isaret' | 'bos'"""
        if not isinstance(h, str) or not h.strip() or h.strip() == YOK:
            return "bos"
        return "isaret" if isaretli(h) else "dolu"

    def eksik_kural(no, kural, sev, yol, hucre_listesi, mesaj):
        """Hücrelerden biri dolu değilse kuralı düşürür; neden yalnız işaretse bulgu 'açık' olur."""
        haller = [hal(h) for h in hucre_listesi]
        if all(x == "dolu" for x in haller):
            return
        kal(no, kural)
        bul(sev, kural, yol, mesaj, no, acik="bos" not in haller)

    # --- üst yapı
    if belge.get("sema") != T["sema"]:
        bul("UYARI", "YAPI_001", "/sema", f"Şema sürümü {T['sema']} bekleniyor, bulunan: {belge.get('sema')}")
    if not turler or any(t not in TUR_AD for t in turler):
        bul("HATA", "META_001", "/turler", "En az bir geçerli RICEF türü gerekli: " + ", ".join(TUR_AD))
    if profil not in T["profiller"]:
        bul("HATA", "YAPI_001", "/profil", "Profil hafif, standart ya da tam olmalı")
    meta = belge.get("meta") or {}
    bos_meta = [k for k in ("surum", "tarih", "hazirlayan", "durum") if not str(meta.get(k) or "").strip()]
    if bos_meta:
        bul("UYARI", "YAPI_010", "/meta", "Boş meta alanları: " + ", ".join(bos_meta) + f" (bilinmiyorsa {YOK})")
    for ad, n in (("surum_gecmisi", 4), ("onaylar", 3)):
        for i, s in enumerate(belge.get(ad) or []):
            if not isinstance(s, list) or len(s) != n or not all(isinstance(h, str) and h.strip() for h in s):
                bul("UYARI", "YAPI_010", f"/{ad}/{i}", f"Satır {n} dolu hücreli dizi olmalı (yoksa {YOK})")
    for no in icerik:
        if no not in BOLUM:
            bul("HATA", "YAPI_001", f"/bolumler/{no}", "Tanımsız bölüm numarası")
    if "6.2" in icerik:
        bul("UYARI", "YAPI_007", "/bolumler/6.2", "6.2 türetilir; JSON'a yazmayın")

    sayilan = {}  # no -> 'taban' | 'bonus'
    for b in T["bolumler"]:
        no, ic = b["no"], icerik.get(b["no"])
        durum = bolum_durumu(b, turler, profil)
        if b.get("turetilmis"):
            if durum == "gecerli" and turet_62(belge):
                sayilan[no] = "bonus"
                kural_sonuc[no] = {k: True for k in b["kurallar"]}
            continue
        if durum == "tur_disi":
            if isinstance(ic, dict) and (ic.get("satirlar") or ic.get("alanlar")):
                bul("UYARI", "YAPI_008", f"/bolumler/{no}", f"Bölüm seçili türlerde geçerli değil ({tur_metni(b)}); içerik yok sayılır", no)
            continue
        if durum == "profil_disi" and not ic:
            continue
        if ic is None and b["sinif"] == "Bonus":
            bul("BİLGİ", "GEN_002", f"/bolumler/{no}", f"Profilde açık bonus bölüm yazılmamış: {no} {b['baslik']}", no)
            continue
        if ic is None:
            bul("HATA" if b["sinif"] == "Kritik" else "UYARI", "GEN_002", f"/bolumler/{no}", f"{no} {b['baslik']} eksik", no)
            sayilan[no] = "taban"
            kural_sonuc[no] = {k: False for k in b["kurallar"]}
            continue
        if ic.get("gecerli") is False:
            if b["sinif"] == "Kritik":
                bul("HATA", "KRITIK_001", f"/bolumler/{no}", "Kritik bölüm elle geçersiz kılınamaz", no)
            elif not str(ic.get("gerekce") or "").strip():
                bul("UYARI", "YAPI_009", f"/bolumler/{no}/gerekce", "Geçersiz kılınan bölüm gerekçe ister", no)
            continue
        sayilan[no] = "bonus" if b["sinif"] == "Bonus" else "taban"
        kural_sonuc[no] = {k: True for k in b["kurallar"]}
        alanlar, satirlar = ic.get("alanlar") or {}, ic.get("satirlar") or []
        tanimli = [a["anahtar"] for a in b["alanlar"]]
        for a in b["alanlar"]:
            v = alanlar.get(a["anahtar"])
            if not isinstance(v, str) or not v.strip():
                bul("UYARI", "GEN_002", f"/bolumler/{no}/alanlar/{a['anahtar']}", f"'{a['etiket']}' boş", no)
                kal(no, "GEN_002")
            elif a.get("secenekler") and v not in a["secenekler"] and v.strip() != YOK and not isaretli(v):
                bul("BİLGİ", "YAPI_003", f"/bolumler/{no}/alanlar/{a['anahtar']}", "Tercih edilen ifade: " + " | ".join(a["secenekler"])
                    + " (hiçbiri uymuyorsa verilen kararı kendi sözleriyle bırakın)", no)
        for k in alanlar:
            if k not in tanimli:
                bul("UYARI", "YAPI_002", f"/bolumler/{no}/alanlar/{k}", "Tanımsız alan anahtarı", no)
        n = len(b["sutunlar"])
        if n and len(satirlar) < b["en_az_satir"]:
            bul("UYARI", "GEN_002", f"/bolumler/{no}/satirlar", f"En az {b['en_az_satir']} satır gerekli, bulunan {len(satirlar)}", no)
            kal(no, "GEN_002")
        for i, s in enumerate(satirlar):
            yol = f"/bolumler/{no}/satirlar/{i}"
            if not isinstance(s, list) or len(s) != n:
                bul("HATA", "YAPI_002", yol, f"Satır {n} hücreli dizi olmalı", no)
                continue
            for j, (h, c) in enumerate(zip(s, b["sutunlar"])):
                if not isinstance(h, str) or not h.strip():
                    bul("UYARI", "GEN_002", f"{yol}/{j}", f"Boş hücre ('{c['ad']}'); yoksa {YOK} yazın", no)
                    kal(no, "GEN_002")
                elif c.get("secenekler") and h not in c["secenekler"] and not isaretli(h):
                    bul("UYARI", "YAPI_003", f"{yol}/{j}", f"'{c['ad']}' şunlardan biri ya da bir BEKLİYOR işareti olmalı: " + " | ".join(c["secenekler"]), no)
                elif j == 0 and c.get("kimlik") and not re.fullmatch("(" + "|".join(c["kimlik"]) + r")-\d{2,3}", h):
                    bul("HATA", "YAPI_005", f"{yol}/0", f"Kimlik {c['kimlik'][0]}-nn biçiminde olmalı", no)

    # --- yer tutucu, açık hücre, yuvarlak ifade
    toplam, acik_say = {}, {}
    for no, yol, m in hucreler(belge):
        if no not in sayilan:
            continue
        toplam[no] = toplam.get(no, 0) + 1
        if any(r.search(m) for r in YER_TUTUCU_RE):
            bul("UYARI", "GEN_001", yol, "Yer tutucu metin kalmış", no)
            kal(no, "GEN_001")
        if isaretli(m):
            acik_say[no] = acik_say.get(no, 0) + 1
            if not re.search(r"OPEN-\d{2,3}", m):
                bul("UYARI", "KARAR_001", yol, "BEKLİYOR işareti bir OPEN-nn kimliği taşımalı", no)
        if no in ("2.1", "2.2", "3.5"):
            km = kucuk(m)
            for f, r in YUVARLAK_RE:
                if r.search(km):
                    bul("UYARI", {"2.1": "QUAL_003", "2.2": "PROC_001", "3.5": "ALGO_003"}[no], yol, f"Yuvarlak ifade: '{f.strip()}'", no)
                    if no != "2.1":
                        kal(no, {"2.2": "PROC_001", "3.5": "ALGO_003"}[no])
    for no, a in acik_say.items():
        if a / max(1, toplam[no]) > 0.3:
            bul("UYARI", "GEN_002", f"/bolumler/{no}", f"Hücrelerin %{round(100 * a / toplam[no])}'i karar/bilgi bekliyor", no, acik=True)
            kal(no, "GEN_002")

    def satir(no):
        ic = icerik.get(no) or {}
        return [s for s in (ic.get("satirlar") or []) if isinstance(s, list) and len(s) == len(BOLUM[no]["sutunlar"])]

    # --- bölüme özgü motor kuralları
    if "2.5" in sayilan:
        tur25 = {s[1] for s in satir("2.5")}
        if not tur25:
            kal("2.5", "SCOPE_000")
        if "Kapsam dışı" not in tur25:
            kal("2.5", "SCOPE_001"); bul("UYARI", "SCOPE_001", "/bolumler/2.5/satirlar", "Kapsam dışı (OOS) satırı yok", "2.5")
        eksik_kural("2.5", "SCOPE_001", "UYARI", "/bolumler/2.5/alanlar/kapsam_siniri", [(icerik["2.5"].get("alanlar") or {}).get("kapsam_siniri")],
                    "Kapsam sınırı yazılı değil")
        if len(tur25 & {"Bağımlılık", "Varsayım", "Kapsam dışı"}) < 3:
            kal("2.5", "SCOPE_002"); bul("BİLGİ", "SCOPE_002", "/bolumler/2.5/satirlar", "Bağımlılık, Varsayım ve Kapsam dışı üçü de bulunmalı", "2.5")
    if "2.1" in sayilan:
        sorunlu = [s for s in satir("2.1") if s[4] == "Evet"]
        if not any(hal(s[5]) == "dolu" and re.search(r"\d", s[5]) for s in sorunlu):
            kal("2.1", "PROC_002")
            bul("UYARI", "PROC_002", "/bolumler/2.1/satirlar", "Sorunlu adım ('Evet') ve sayısal etkisi gerekli", "2.1",
                acik=bool(sorunlu) and all(hal(s[5]) == "isaret" for s in sorunlu))
    if "3.4" in sayilan:
        for i, s in enumerate(satir("3.4")):
            eksik_kural("3.4", "MAP_001", "UYARI", f"/bolumler/3.4/satirlar/{i}", [s[j] for j in (1, 2, 3, 4, 5, 8)], "Kaynak, hedef, tip ve örnek değer somut olmalı")
    if "3.5" in sayilan:
        ss = satir("3.5")
        nesneli = [bool(sum(map(len, nesneler(s[4], True)))) for s in ss]
        for i, (s, var) in enumerate(zip(ss, nesneli)):
            if not var and s[4].strip() != YOK:
                kal("3.5", "ALGO_001")
                if isaretli(s[4]):
                    bul("UYARI", "ALGO_001", f"/bolumler/3.5/satirlar/{i}/4", "SAP nesnesi karar/bilgi bekliyor; ad girdiyle gelmeli, uydurmayın", "3.5", acik=True)
                else:
                    bul("HATA", "ALGO_001", f"/bolumler/3.5/satirlar/{i}/4", f"Somut SAP nesnesi adı yok (adım nesne gerektirmiyorsa {YOK}, bilinmiyorsa işaret)", "3.5")
        if ss and sum(nesneli) * 2 < len(ss):
            kal("3.5", "ALGO_001")
            bul("UYARI", "ALGO_001", "/bolumler/3.5/satirlar", "Adımların yarısından azı somut SAP nesnesi içeriyor", "3.5", acik=any(isaretli(s[4]) for s in ss))
        if len(ss) < 3:
            kal("3.5", "ALGO_002")
    if "5.1" in sayilan:
        ss = satir("5.1")
        if any(s[3] not in ("E", "W", "I", "S", "A") for s in ss):
            kal("5.1", "ERR_001")
        if len(ss) < 2:
            kal("5.1", "ERR_002")
        if not ss:
            kal("5.1", "ERR_003")
    if "6.1" in sayilan:
        ss = satir("6.1")
        somut = [hal(s[3]) == "dolu" and bool(re.search(r"\d{3,}", s[3])) for s in ss]
        if not ss or sum(somut) * 2 < len(ss):
            kal("6.1", "TEST_001")
            bul("UYARI", "TEST_001", "/bolumler/6.1/satirlar", "Test verisi gerçek biçimli değer içermeli (belge no, ana veri)", "6.1",
                acik=bool(ss) and all(hal(s[3]) == "isaret" for s, ok in zip(ss, somut) if not ok))
        if not any(s[1] in ("Negatif", "Sınır") for s in ss):
            kal("6.1", "TEST_002"); bul("UYARI", "TEST_002", "/bolumler/6.1/satirlar", "En az bir Negatif ya da Sınır senaryosu gerekli", "6.1")
    for no, idx in (("5.2", (1, 2, 3, 4)), ("5.3", (1, 2))):
        if no in sayilan:
            for i, s in enumerate(satir(no)):
                eksik_kural(no, "AUTH_001", "UYARI", f"/bolumler/{no}/satirlar/{i}", [s[j] for j in idx], "Yetki satırı somut ad ve değer içermeli")
    if "7.3" in sayilan:
        aciklar = [s for s in satir("7.3") if s[5] == "Açık"]
        sahipsiz = [s[0] for s in aciklar if hal(s[3]) != "dolu"]
        tarihsiz = [s[0] for s in aciklar if hal(s[3]) == "dolu" and hal(s[4]) != "dolu"]
        if sahipsiz:
            kal("7.3", "OPEN_001")
            bul("UYARI", "OPEN_001", "/bolumler/7.3/satirlar", "Sahibi olmayan açık noktalar: " + ", ".join(sahipsiz)
                + ". Ad bilinmiyorsa rol yazın (SAP danışmanı, ABAP geliştirici, karşı sistem ekibi).", "7.3")
        if tarihsiz:
            kal("7.3", "OPEN_001")
            bul("BİLGİ", "OPEN_001", "/bolumler/7.3/satirlar", f"Hedef tarihi verilmemiş açık nokta: {len(tarihsiz)}. Tarih girdiden gelir; uydurulmaz, {YOK} kalır.",
                "7.3", acik=True)
        gecerli_no = {b["no"] for b in T["bolumler"] if bolum_durumu(b, turler, profil) != "tur_disi"}
        for i, s in enumerate(satir("7.3")):
            nolar = re.findall(r"(?<![\d.])\d\.\d{1,2}(?![\d])", s[2])
            yanlis = [n for n in nolar if n not in gecerli_no]
            if s[5] == "Açık" and (not nolar or yanlis):
                bul("UYARI", "OPEN_002", f"/bolumler/7.3/satirlar/{i}/2", "'Etkilediği bölüm' bu belgede yazılan bölüm numaralarını içermeli (örn. 3.4, 3.5)"
                    + (": geçersiz " + ", ".join(yanlis) if yanlis else ""), "7.3")
        karar_refs = {m for _, _, h in hucreler(belge) if ISARET["karar"] in h for m in re.findall(r"OPEN-\d{2,3}", h)}
        kategorisiz = [s[0] for s in satir("7.3") if s[0] in karar_refs and s[5] == "Açık" and s[7] == YOK]
        if kategorisiz:
            bul("UYARI", "KARAR_002", "/bolumler/7.3/satirlar", "KARAR BEKLİYOR ile anılan açık noktanın kategorisi 'Karar bekleyen konu' ya da uygun kalem olmalı: "
                + ", ".join(kategorisiz), "7.3")

    # --- nesne kataloğu (4.1) ve uydurma denetimi
    nesne_sutun = T["nesne_sutunlari"]
    temiz = lambda ad: ad.replace(ISARET["dogrula"], "").strip()
    katalog, dogrulanacak = {}, set()
    for i, s in enumerate(satir("4.1")):
        if hal(s[1]) == "dolu":
            katalog[temiz(s[1])] = (i, s)
            if ISARET["dogrula"] in s[1]:
                dogrulanacak.add(temiz(s[1]))
    kullanilan_ozel, kullanilan_std, kullanilan_app, ilk_yer, disaridaki_metin = set(), set(), set(), {}, []
    for no, yol, m in hucreler(belge):
        sutun = int(yol.rsplit("/", 1)[1]) if "/satirlar/" in yol else -1
        o, sd, ap = nesneler(m, sutun in nesne_sutun.get(no, []))
        if ISARET["dogrula"] in m:
            dogrulanacak.update(sd | ap)
        if no == "4.1":
            continue
        disaridaki_metin.append(m)
        for x in o | sd | ap:
            ilk_yer.setdefault(x, yol)
        kullanilan_ozel |= o; kullanilan_std |= sd; kullanilan_app |= ap
    if "4.1" in sayilan:
        eksik = sorted((kullanilan_ozel | kullanilan_std) - set(katalog))
        if eksik:
            kal("4.1", "SAP_001"); bul("UYARI", "SAP_001", "/bolumler/4.1/satirlar", "Katalogda olmayan nesneler: " + ", ".join(eksik), "4.1")
        hepsi = "\n".join(disaridaki_metin)
        kullanilmayan = [ad for ad in katalog if ad and ad not in hepsi]
        if kullanilmayan:
            kal("4.1", "SAP_002"); bul("BİLGİ", "SAP_002", "/bolumler/4.1/satirlar", "Belgede kullanılmayan katalog nesneleri: " + ", ".join(kullanilmayan), "4.1")
        ad_kurali = proje.get("adlandirma") or {}
        tipler = {kucuk(t): t for t in T["sap_tipleri"]}
        for i, s in enumerate(satir("4.1")):
            eksik_kural("4.1", "OBJ_001", "BİLGİ", f"/bolumler/4.1/satirlar/{i}/1", [s[1]], "Nesne adı yok")
            tip = kucuk(re.split(r"\s*[(/]", s[2].strip())[0].strip())
            if hal(s[2]) != "dolu":
                eksik_kural("4.1", "SAP_003", "UYARI", f"/bolumler/4.1/satirlar/{i}/2", [s[2]], "SAP tipi yok")
            elif tip not in tipler:
                kal("4.1", "SAP_003"); bul("UYARI", "SAP_003", f"/bolumler/4.1/satirlar/{i}/2", f"Bilinmeyen SAP tipi '{s[2]}' (liste: references/sap-sozluk.md)", "4.1")
            if s[3] == "Z" and hal(s[1]) == "dolu":
                ad = temiz(s[1])
                onekler = tuple(ad_kurali.get("on_ekler") or ("Z", "Y", "/"))
                azami = (ad_kurali.get("azami_uzunluk") or {}).get(tipler.get(tip, ""))
                if not ad.startswith(onekler) or (azami and len(ad) > azami):
                    kal("4.1", "SAP_004"); bul("UYARI", "SAP_004", f"/bolumler/4.1/satirlar/{i}/1",
                                               "Adlandırma kuralı: ön ek " + ", ".join(onekler) + (f"; en çok {azami} karakter" if azami else ""), "4.1")
    dogrulanmis = {(k["ad"] if isinstance(k, dict) else k) for k in proje.get("katalog") or []}
    dogrulanmis |= set().union(*nesneler(girdi_metni, True))
    supheli = sorted((kullanilan_std | kullanilan_app | {k for k in katalog if nesneler(k, True)[1]}) - dogrulanmis - dogrulanacak)
    if supheli:
        bul("HATA", "UYD_001", ilk_yer.get(supheli[0], "/bolumler/4.1/satirlar"),
            "Girdide ve proje kataloğunda olmayan SAP nesneleri: " + ", ".join(supheli)
            + f". Kullanıcıyla doğrulayın, ya da 4.1'de adın sonuna '{ISARET['dogrula']}' ekleyip 7.3'te tek bir açık nokta açın."
            + " SAP nesnesi değilse üst düzey 'nesne_degil' dizisine ekleyin.")
    if dogrulanacak:
        metin73 = " ".join(" ".join(s) for s in satir("7.3"))
        if not ("DOĞRULANACAK" in metin73 or "doğrula" in kucuk(metin73) or any(d in metin73 for d in dogrulanacak)):
            bul("UYARI", "UYD_002", "/bolumler/7.3/satirlar", "Doğrulanacak nesneler için 7.3'te tek bir açık nokta açın ('DOĞRULANACAK nesneler: …'): "
                + ", ".join(sorted(dogrulanacak)))

    # --- kimlik zinciri
    tablo, yinelenen = kimlik_tablosu(belge)
    for k, no, i in yinelenen:
        bul("HATA", "YAPI_006", f"/bolumler/{no}/satirlar/{i}/0", f"Yinelenen kimlik {k}", no)
    tanimsiz = {}
    for no, yol, m in hucreler(belge):
        for mm in KIMLIK_RE.finditer(m):
            if mm.group(0) not in tablo:
                tanimsiz.setdefault(mm.group(0), []).append(yol)
    for k, yollar in sorted(tanimsiz.items()):
        bul("HATA", "ZINCIR_001", yollar[0], f"Tanımsız kimlik {k}" + (f" ({len(yollar)} yerde)" if len(yollar) > 1 else ""))
    for s in turet_62(belge):
        if s[7] != "Tam":
            bul("UYARI", "ZINCIR_002", "/bolumler/2.2/satirlar", f"{s[0]} zinciri {s[7].lower()}: SC [{s[1]}] · STEP [{s[2]}] · TC [{s[6]}]", "2.2")
    g = komsuluk(belge)
    testsiz = sorted(s[0] for s in satir("5.1") if s[3] in ("E", "A") and not any(k.startswith("TC-") for k in g.get(s[0], ())))
    if testsiz and "6.1" in sayilan:
        bul("BİLGİ", "ZINCIR_003", "/bolumler/6.1/satirlar", "Test senaryosu olmayan hata mesajları: " + ", ".join(testsiz), "6.1")

    return bulgular, kural_sonuc, sayilan


def gosterge(belge, kural_sonuc, sayilan):
    """Yalnız mekanik kurallardan hesaplanan puan göstergesi (kalite/LLM kısmı içermez)."""
    agirlik = {k["id"]: k["agirlik"] * (PAR["info_factor"] if k["siddet"] == "info" else 1) for k in T["kurallar"]}
    siddet = {k["id"]: k["siddet"] for k in T["kurallar"]}
    puan = {}
    for no, sonuc in kural_sonuc.items():
        if no not in sayilan:
            continue
        top = sum(agirlik[k] for k in sonuc)
        kalan = sum(agirlik[k] for k, ok in sonuc.items() if not ok)
        p = 100 * (1 - kalan / top) if top else 100
        if any(not ok and siddet[k] == "error" for k, ok in sonuc.items()):
            p = min(p, PAR["error_cap"])
        puan[no] = p
    if not puan:
        return {"ortalama": 0, "sonuc": 0, "bant": "Revizyon", "bolum": {}, "cezalar": {}}
    w = {no: BOLUM[no]["agirlik"] for no in puan}
    ort = sum(w[n] * puan[n] for n in puan) / sum(w.values())
    kritik = [n for n in puan if BOLUM[n]["sinif"] == "Kritik" and puan[n] < PAR["crit_thr"]]
    taban = sorted((puan[n], n) for n in puan if sayilan[n] == "taban")[:2]
    zayif = 0
    for p, n in taban:
        fark = ort - p
        zayif += PAR["weak_pen2"] if fark >= PAR["weak_gap2"] else PAR["weak_pen1"] if fark >= PAR["weak_gap1"] else 0
    zayif = min(PAR["weak_cap"], zayif)
    sayac = {}
    for s in (belge.get("bolumler", {}).get("7.3", {}) or {}).get("satirlar") or []:
        if isinstance(s, list) and len(s) == 8 and s[5] == "Açık" and s[7] in T["hazirlik_kalemleri"]:
            sayac[s[7]] = sayac.get(s[7], 0) + 1
    hazirlik = min(PAR["ready_cap"], sum(min(PAR["ready_item_cap"], n * PAR["ready_per"]) for n in sayac.values()))
    sonuc = round(max(0, min(100, ort - PAR["crit_pen"] * len(kritik) - zayif - hazirlik)), 1)
    bant = "Geliştirmeye hazır" if sonuc >= PAR["band_hi"] else "Koşullu" if sonuc >= PAR["band_mid"] else "Revizyon"
    return {"ortalama": round(ort, 1), "sonuc": sonuc, "bant": bant, "bolum": {n: round(p, 1) for n, p in puan.items()},
            "cezalar": {"kritik": PAR["crit_pen"] * len(kritik), "kritik_bolumler": kritik, "zayif": zayif, "hazirlik": hazirlik},
            "en_dusuk": [n for _, n in taban]}


SEV_SIRA = {"HATA": 0, "UYARI": 1, "BİLGİ": 2}


def tam_denetim(belge, proje_yolu=None, girdi_yollari=None):
    proje = yukle(proje_yolu) if proje_yolu else {}
    metin = ""
    for y in girdi_yollari or []:
        with open(y, encoding="utf-8", errors="ignore") as f:
            metin += f.read() + "\n"
    bulgular, ks, sayilan = denetle(belge, proje, metin)
    bulgular.sort(key=lambda b: (SEV_SIRA[b["sev"]], -(BOLUM[b["bolum"]]["agirlik"] if b["bolum"] in BOLUM else 99)))
    return bulgular, gosterge(belge, ks, sayilan), sayilan


# ----------------------------------------------------------------------------- görünüm modeli (döküm betikleri kullanır)
def gorunum(belge):
    turler, profil = belge.get("turler") or [], belge.get("profil") or "standart"
    icerik = belge.get("bolumler") or {}
    gruplar = []
    for g in T["gruplar"]:
        bolumler = []
        for b in (x for x in T["bolumler"] if x["grup"] == g["no"]):
            no, ic = b["no"], icerik.get(b["no"]) or {}
            durum = bolum_durumu(b, turler, profil)
            v = {"no": no, "baslik": b["baslik"], "kisa": b["kisa"], "agirlik": b["agirlik"], "sinif": b["sinif"], "durum": durum,
                 "gerekce": "", "alanlar": [], "sutunlar": [c["ad"] for c in b["sutunlar"]], "satirlar": [], "mermaid": ic.get("mermaid") or ""}
            if durum == "tur_disi":
                v["gerekce"] = f"Geliştirme türü kapsamı dışında ({tur_metni(b)})."
            elif durum == "profil_disi" and not ic:
                continue
            elif ic.get("gecerli") is False:
                v["durum"], v["gerekce"] = "elle", ic.get("gerekce") or ""
            else:
                v["durum"] = "gecerli"
                v["alanlar"] = [(a["etiket"], (ic.get("alanlar") or {}).get(a["anahtar"], "")) for a in b["alanlar"]]
                if no == "1.1":
                    v["sutunlar"] = ["Kod", "Tür", "Seçim", "Açıklama"]
                    v["satirlar"] = [[t["kod"], t["ad"], "Evet" if t["kod"] in turler else "Hayır", t["aciklama"]] for t in T["tur_tanimlari"]]
                elif no == "6.2":
                    v["satirlar"] = turet_62(belge)
                    if not v["satirlar"]:
                        continue
                elif no == "5.4":
                    v["sutunlar"], v["satirlar"] = birlestir_54(belge)
                else:
                    v["satirlar"] = [s for s in ic.get("satirlar") or [] if isinstance(s, list)]
            bolumler.append(v)
        gruplar.append({"no": g["no"], "ad": g["ad"], "bolumler": bolumler})
    return gruplar


def dosya_adi(belge):
    a = (belge.get("bolumler", {}).get("1.1", {}).get("alanlar") or {})
    kimlik = re.sub(r"[^A-Za-z0-9_-]+", "-", a.get("gel_id") or "").strip("-") or "FS-TS"
    surum = re.sub(r"[^0-9A-Za-z.]+", "", (belge.get("meta") or {}).get("surum") or "0.1")
    return f"{kimlik}_FS-TS_v{surum}"


def bos_yol(yol):
    if not os.path.exists(yol):
        return yol
    kok, uz = os.path.splitext(yol)
    i = 2
    while os.path.exists(f"{kok}-{i}{uz}"):
        i += 1
    return f"{kok}-{i}{uz}"


# ----------------------------------------------------------------------------- komutlar
def bilgi_metni(b, ornek=False):
    ek = f" · en az {b['en_az_satir']} satır" if b["en_az_satir"] > 1 else ""
    out = [f"## {b['no']} {b['baslik']}  [ağırlık {b['agirlik']} · {b['sinif']} · {tur_metni(b)}{ek}]"]
    if b.get("not"):
        out.append("Not: " + b["not"])
    out += ["Amaç: " + b["amac"], "Kural: " + b["kural"]]
    if b["alanlar"]:
        out.append("Alanlar: " + " ; ".join(f"{x['anahtar']} = {x['etiket']}" + (f" — {x['ipucu']}" if x["ipucu"] else "")
                                            + (f" [{' | '.join(x['secenekler'])}]" if x.get("secenekler") else "")
                                            + (" (KARAR)" if x.get("karar") else "") for x in b["alanlar"]))
    if b["sutunlar"] and not b.get("turetilmis"):
        out.append("Sütunlar: " + " ; ".join(f"{i} {c['ad']}" + (f" {{{'/'.join(c['kimlik'])}-nn}}" if c.get("kimlik") else "")
                                             + (f" [{' | '.join(c['secenekler'])}]" if c.get("secenekler") else "")
                                             + (f" — {c['ipucu']}" if c["ipucu"] else "") + (" (KARAR)" if c.get("karar") else "")
                                             for i, c in enumerate(b["sutunlar"])))
    out.append("İyi: " + b["iyi"])
    if b["sinif"] == "Kritik":
        out.append("Kötü: " + b["kotu"])
    if ornek and b.get("ornek_satir"):
        out.append("Örnek satır: " + json.dumps(b["ornek_satir"], ensure_ascii=False))
    out.append("Denetim: " + ", ".join(b["kurallar"] + b["eski_kurallar"]))
    return "\n".join(out)


def k_bilgi(a):
    turler = [t for t in (a.tur or "").split(",") if t]
    for b in T["bolumler"]:
        if a.bolum and b["no"] not in a.bolum.split(","):
            continue
        if a.grup and b["grup"] not in a.grup.split(","):
            continue
        if bolum_durumu(b, turler, a.profil) != "gecerli" and not a.bolum:
            continue
        print(bilgi_metni(b, a.ornek) + "\n")


def k_iskelet(a):
    turler = [t for t in a.tur.split(",") if t]
    gecersiz = [t for t in turler if t not in TUR_AD]
    if gecersiz or not turler:
        sys.exit("Geçersiz tür. Seçenekler: " + ", ".join(f"{k}={v}" for k, v in TUR_AD.items()))
    bolumler = {}
    for no in T["yazim_sirasi"]:
        b = BOLUM[no]
        if bolum_durumu(b, turler, a.profil) != "gecerli":
            continue
        ic = {}
        if b["alanlar"]:
            ic["alanlar"] = {x["anahtar"]: "" for x in b["alanlar"]}
        if b["sutunlar"]:
            ic["satirlar"] = []
        bolumler[no] = ic
    if a.id:
        bolumler["1.1"]["alanlar"]["gel_id"] = a.id
    belge = {"sema": T["sema"], "meta": {"surum": "0.1", "tarih": datetime.date.today().isoformat(), "hazirlayan": YOK, "durum": "Taslak", "musteri": YOK},
             "turler": turler, "profil": a.profil, "bolumler": bolumler,
             "surum_gecmisi": [["0.1", datetime.date.today().isoformat(), YOK, "İlk taslak"]], "onaylar": []}
    kaydet(belge, a.cikti)
    print(f"İskelet yazıldı: {a.cikti} · {len(bolumler)} bölüm · türler {','.join(turler)} · profil {a.profil}")
    print("Yazım sırası:", " → ".join(bolumler), "(6.2 türetilir; grup sırası " + ", ".join(T["grup_sirasi"]) + ")")


def k_eksik(a):
    belge = yukle(a.dosya)
    turler, profil, icerik = belge.get("turler") or [], belge.get("profil") or "standart", belge.get("bolumler") or {}
    satirlar = []
    for b in sorted(T["bolumler"], key=lambda x: -x["agirlik"]):
        if b.get("turetilmis") or bolum_durumu(b, turler, profil) != "gecerli":
            continue
        ic = icerik.get(b["no"])
        if isinstance(ic, dict) and ic.get("gecerli") is False:
            continue
        ic = ic or {}
        bos = [x["etiket"] for x in b["alanlar"] if not str((ic.get("alanlar") or {}).get(x["anahtar"]) or "").strip()]
        bekleyen = sum(1 for no, _, m in hucreler({"bolumler": {b["no"]: ic}}) if isaretli(m))
        n = len(ic.get("satirlar") or [])
        if bos or bekleyen or (b["sutunlar"] and n < b["en_az_satir"]):
            satirlar.append(f"{b['no']} {b['baslik']} [ağırlık {b['agirlik']}{', KRİTİK' if b['sinif'] == 'Kritik' else ''}]: "
                            + "; ".join(x for x in [f"boş alanlar: {', '.join(bos)}" if bos else "",
                                                     f"satır {n}/{b['en_az_satir']}" if b["sutunlar"] and n < b["en_az_satir"] else "",
                                                     f"{bekleyen} hücre karar/bilgi bekliyor" if bekleyen else ""] if x))
    print("\n".join(satirlar) if satirlar else "Eksik yok.")


def acik_ozeti(bulgular):
    """Karar/bilgi bekleyen hücrelerden doğan bulguların tek satırlık özeti."""
    grup = {}
    for b in bulgular:
        if b.get("acik"):
            grup.setdefault(b["kural"], []).append(b["bolum"] or "?")
    return " · ".join(f"{k} ({', '.join(sorted(set(v), key=lambda n: [int(x) for x in n.split('.')] if n[0].isdigit() else [99]))})" for k, v in grup.items())


def yazdir_denetim(bulgular, g, azami):
    kusur = [b for b in bulgular if not b.get("acik")]
    say = {s: sum(1 for b in kusur if b["sev"] == s) for s in SEV_SIRA}
    print(f"DENETİM  kusur: hata {say['HATA']} · uyarı {say['UYARI']} · bilgi {say['BİLGİ']}  |  girdi bekleyen: {len(bulgular) - len(kusur)}  |  "
          f"mekanik gösterge {str(g['sonuc']).replace('.', ',')} ({g['bant']}) — yalnız kural kısmı; kalite puanını gerçek motor ölçer")
    for b in kusur[:azami]:
        print(f"{b['sev']:5} {b['kural']:10} {b['yol']}  {b['mesaj']}")
    if len(kusur) > azami:
        print(f"… {len(kusur) - azami} kusur daha (--azami ile artırın)")
    if len(kusur) < len(bulgular):
        print("GİRDİ BEKLEYEN (düzeltilecek kusur değil; karar ya da bilgi gelince kapanır, içerik uydurmayın): " + acik_ozeti(bulgular))


def k_denetle(a):
    belge = yukle(a.dosya)
    bulgular, g, _ = tam_denetim(belge, a.proje, a.girdi)
    if a.json:
        print(json.dumps({"bulgular": bulgular, "gosterge": g}, ensure_ascii=False, indent=1))
    else:
        yazdir_denetim(bulgular, g, a.azami)
    sys.exit(1 if any(b["sev"] == "HATA" and not b.get("acik") for b in bulgular) else 0)


def yol_coz(belge, yol):
    parcalar = [p for p in yol.split("/") if p != ""]
    hedef = belge
    for p in parcalar[:-1]:
        hedef = hedef[int(p)] if isinstance(hedef, list) else hedef.setdefault(p, {})
    son = parcalar[-1]
    return hedef, (int(son) if isinstance(hedef, list) and son != "-" else son)


def k_yama(a):
    belge = yukle(a.dosya)
    ham = a.op or (open(a.yama_dosyasi, encoding="utf-8").read() if a.yama_dosyasi else sys.stdin.read())
    islemler = json.loads(ham)
    for op in islemler if isinstance(islemler, list) else [islemler]:
        hedef, son = yol_coz(belge, op["yol"])
        tur = op.get("islem", "ayarla")
        if tur == "ayarla":
            hedef[son] = op["deger"]
        elif tur == "ekle":
            (hedef if son == "-" else hedef.setdefault(son, []) if isinstance(hedef, dict) else hedef[son]).append(op["deger"])
        elif tur == "sil":
            del hedef[son]
        else:
            sys.exit(f"Bilinmeyen işlem: {tur} (ayarla | ekle | sil)")
    kaydet(belge, a.dosya)
    print(f"{len(islemler) if isinstance(islemler, list) else 1} işlem uygulandı: {a.dosya}")


def ozet_satirlari(belge, bulgular, g, sayilan):
    a = (belge.get("bolumler", {}).get("1.1", {}).get("alanlar") or {})
    turler, profil = belge.get("turler") or [], belge.get("profil") or "standart"
    durumlar = [bolum_durumu(b, turler, profil) for b in T["bolumler"]]
    elle = [no for no, ic in (belge.get("bolumler") or {}).items() if isinstance(ic, dict) and ic.get("gecerli") is False]
    acik = [s for s in (belge.get("bolumler", {}).get("7.3", {}) or {}).get("satirlar") or [] if isinstance(s, list) and len(s) == 8 and s[5] == "Açık"]
    bekleyen = sum(1 for _, _, m in hucreler(belge) if isaretli(m))
    dogrula = sorted({x for _, _, m in hucreler(belge) if ISARET["dogrula"] in m for x in (nesneler(m, True)[1] | nesneler(m, True)[2])})
    kusur = [b for b in bulgular if not b.get("acik")]
    say = {s: sum(1 for b in kusur if b["sev"] == s) for s in SEV_SIRA}
    c = g["cezalar"]
    yazilan = [n for n in sayilan if not BOLUM[n].get("turetilmis")]
    kimlik = a.get("gel_id") or "—"
    out = [f"{'kimlik bekleniyor' if isaretli(kimlik) else kimlik} · {a.get('baslik') or '—'} · türler {', '.join(TUR_AD.get(t, t) for t in turler)} · profil {profil}",
           f"Bölümler: {len(yazilan)} yazıldı{' + 6.2 türetildi' if '6.2' in sayilan else ''} · {durumlar.count('tur_disi')} tür dışı · {durumlar.count('profil_disi')} profil dışı"
           + (f" · elle geçersiz: {', '.join(elle)}" if elle else ""),
           f"Açık noktalar: {len(acik)} · karar/bilgi bekleyen hücre: {bekleyen} · doğrulanacak SAP nesnesi: {len(dogrula)}"
           + (f" ({', '.join(dogrula[:6])}{'…' if len(dogrula) > 6 else ''})" if dogrula else "")]
    def agirlik(s):
        w = [BOLUM[n]["agirlik"] for n in re.findall(r"(?<![\d.])\d\.\d{1,2}(?![\d])", s[2]) if n in BOLUM]
        return (-max(w), -sum(w)) if w else (0, 0)
    acik = sorted(acik, key=agirlik)  # en ağır bölümü tıkayan önce; eşitlikte kimlik sırası korunur
    out += [f"  {s[0]} [{s[2]}] {s[1][:110]}{'…' if len(s[1]) > 110 else ''} — {s[3]}, {s[4]}" for s in acik[:5]]
    if len(acik) > 5:
        out.append(f"  … +{len(acik) - 5} açık nokta daha (7.3)")
    out.append(f"Denetim: kusur hata {say['HATA']} · uyarı {say['UYARI']} · bilgi {say['BİLGİ']}"
               + (f" · girdi bekleyen: {acik_ozeti(bulgular)}" if len(kusur) < len(bulgular) else ""))
    out.append(f"Mekanik gösterge: {str(g['sonuc']).replace('.', ',')} ({g['bant']}) = ortalama {str(g['ortalama']).replace('.', ',')}"
               f" − kritik {c.get('kritik', 0)} − zayıf bölüm {c.get('zayif', 0)} − hazırlık {c.get('hazirlik', 0)}."
               " Yalnız mekanik kurallar; kalite (LLM) puanını gerçek motor ölçer.")
    if [n for n in g.get("en_dusuk", []) if g["bolum"][n] < 100]:
        out.append("En düşük iki bölüm: " + ", ".join(f"{n} ({str(g['bolum'][n]).replace('.', ',')})" for n in g["en_dusuk"]))
    return out


def k_ozet(a):
    belge = yukle(a.dosya)
    bulgular, g, sayilan = tam_denetim(belge, a.proje, a.girdi)
    print("\n".join(ozet_satirlari(belge, bulgular, g, sayilan)))


def k_dok(a):
    belge = yukle(a.dosya)
    bulgular, g, sayilan = tam_denetim(belge, a.proje, a.girdi)
    yapisal = [b for b in bulgular if b["sev"] == "HATA" and not b.get("acik") and b["kural"].startswith(("YAPI", "META"))]
    if yapisal:
        yazdir_denetim(yapisal, g, 20)
        sys.exit("Yapısal hata varken döküm yapılmaz; önce düzeltin.")
    os.makedirs(a.cikti, exist_ok=True)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    ctx = {"T": T, "gorunum": gorunum(belge), "bulgular": bulgular, "gosterge": g, "ozet": ozet_satirlari(belge, bulgular, g, sayilan),
           "logo": next((p for p in [getattr(a, "logo", None), os.path.join(KOK, "assets", "logo.png")] if p and os.path.exists(p)), None), "tur_ad": TUR_AD}
    for bicim in a.bicim.split(","):
        bicim = bicim.strip().lower()
        if bicim == "docx":
            import dok_docx as m
            hedef = bos_yol(os.path.join(a.cikti, dosya_adi(belge) + ".docx"))
        elif bicim == "xlsx":
            import dok_xlsx as m
            hedef = bos_yol(os.path.join(a.cikti, dosya_adi(belge) + ".xlsx"))
        elif bicim in ("md", "vault"):
            import dok_md as m
            hedef = bos_yol(os.path.join(a.cikti, dosya_adi(belge) + (".md" if bicim == "md" else "_vault")))
        else:
            sys.exit(f"Bilinmeyen biçim '{bicim}'. Seçenekler: docx, xlsx, md, vault")
        try:
            m.uret(belge, ctx, hedef, bicim)
        except ImportError as e:
            sys.exit(f"{bicim} için gerekli kütüphane yok ({e.name}). Kurun: pip install " + {"docx": "python-docx", "xlsx": "openpyxl"}.get(bicim, e.name))
        print("Üretildi:", hedef)


def main():
    try:
        import signal
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # çıktı `head` gibi bir araca bağlandığında sessizce bit
    except (ImportError, AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="Belirtim Yazmanı · FS-TS içerik aracı")
    alt = p.add_subparsers(dest="komut", required=True)
    q = alt.add_parser("bilgi", help="Geçerli bölümlerin yazım bilgisi (türe ve profile göre süzülmüş)")
    q.add_argument("--tur", default=""); q.add_argument("--profil", default="standart"); q.add_argument("--grup"); q.add_argument("--bolum")
    q.add_argument("--ornek", action="store_true"); q.set_defaults(f=k_bilgi)
    q = alt.add_parser("iskelet", help="Boş içerik JSON'u üret")
    q.add_argument("--tur", required=True, help="Virgüllü tür kodları: " + ", ".join(f"{k}={v}" for k, v in TUR_AD.items()))
    q.add_argument("--profil", default="standart", choices=list(T["profiller"])); q.add_argument("--id"); q.add_argument("--cikti", required=True)
    q.set_defaults(f=k_iskelet)
    for ad, f, yardim in (("eksik", k_eksik, "Boş alanları ve bekleyen hücreleri ağırlık sırasıyla listele"),
                          ("denetle", k_denetle, "Mekanik denetim ve gösterge"), ("ozet", k_ozet, "Teslim raporu satırları"),
                          ("dok", k_dok, "JSON'u belgeye dök")):
        q = alt.add_parser(ad, help=yardim)
        q.add_argument("dosya")
        if ad != "eksik":
            q.add_argument("--proje", help="Proje profili JSON'u (adlandırma, doğrulanmış katalog)")
            q.add_argument("--girdi", nargs="*", help="Girdi metin dosyaları; içlerindeki SAP adları doğrulanmış sayılır")
        if ad == "denetle":
            q.add_argument("--json", action="store_true"); q.add_argument("--azami", type=int, default=40)
        if ad == "dok":
            q.add_argument("--bicim", required=True, help="docx, xlsx, md, vault (virgülle birden çok)"); q.add_argument("--cikti", default=".")
            q.add_argument("--logo", help="Kapak ve üst bilgi logosu (PNG); verilmezse assets/logo.png varsa o kullanılır")
        q.set_defaults(f=f)
    q = alt.add_parser("yama", help="JSON'a hedefli değişiklik uygula")
    q.add_argument("dosya")
    q.add_argument("--op", help='JSON işlem listesi. ayarla: {"islem":"ayarla","yol":"/bolumler/3.5/satirlar/0/4","deger":"…"} · '
                                'satır ekle: {"islem":"ekle","yol":"/bolumler/3.5/satirlar","deger":["STEP-04","4",…]} · '
                                'sil: {"islem":"sil","yol":"/bolumler/3.5/satirlar/2"}. Satır ve sütun numaraları 0\'dan başlar.')
    q.add_argument("--yama-dosyasi"); q.set_defaults(f=k_yama)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
