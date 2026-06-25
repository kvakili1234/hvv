#!/usr/bin/env python3
"""Scrape real heartveinvascular.com content pages into structured JSON."""
import json, re, time, os, sys
import requests
from bs4 import BeautifulSoup

BASE = "https://heartveinvascular.com"
HDRS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
OUT = os.path.dirname(__file__)

# slug -> url path  (all real content pages)
PAGES = {
  "home": "/",
  "about": "/about-dr-babak-alex-vakili-cardiologist/",
  "office-location": "/about-dr-babak-alex-vakili-cardiologist/dr-alex-vakili-office-location/",
  "doctor": "/doctor-babak-alex-vakili/",
  "hospital-admissions": "/doctor-babak-alex-vakili/hospital-admissions/",
  "contact": "/contact-us/",
  # category hubs
  "heart-procedures": "/heart-procedures/",
  "vein-procedures": "/vein-procedures/",
  "vascular-procedures": "/vascular-procedures/",
  "endovascular-services": "/endovascular-services/",
  "endovenous-services": "/endovenous-services/",
  "integrative-medicine": "/integrative-medicine/",
  "patient-resources": "/patient-resources/",
  # heart procedures
  "cardiac-catheterization": "/cardiac-catheterization-procedure/",
  "nuclear-cardiac-stress-test": "/nuclear-cardiac-stress-test/",
  "64-slice-ct": "/heart-procedures/64-slice-ct-procedure/",
  "advanced-lipid-inr": "/heart-procedures/advanced-lipid-and-inr-monitoring/",
  "ambulatory-blood-pressure": "/heart-procedures/ambulatory-blood-pressure-abp/",
  "cardiac-event-recording": "/heart-procedures/cardiac-event-recording/",
  "cardiac-pet-scan": "/heart-procedures/cardiac-pet-scan/",
  "echocardiogram": "/heart-procedures/echocardiogram/",
  "holter-monitoring": "/heart-procedures/holter-monitoring/",
  "pacer-defibrillator": "/heart-procedures/pacer-and-defibrillator-integration/",
  "sleep-study": "/heart-procedures/sleep-study/",
  "stress-test": "/heart-procedures/stress-test/",
  # vein / vascular procedures (his site nests vascular under vein-procedures)
  "aaa-screening": "/vein-procedures/abdominal-aortic-aneurysm-screening/",
  "ambulatory-phlebectomy": "/vein-procedures/ambulatory-phlebectomy/",
  "ankle-brachial-index": "/vein-procedures/ankle-brachial-index-test/",
  "arterial-duplex-leg": "/vein-procedures/arterial-duplex-of-the-leg-vein/",
  "carotid-duplex": "/vein-procedures/carotid-duplex-imaging/",
  "conservative-vein-treatments": "/vein-procedures/conservative-vein-treatments/",
  "endovenous-catheter-occlusion": "/vein-procedures/endovenous-catheter-occlusion/",
  "vein-faq": "/vein-procedures/frequently-asked-questions/",
  "heart-disease-overview": "/vein-procedures/heart-disease-overview/",
  "renal-ultrasound": "/vein-procedures/renal-ultrasound/",
  "sclerotherapy": "/vein-procedures/sclerotherapy/",
  "treatment-risks": "/vein-procedures/treatment-risks-and-side-effects/",
  "ultrasound-imaging": "/vein-procedures/ultrasound-imaging/",
  "varicose-veins-leg-swelling": "/vein-procedures/varicose-veins-and-leg-swelling/",
  "vascular-ultrasound": "/vein-procedures/vascular-ultrasound/",
  "vein-disease-overview": "/vein-procedures/vein-disease-overview/",
  "vein-disease": "/vein-procedures/vein-disease/",
  "vein-mapping": "/vein-procedures/vein-mapping/",
  "venaseal": "/vein-procedures/venaseal-closure-system/",
  # integrative
  "iv-vitamins": "/integrative-medicine/iv-vitamins/",
  "metabolic-testing": "/integrative-medicine/metabolic-testing/",
  # patient resources
  "accepted-insurance": "/patient-resources/accepted-insurance/",
  "cancellation-policy": "/patient-resources/cancellation-policy/",
  "patient-education": "/patient-resources/patient-education/",
  "patient-forms": "/patient-resources/patient-forms/",
  "prescription-refills": "/patient-resources/prescription-refills/",
  "shop": "/vitamin-cbd-shop/",
}

def clean(t):
    return re.sub(r"\s+", " ", t or "").strip()

def extract(slug, html):
    soup = BeautifulSoup(html, "html.parser")
    # title / meta
    title = clean(soup.title.string if soup.title else "")
    md = soup.find("meta", attrs={"name": "description"})
    meta_desc = clean(md["content"]) if md and md.get("content") else ""
    og = soup.find("meta", attrs={"property": "og:image"})
    og_image = og["content"] if og and og.get("content") else ""
    # h1
    h1 = ""
    h1el = soup.find(["h1"]) or soup.select_one(".elementor-heading-title")
    if h1el: h1 = clean(h1el.get_text())
    # ordered content blocks from elementor widgets
    blocks = []
    for w in soup.select(".elementor-widget-heading, .elementor-widget-text-editor, .elementor-widget-icon-list, .elementor-widget-image"):
        cls = w.get("class", [])
        if "elementor-widget-heading" in cls:
            txt = clean(w.get_text())
            if txt: blocks.append({"type": "heading", "text": txt})
        elif "elementor-widget-text-editor" in cls:
            # keep paragraph + list structure; convert <br> to spaces so words aren't glued
            for el in w.select("p, li, h2, h3, h4"):
                for br in el.find_all("br"): br.replace_with(" ")
                txt = clean(el.get_text())
                if txt and len(txt) > 1:
                    blocks.append({"type": "li" if el.name == "li" else ("h" if el.name in ("h2","h3","h4") else "p"), "text": txt})
        elif "elementor-widget-icon-list" in cls:
            for li in w.select(".elementor-icon-list-text"):
                txt = clean(li.get_text())
                if txt: blocks.append({"type": "li", "text": txt})
        elif "elementor-widget-image" in cls:
            img = w.find("img")
            if img and img.get("src"):
                blocks.append({"type": "img", "src": img["src"], "alt": clean(img.get("alt",""))})
    # fallback: if no elementor blocks, grab all p/li/h2/h3
    if not blocks:
        for el in soup.select("main p, main li, article p, article li, p, li"):
            txt = clean(el.get_text())
            if txt and len(txt) > 20:
                blocks.append({"type": "li" if el.name=="li" else "p", "text": txt})
    # de-dup consecutive identical
    out = []
    seen = set()
    for b in blocks:
        key = (b.get("type"), b.get("text",""), b.get("src",""))
        if key in seen: continue
        seen.add(key)
        out.append(b)
    return {"slug": slug, "title": title, "meta_desc": meta_desc, "h1": h1,
            "og_image": og_image, "blocks": out}

def main():
    data = {}
    s = requests.Session(); s.headers.update(HDRS)
    for slug, path in PAGES.items():
        url = BASE + path
        try:
            r = s.get(url, timeout=25)
            if r.status_code != 200:
                print(f"  !! {slug} HTTP {r.status_code}"); continue
            data[slug] = extract(slug, r.text)
            nb = len(data[slug]["blocks"])
            print(f"  ok {slug:32s} blocks={nb:3d} h1='{data[slug]['h1'][:40]}'")
        except Exception as e:
            print(f"  !! {slug} ERR {e}")
        time.sleep(0.25)  # polite
    with open(os.path.join(OUT, "content.json"), "w") as f:
        json.dump(data, f, indent=1)
    print(f"\nSaved {len(data)} pages -> content.json")

if __name__ == "__main__":
    main()
