#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static-site generator for Heart Vein & Vascular. Emits home + all sub-pages
from scraped real content (scrape/content.json, scrape/reviews.json)."""
import json, os, re, html as _h

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(ROOT,"scrape/content.json")))
REVIEWS = json.load(open(os.path.join(ROOT,"scrape/reviews.json")))
MANI = json.load(open(os.path.join(ROOT,"scrape/img_manifest.json")))

SITE = "https://kvakili1234.github.io/hvv"
PHONE="407-990-1921"; TOLL="855-537-4411"; EMAIL="support@heartveinvascular.com"
ADDR="2170 W State Road 434, Ste 190, Longwood, FL 32779"
PORTAL="https://health.healow.com/hvv"
LINKEDIN="https://www.linkedin.com/in/babak-alex-vakili-md-facc-fscai-cpi-198b75353/"
# form delivery (no backend; activates after first email is confirmed by office)
FORM_ACTION="https://formsubmit.co/ajax/" + EMAIL

def esc(s): return _h.escape(s or "", quote=True)
def local_img(url):
    if not url: return ""
    key=re.sub(r'-\d+x\d+(?=\.)','',url)
    return MANI.get(key, MANI.get(url, ""))

# ---------------- Information architecture ----------------
# (display title, content-slug, short nav label)
HEART=[("Cardiac Catheterization","cardiac-catheterization"),
 ("Nuclear Cardiac Stress Test","nuclear-cardiac-stress-test"),
 ("Stress Test","stress-test"),
 ("Echocardiogram","echocardiogram"),
 ("Cardiac PET-CT Stress Test","cardiac-pet-scan"),
 ("Cardiac CCTA (64-Slice CT)","64-slice-ct"),
 ("Holter Monitoring","holter-monitoring"),
 ("Cardiac Event Recording","cardiac-event-recording"),
 ("Ambulatory Blood Pressure","ambulatory-blood-pressure"),
 ("Advanced Lipid & INR Monitoring","advanced-lipid-inr"),
 ("Pacer & Defibrillator Integration","pacer-defibrillator"),
 ("Sleep Study","sleep-study"),
 ("Heart Attack Overview","heart-disease-overview")]
VEIN=[("Radiofrequency Catheter Ablation","endovenous-catheter-occlusion"),
 ("VenaSeal Closure System","venaseal"),
 ("Sclerotherapy","sclerotherapy"),
 ("Ambulatory Phlebectomy","ambulatory-phlebectomy"),
 ("Conservative Vein Treatments","conservative-vein-treatments"),
 ("Vein Mapping","vein-mapping"),
 ("Venous Reflux Disease","vein-disease"),
 ("Chronic Venous Insufficiency Ultrasound","ultrasound-imaging"),
 ("Varicose Veins & Leg Swelling","varicose-veins-leg-swelling"),
 ("Vein Disease Overview","vein-disease-overview")]
VASC=[("Carotid Duplex Imaging","carotid-duplex"),
 ("Abdominal Aortic Aneurysm Screening","aaa-screening"),
 ("Arterial Duplex of the Leg","arterial-duplex-leg"),
 ("Ankle-Brachial Index Test","ankle-brachial-index"),
 ("Renal Ultrasound","renal-ultrasound"),
 ("Vascular Ultrasound","vascular-ultrasound")]
INFO=[("Treatment Risks & Side Effects","treatment-risks"),
 ("Frequently Asked Questions","vein-faq")]
INTEG=[("IV Vitamins","iv-vitamins"),("Metabolic Testing","metabolic-testing")]
RESOURCES=[("Patient Portal",PORTAL,"ext"),
 ("Patient Forms","patient-forms","int"),
 ("Patient Education","patient-education","int"),
 ("Prescription Refills","prescription-refills","int"),
 ("Accepted Insurance","accepted-insurance","int"),
 ("Cancellation Policy","cancellation-policy","int")]

CAT={"heart":("Heart","heart.html"),"vein":("Vein & Vascular","vein-vascular.html"),
     "vascular":("Vein & Vascular","vein-vascular.html"),"integrative":("Integrative Medicine","integrative.html")}
PROC_CAT={}
for t,s in HEART: PROC_CAT[s]=("heart",t)
for t,s in VEIN: PROC_CAT[s]=("vein",t)
for t,s in VASC: PROC_CAT[s]=("vascular",t)
for t,s in INFO: PROC_CAT[s]=("vein",t)
for t,s in INTEG: PROC_CAT[s]=("integrative",t)

# ---------------- content cleaning ----------------
FOOTER_HEADS={"Navigation","Contact Details","Quick Links"}
BIO_SKIP_HEADS={"WORKING HOURS","MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY","SUNDAY","CONTACT INFO","OFFICE HOURS:"}
def clean_blocks(slug):
    raw=DATA.get(slug,{}).get("blocks",[]); h1=DATA.get(slug,{}).get("h1","")
    out=[]
    for b in raw:
        t=b.get("text","")
        if b["type"]=="img":
            src=b.get("src","")
            if "logosNew" in src: continue
            if "footer-logo" in src: break
        if b["type"]=="heading":
            if t in FOOTER_HEADS: break
            if t.strip().rstrip(".:").lower()==h1.strip().rstrip(".:").lower(): continue
        if b["type"]=="p" and t.startswith("Copyright"): break
        out.append(b)
    return out

def first_para(slug, fallback=""):
    for b in clean_blocks(slug):
        if b["type"]=="p" and len(b.get("text",""))>30:
            return b["text"]
    return fallback
def teaser(slug, n=115):
    p=first_para(slug)
    p=re.sub(r'\s+',' ',p).strip()
    if len(p)<=n: return p
    cut=p[:n].rsplit(" ",1)[0]
    return cut+"…"
def page_img(slug):
    for b in clean_blocks(slug):
        if b["type"]=="img":
            li=local_img(b.get("src",""))
            if li: return li
    return ""

# ---------------- shared chrome ----------------
def head(title, desc, base, canonical, og_img="img/family.jpg", schema=""):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}"/>
<link rel="canonical" href="{SITE}/{canonical}"/>
<meta property="og:type" content="website"/>
<meta property="og:title" content="{esc(title)}"/>
<meta property="og:description" content="{esc(desc)}"/>
<meta property="og:image" content="{SITE}/{og_img}"/>
<meta property="og:url" content="{SITE}/{canonical}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{esc(title)}"/>
<meta name="twitter:description" content="{esc(desc)}"/>
<meta name="twitter:image" content="{SITE}/{og_img}"/>
<meta name="theme-color" content="#ED2D5D"/>
<link rel="icon" type="image/png" href="{base}logo.png"/>
<link rel="apple-touch-icon" href="{base}logo.png"/>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/site.css"/>
{schema}
</head>
<body>
<div class="demo">DEMO REDESIGN · for review</div>'''

def navlist(items, base, prefix="p/"):
    return "".join(f'<a href="{base}{prefix}{s}.html">{esc(t)}</a>' for t,s in items)

def topbar(base):
    return f'''<div class="topbar"><div class="wrap">
 <div class="l">
  <span style="display:inline-flex;align-items:center;gap:7px"><span class="icsm" style="color:var(--rose)"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></span>Mon–Fri 8:00 AM – 4:30 PM · Sat &amp; Sun Closed</span>
  <span style="display:inline-flex;align-items:center;gap:7px"><span class="icsm" style="color:var(--rose)"><svg viewBox="0 0 24 24"><path d="M12 21s-6-5.7-6-10a6 6 0 1 1 12 0c0 4.3-6 10-6 10z"/><circle cx="12" cy="11" r="2"/></svg></span>{ADDR}</span>
 </div>
 <div class="r">
  <a class="ph" href="tel:+1{PHONE.replace('-','')}" style="display:inline-flex;align-items:center;gap:7px"><span class="icsm"><svg viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.1-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg></span>{PHONE}</a>
  <a href="{PORTAL}" target="_blank" rel="noopener">Patient Portal</a>
  <a class="chip" href="{base}shop.html">Shop</a>
 </div>
</div></div>'''

def nav(base):
    heart_dd=navlist(HEART,base); vein_dd=navlist(VEIN+VASC+INFO,base); int_dd=navlist(INTEG,base)
    res_dd=f'<a href="{PORTAL}" target="_blank" rel="noopener">Patient Portal ↗</a>'+ \
           "".join(f'<a href="{base}r/{s}.html">{esc(t)}</a>' for t,s,k in RESOURCES if k=="int")
    return f'''<nav><div class="nav-in">
 <a href="{base}index.html" class="brand"><img src="{base}logo.png" alt="Heart Vein &amp; Vascular"/></a>
 <div class="nav-links">
  <div><span>Heart</span><div class="dd wide"><div class="dh" style="column-span:all">Heart Services</div>{heart_dd}</div></div>
  <div><span>Vein &amp; Vascular</span><div class="dd wide"><div class="dh" style="column-span:all">Vein, Vascular &amp; Diagnostics</div>{vein_dd}</div></div>
  <div><span>Integrative</span><div class="dd"><div class="dh">Integrative Medicine</div>{int_dd}</div></div>
  <div><span>Patient Resources</span><div class="dd"><div class="dh">For Our Patients</div>{res_dd}</div></div>
  <a class="lnk" href="{base}about.html">Dr. Vakili</a>
  <a class="lnk" href="{base}index.html#reviews">Reviews</a>
  <a class="lnk" href="{base}contact.html">Contact</a>
  <a class="btn" href="{base}book.html" style="margin-left:10px;padding:11px 22px">Book Appointment</a>
 </div>
 <button class="navtoggle" aria-label="Menu" onclick="toggleMobNav()"><span></span><span></span><span></span></button>
</div></nav>
<div class="mobnav-bg" onclick="closeMobNav()"></div>
<div class="mobnav">
 <div class="mn-sec"><div class="mn-head">Heart<span class="ar"></span></div><div class="mn-sub">{heart_dd}</div></div>
 <div class="mn-sec"><div class="mn-head">Vein &amp; Vascular<span class="ar"></span></div><div class="mn-sub">{vein_dd}</div></div>
 <div class="mn-sec"><div class="mn-head">Integrative<span class="ar"></span></div><div class="mn-sub">{int_dd}</div></div>
 <div class="mn-sec"><div class="mn-head">Patient Resources<span class="ar"></span></div><div class="mn-sub">{res_dd}</div></div>
 <a class="mn-link" href="{base}about.html">Dr. Vakili</a>
 <a class="mn-link" href="{base}index.html#reviews">Reviews</a>
 <a class="mn-link" href="{base}contact.html">Contact</a>
 <a class="btn" href="{base}book.html" onclick="closeMobNav()">Book Appointment</a>
 <a class="mn-call" href="tel:+1{PHONE.replace('-','')}">📞 {PHONE}</a>
</div>'''

def footer(base):
    care="".join(f'<a href="{base}p/{s}.html">{esc(t)}</a>' for t,s in [HEART[0],VEIN[0],VASC[0]])
    return f'''<footer><div class="wrap">
 <div class="foot-grid">
  <div>
   <img class="flogo" src="{base}logo.png" alt="Heart Vein &amp; Vascular"/>
   <p class="fabout">Advanced, personal cardiovascular, vein &amp; vascular care serving Longwood and greater Orlando for over 20 years. Your heart, your health, our focus.</p>
   <a class="soc" href="{LINKEDIN}" target="_blank" rel="noopener" aria-label="LinkedIn"><svg viewBox="0 0 24 24" fill="#fff" stroke="none"><path d="M4.98 3.5A2.5 2.5 0 1 1 0 3.5a2.5 2.5 0 0 1 4.98 0zM.5 8h4V24h-4zM8 8h3.8v2.2h.05c.53-1 1.83-2.2 3.77-2.2 4 0 4.8 2.6 4.8 6.05V24h-4v-7.2c0-1.7 0-3.9-2.4-3.9s-2.7 1.86-2.7 3.78V24H8z"/></svg></a>
  </div>
  <div><h4>Care</h4>
   <a href="{base}heart.html">Heart Services</a><a href="{base}vein-vascular.html">Vein &amp; Vascular</a>
   <a href="{base}integrative.html">Integrative Medicine</a><a href="{base}about.html">Dr. Vakili</a><a href="{base}index.html#reviews">Reviews</a></div>
  <div><h4>Patients</h4>
   <a href="{PORTAL}" target="_blank" rel="noopener">Patient Portal</a><a href="{base}r/patient-forms.html">Patient Forms</a>
   <a href="{base}r/patient-education.html">Patient Education</a><a href="{base}r/prescription-refills.html">Prescription Refills</a>
   <a href="{base}r/accepted-insurance.html">Accepted Insurance</a></div>
  <div><h4>Contact</h4>
   <a href="tel:+1{PHONE.replace('-','')}">{PHONE}</a><a href="tel:+1{TOLL.replace('-','')}">Toll-free {TOLL}</a>
   <a href="mailto:{EMAIL}">{EMAIL}</a><a href="{base}contact.html">{ADDR}</a></div>
 </div></div>
 <div class="disc">In a medical emergency, call 911. This website is for general information and appointment requests only and does not constitute medical advice. A physician referral is required for all diagnostic services.</div>
 <div class="fbar">© 2026 Heart Vein &amp; Vascular · Babak Alex Vakili, MD, FACC, FSCAI, CPI · Demo redesign for review.</div>
</footer>
<div class="mcall"><a class="call" href="tel:+1{PHONE.replace('-','')}"><svg style="width:17px;height:17px" viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2 3.1 2 2 0 0 1 4.1 1h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>Call</a>
<a class="book" href="{base}book.html">Book Appointment</a></div>
<script src="{base}assets/site.js"></script>
</body></html>'''

def page(title,desc,base,canonical,bodyhtml,og_img="img/family.jpg",schema=""):
    return head(title,desc,base,canonical,og_img,schema)+topbar(base)+nav(base)+bodyhtml+footer(base)

# render cleaned content blocks into HTML (paragraphs, lists, sub-headings, callouts)
def render_content(slug, base, skip_heads=None, skip_imgs=True):
    skip_heads = skip_heads or set()
    blocks=clean_blocks(slug)
    parts=[]; ul=[]; first_p=True
    def flush():
        nonlocal ul
        if ul:
            parts.append("<ul>"+"".join(f"<li>{esc(x)}</li>" for x in ul)+"</ul>"); ul=[]
    for b in blocks:
        t=b.get("text","")
        if b["type"]=="img":
            continue  # images handled separately as figure
        if b["type"]=="heading":
            if t.strip().rstrip(":.") in {h.rstrip(":.") for h in skip_heads}: continue
            flush(); parts.append(f"<h2>{esc(t)}</h2>")
        elif b["type"]=="li":
            ul.append(t)
        else: # p
            if t in skip_heads: continue
            flush()
            # turn bullet-ish lines into list
            cls=' class="lede"' if first_p else ''
            # split lines that contain bullet chars
            if t.strip().startswith(("•","-")) :
                ul.append(t.strip("•- ").strip()); continue
            parts.append(f"<p{cls}>{esc(t)}</p>"); first_p=False
    flush()
    return "\n".join(parts)

# ---------------- shared UI fragments ----------------
def appt_form(base):
    opts="".join(f"<option>{o}</option>" for o in
      ["Reason for visit…","Heart / Cardiology","Vein treatment","Vascular screening","Integrative medicine","Follow-up visit","Something else"])
    return f'''<div>
 <form class="cform" action="{FORM_ACTION}" method="POST" onsubmit="return submitForm(event)">
  <div class="form-body">
   <h3>Request an Appointment</h3><p class="fsub">Tell us a little about you and our office will reach out to confirm — often the same week.</p>
   <input type="hidden" name="_subject" value="New appointment request — heartveinvascular.com"/>
   <input type="text" name="_honey" style="display:none"/>
   <div class="row">
    <div class="field"><label for="fn">First name</label><input id="fn" name="First name" required placeholder="First name"/></div>
    <div class="field"><label for="ln">Last name</label><input id="ln" name="Last name" required placeholder="Last name"/></div>
   </div>
   <div class="row">
    <div class="field"><label for="ph">Phone</label><input id="ph" name="Phone" type="tel" required placeholder="(407) 000-0000"/></div>
    <div class="field"><label for="em">Email</label><input id="em" name="Email" type="email" required placeholder="you@email.com"/></div>
   </div>
   <div class="field"><label for="rs">Reason for visit</label><select id="rs" name="Reason">{opts}</select></div>
   <div class="field"><label for="ms">Anything we should know? <span style="color:var(--muted);font-weight:400">(optional)</span></label><textarea id="ms" name="Message" placeholder="Briefly describe your symptoms or question"></textarea></div>
   <button class="btn" type="submit">Request Appointment →</button>
   <p class="priv">🔒 Your information is private and used only to contact you. Do not include urgent medical details — call 911 for emergencies.</p>
  </div>
 </form>
 <div class="ok-msg">
  <div class="big"><svg viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5"/></svg></div>
  <h3>Thank you — request received.</h3>
  <p>Our office will reach out shortly to confirm your appointment. For anything urgent, please call <a href="tel:+1{PHONE.replace('-','')}" style="color:var(--rose);font-weight:600">{PHONE}</a>.</p>
 </div>
</div>'''

def contact_aside(base):
    return f'''<div class="ci-list">
 <div class="ci"><div class="ri"><svg viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2 3.1 2 2 0 0 1 4.1 1h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg></div><div><b>Call Us</b><div><a href="tel:+1{PHONE.replace('-','')}">{PHONE}</a> &nbsp;·&nbsp; <a href="tel:+1{TOLL.replace('-','')}">Toll-free {TOLL}</a></div></div></div>
 <div class="ci"><div class="ri"><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg></div><div><b>Email</b><div><a href="mailto:{EMAIL}">{EMAIL}</a></div></div></div>
 <div class="ci"><div class="ri"><svg viewBox="0 0 24 24"><path d="M12 21s-6-5.7-6-10a6 6 0 1 1 12 0c0 4.3-6 10-6 10z"/><circle cx="12" cy="11" r="2"/></svg></div><div><b>Visit Us</b><div>2170 W State Road 434, Suite 190<br>Longwood, FL 32779</div></div></div>
 <div class="ci"><div class="ri"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><div><b>Office Hours</b><div>Monday – Friday: 8:00 AM – 4:30 PM<br>Saturday &amp; Sunday: Closed</div></div></div>
 <div class="cmap"><iframe loading="lazy" title="Map to Heart Vein &amp; Vascular" src="https://maps.google.com/maps?q=2170%20West%20State%20Road%20434%20Suite%20190%20Longwood%20FL%2032779&t=m&z=14&output=embed&iwloc=near"></iframe></div>
</div>'''

def reviews_carousel(base):
    cards=[]
    for r in REVIEWS:
        initials="".join(w[0] for w in r["name"].split()[:2]).upper()
        stars="★"*int(r.get("stars",5))
        cards.append(f'''<div class="rev-card clamp"><div class="q">&ldquo;</div><div class="stars">{stars}</div>
   <p class="txt">{esc(r["text"])}</p>
   <div class="who"><div class="av">{esc(initials)}</div><div><b>{esc(r["name"])}</b><small>Verified patient review</small></div></div></div>''')
    return f'''<section class="section soft" id="reviews"><div class="wrap">
 <div class="center" style="max-width:640px;margin:0 auto 40px">
  <span class="eyebrow" style="justify-content:center">Patient Stories</span>
  <h2 style="font-size:40px;margin:16px 0 8px">Loved by Central Florida families.</h2>
  <p class="lead">Real words from patients who&rsquo;ve trusted Dr. Vakili — many for 15, 20 years and more.</p>
 </div>
 <div class="rev-wrap"><div class="rev-track" id="revTrack">{''.join(cards)}</div>
  <div class="rev-nav">
   <span class="rev-source"><span class="g">G</span> Verified Google reviews · ★★★★★</span>
   <div class="rev-arrows">
    <button id="revPrev" aria-label="Previous reviews"><span class="ar"><svg viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></svg></span></button>
    <button id="revNext" aria-label="More reviews"><span class="ar"><svg viewBox="0 0 24 24"><path d="M9 18l6-6-6-6"/></svg></span></button>
   </div>
  </div>
 </div>
</div></section>'''

# ---------------- HOME ----------------
def build_home():
    base=""
    slides=[
     ("Your Heart, Your Health,","Our Focus","Experience advanced cardiovascular testing and treatment in a private, deeply personal setting — where you always see your physician, Dr. Babak Alex Vakili.","heart.html","Explore Heart Care"),
     ("Your Legs, Your Comfort,","Our Priority","Find relief from vein pain, swelling, and cosmetic concerns with advanced, minimally invasive vein treatments in a calm, private setting.","vein-vascular.html","Explore Vein Care"),
     ("Your Circulation, Your Strength,","Our Commitment","Advanced vascular diagnostics and treatments to identify, manage, and prevent serious circulatory conditions — expert care in a comfortable environment.","vein-vascular.html","Explore Vascular Care"),
     ("Your Cardiologist, Your Advocate,","Our Expert","With over 20 years of experience in Central Florida, Dr. Vakili blends advanced expertise with a deeply personal approach to every patient.","about.html","Meet Dr. Vakili"),
    ]
    sl_html=""
    for i,(a,b,sub,href,btn) in enumerate(slides):
        on=" on" if i==0 else ""
        sl_html+=f'''<div class="slide{on}"><span class="eyebrow">Heart · Vein · Vascular — Longwood, FL</span>
      <h1>{esc(a)}<br><span class="accent">{esc(b)}</span></h1>
      <p class="sub">{esc(sub)}</p>
      <div class="hero-cta"><a class="btn" href="{base}book.html">Book an Appointment</a><a class="btn ghost" href="{base}{href}">{esc(btn)}</a></div>
      </div>'''
    hero_imgs=["img/family.jpg","img/real_legs.jpg","img/active.jpg","drvakili.png"]
    himg="".join(f'<img class="{"on" if i==0 else ""}" src="{base}{s}" alt="" {"loading=lazy" if i else ""}/>' for i,s in enumerate(hero_imgs))

    # service blocks
    def svc_block(cat_title,tag,intro,items,hub,img,rev=False):
        links="".join(f'<a href="{base}p/{s}.html">{esc(t)}</a>' for t,s in items)
        cls="svc-block rev" if rev else "svc-block"
        return f'''<div class="{cls}">
   <div class="sb-img"><img src="{base}{img}" alt="{esc(cat_title)}" loading="lazy"/></div>
   <div><span class="sb-tag"><svg style="width:15px;height:15px" viewBox="0 0 24 24"><path d="M3 12h4l2 5 4-12 2 7h6"/></svg>{esc(tag)}</span>
    <h3>{esc(cat_title)}</h3><p style="color:var(--muted)">{esc(intro)}</p>
    <div class="svc-list">{links}</div>
    <a class="btn ghost sm" style="margin-top:20px" href="{base}{hub}">All {esc(tag.lower())} services →</a></div>
  </div>'''

    body=f'''
<section class="hero"><div class="hero-in">
 <div class="slides">{sl_html}<div class="hero-dots">{''.join(f'<button class="{"on" if i==0 else ""}" aria-label="Slide {i+1}"></button>' for i in range(len(slides)))}</div></div>
 <div class="hero-figure"><div class="hero-imgs">{himg}</div>
  <div class="float-card tl"><div class="n">20+</div><div><small>Years caring for<br>Central Florida</small></div></div>
  <div class="float-card br"><span class="stars">★★★★★</span><b>&ldquo;He truly cares.&rdquo;</b><small>— verified patient review</small></div>
 </div>
</div></section>

<div class="trustrip"><div class="wrap">
 <div class="ti"><span class="ic"><svg viewBox="0 0 24 24"><path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5z"/><path d="m9 12 2 2 4-4"/></svg></span><div>Board-Certified<small>Interventional cardiology</small></div></div>
 <div class="ti"><span class="ic"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg></span><div>You See the Physician<small>Every visit, never handed off</small></div></div>
 <div class="ti"><span class="ic"><svg viewBox="0 0 24 24"><path d="M12 21s-6-5.7-6-10a6 6 0 1 1 12 0c0 4.3-6 10-6 10z"/><circle cx="12" cy="11" r="2"/></svg></span><div>Private Practice<small>Independent since 2002</small></div></div>
 <div class="ti"><span class="ic"><svg viewBox="0 0 24 24"><path d="M3 12h4l2 5 4-12 2 7h6"/></svg></span><div>Heart · Vein · Vascular<small>Complete care, one office</small></div></div>
</div></div>

<section class="section"><div class="wrap">
 <div class="center" style="max-width:600px;margin:0 auto 44px"><span class="eyebrow" style="justify-content:center">What We Do</span>
  <h2 style="font-size:40px;margin:16px 0 8px">Everything we offer, one trusted practice.</h2>
  <p class="lead">From the heart to the veins to the vascular system — complete diagnostics and treatment by a single, board-certified physician who knows your full history.</p></div>
 <div class="pillars">
  <a class="pillar p1" href="{base}heart.html"><span class="pic"><svg viewBox="0 0 24 24"><path d="M12 21s-7-4.5-9.5-9C1 9 2.5 5 6 5c2 0 3 1 4 2.5C11 6 12 5 14 5c3.5 0 5 4 3.5 7-2.5 4.5-9.5 9-9.5 9z" stroke="#fff"/></svg></span><h3>Heart</h3><p>Diagnostics, imaging &amp; interventional cardiology</p></a>
  <a class="pillar p2" href="{base}vein-vascular.html"><span class="pic"><svg viewBox="0 0 24 24"><path d="M6 3v6a6 6 0 0 0 12 0V3M9 21c0-4 6-4 6-8" stroke="#fff"/></svg></span><h3>Vein</h3><p>Minimally invasive relief for varicose &amp; spider veins</p></a>
  <a class="pillar p3" href="{base}vein-vascular.html"><span class="pic"><svg viewBox="0 0 24 24"><path d="M3 12h4l2-7 4 14 2-7h6" stroke="#fff"/></svg></span><h3>Vascular</h3><p>Screening &amp; treatment of circulatory conditions</p></a>
  <a class="pillar p4" href="{base}about.html"><span class="pic"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" stroke="#fff"/><path d="M4 21a8 8 0 0 1 16 0" stroke="#fff"/></svg></span><h3>Dr. Vakili</h3><p>20+ years · former Chief of Cardiology</p></a>
 </div>
</div></section>

<section class="section soft"><div class="wrap"><div class="split">
 <div class="imgwrap"><img src="{base}img/care.jpg" alt="Personal, attentive cardiovascular care" loading="lazy"/>
  <div class="badge"><span class="ic"><svg viewBox="0 0 24 24"><path d="M12 21s-7-4.5-9.5-9C1 9 2.5 5 6 5c2 0 3 1 4 2.5C11 6 12 5 14 5c3.5 0 5 4 3.5 7-2.5 4.5-9.5 9-9.5 9z"/></svg></span><div><b>Private Practice</b><small>You see Dr. Vakili — every visit</small></div></div></div>
 <div><span class="eyebrow">Welcome to Heart Vein &amp; Vascular</span>
  <h2>Hospital-grade medicine,<br>a genuinely personal touch.</h2>
  <p class="lead">For over two decades, Central Florida families have trusted Dr. Babak Alex Vakili with the care that matters most. As an independent private practice, you&rsquo;re never handed off to a large group — you meet your physician, get answers, and move through every step with clarity.</p>
  <div class="checks">
   <div class="check"><span class="ck"><svg viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5"/></svg></span><span><b>You always see your physician</b> — never handed off to a rotating team.</span></div>
   <div class="check"><span class="ck"><svg viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5"/></svg></span><span><b>Advanced diagnostics in-office</b> — faster answers in a calm, private setting.</span></div>
   <div class="check"><span class="ck"><svg viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5"/></svg></span><span><b>Minimally invasive treatments</b> — often virtually painless, with quick recovery.</span></div>
  </div>
  <a class="btn" style="margin-top:26px" href="{base}book.html">Become a Patient</a></div>
</div></div></section>

<section class="section"><div class="wrap">
 <div class="center" style="max-width:560px;margin:0 auto 30px"><span class="eyebrow" style="justify-content:center">Comprehensive Care</span>
  <h2 style="font-size:38px;margin:16px 0">Three specialties, one physician.</h2></div>
 {svc_block("Heart &amp; Cardiology","Heart","Advanced cardiovascular diagnostics, monitoring and interventional treatment — from prevention to life-saving intervention.",HEART[:8],"heart.html","img/cardio.jpg")}
 {svc_block("Vein Care","Vein","Comfortable, minimally invasive relief from varicose &amp; spider veins, leg swelling and venous disease — so your legs look and feel their best.",VEIN[:8],"vein-vascular.html",page_img("sclerotherapy") or "img/real_legs.jpg",rev=True)}
 {svc_block("Vascular &amp; Diagnostics","Vascular","Comprehensive screening, diagnosis &amp; treatment of circulatory and vascular conditions — identifying and managing problems early.",VASC,"vein-vascular.html","img/vascular-art.jpg")}
</div></section>

<section class="section soft"><div class="wrap"><div class="doc-in">
 <div class="doc-card"><img src="{base}drvakili.png" alt="Dr. Babak Alex Vakili, MD, FACC, FSCAI, CPI"/>
  <h3>Dr. Babak Alex Vakili</h3><div class="cred">MD · FACC · FSCAI · CPI</div>
  <div class="tags"><span>Interventional Cardiology</span><span>Vascular Medicine</span><span>Venous &amp; Lymphatic</span></div></div>
 <div><span class="eyebrow">Meet Your Physician</span>
  <h2>Two decades of trusted cardiovascular expertise.</h2>
  <p class="lead">Dr. Babak Alex Vakili is a distinguished interventional cardiologist with additional subspecialty certifications in vascular medicine as well as venous and lymphatic disorders. In private practice in the Orlando area since 2002, he brings over two decades of expertise and dedication to cardiovascular medicine.</p>
  <p style="color:var(--muted);margin-top:14px">As former <b>Chief of Cardiology at South Seminole Hospital</b>, he combines clinical leadership with a deeply personal approach — listening carefully, explaining clearly, and building relationships that span decades.</p>
  <div class="statbox">
   <div class="stat"><b>Board Certified</b><span>Cardiovascular medicine</span></div>
   <div class="stat"><b>FACC · FSCAI</b><span>Fellowship distinctions</span></div>
   <div class="stat"><b>20+ Years</b><span>Serving Central Florida</span></div>
   <div class="stat"><b>Since 2002</b><span>Independent private practice</span></div>
  </div>
  <a class="btn" style="margin-top:24px" href="{base}about.html">Read Full Bio &amp; Credentials →</a></div>
</div></div></section>

<section class="section"><div class="wrap"><div class="sem-in">
 <div class="imgwrap"><img src="{base}iset.jpeg" alt="Dr. Vakili at the ISET International Conference" loading="lazy"/></div>
 <div><span class="eyebrow">Seminars &amp; Keynote Events</span>
  <h2>Staying at the leading edge of cardiovascular care.</h2>
  <p class="lead">Dr. Vakili attended the International Symposium on Endovascular Therapy (ISET) in Miami — bringing together leading experts in interventional cardiology, interventional radiology, and vascular surgery for an advanced educational experience.</p>
  <p style="color:var(--muted);margin-top:14px">He participates in discussions on the latest advancements in techniques, technologies, and patient-care strategies — returning with insights that bring his patients the most up-to-date treatments in cardiovascular medicine.</p></div>
</div></div></section>

<section class="section soft"><div class="wrap">
 <div class="li-head">
  <div><span class="eyebrow">From Dr. Vakili</span><h2 style="font-size:34px;margin-top:12px">Insights &amp; thought leadership.</h2></div>
  <a class="li-btn" href="{LINKEDIN}" target="_blank" rel="noopener"><svg style="width:18px;height:18px" viewBox="0 0 24 24" fill="#fff" stroke="none"><path d="M4.98 3.5A2.5 2.5 0 1 1 0 3.5a2.5 2.5 0 0 1 4.98 0zM.5 8h4V24h-4zM8 8h3.8v2.2h.05c.53-1 1.83-2.2 3.77-2.2 4 0 4.8 2.6 4.8 6.05V24h-4v-7.2c0-1.7 0-3.9-2.4-3.9s-2.7 1.86-2.7 3.78V24H8z"/></svg>Follow on LinkedIn</a>
 </div>
 <div class="li-grid">
  <a class="li-card" href="{LINKEDIN}recent-activity/all/" target="_blank" rel="noopener"><div class="dt">June 2026</div><h3>RNA Splicing and Cardiovascular Disease</h3><p>&ldquo;When I saw this 2026 State-of-the-Art Review in the European Heart Journal, I thought it would be painfully boring — but by the end I realized the concept is going to be central to how we treat heart disease…&rdquo;</p><span class="rd">Read on LinkedIn →</span></a>
  <a class="li-card" href="{LINKEDIN}recent-activity/all/" target="_blank" rel="noopener"><div class="dt">March 2026</div><h3>2026 ACC/AHA Dyslipidemia Guideline</h3><p>&ldquo;The 2026 ACC/AHA Multisociety Guideline for the Management of Dyslipidemia was just published in JACC. The guideline introduces the PREVENT risk calculator…&rdquo;</p><span class="rd">Read on LinkedIn →</span></a>
  <a class="li-card" href="{LINKEDIN}recent-activity/all/" target="_blank" rel="noopener"><div class="dt">February 2026</div><h3>Anticoagulation After Afib Ablation?</h3><p>&ldquo;One of the most common questions I get after referring a patient for atrial fibrillation ablation is simple: &lsquo;Can I stop my anticoagulation?&rsquo; Here&rsquo;s how I think about that decision with each patient…&rdquo;</p><span class="rd">Read on LinkedIn →</span></a>
 </div>
</div></section>

{reviews_carousel(base)}

<section class="section"><div class="wrap">
 <div class="center" style="max-width:560px;margin:0 auto 40px"><span class="eyebrow" style="justify-content:center">For Our Patients</span>
  <h2 style="font-size:38px;margin:16px 0 8px">Patient resources, made simple.</h2>
  <p class="lead">Everything you need before and between visits — all in one place.</p></div>
 <div class="res-grid">
  <a class="res-card" href="{PORTAL}" target="_blank" rel="noopener"><span class="ic"><svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18"/></svg></span><div><h4>Patient Portal</h4><p>Access records, results &amp; messages securely via healow.</p></div></a>
  <a class="res-card" href="{base}r/patient-forms.html"><span class="ic"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg></span><div><h4>Patient Forms</h4><p>Complete your new-patient paperwork ahead of time.</p></div></a>
  <a class="res-card" href="{base}r/patient-education.html"><span class="ic"><svg viewBox="0 0 24 24"><path d="M4 19V5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2z"/></svg></span><div><h4>Patient Education</h4><p>Trusted information on your conditions &amp; procedures.</p></div></a>
  <a class="res-card" href="{base}r/prescription-refills.html"><span class="ic"><svg viewBox="0 0 24 24"><path d="M10.5 20.5 3.5 13.5a5 5 0 0 1 7-7l7 7a5 5 0 0 1-7 7z"/><path d="M8.5 8.5l7 7"/></svg></span><div><h4>Prescription Refills</h4><p>Request refills quickly — call or use the portal.</p></div></a>
  <a class="res-card" href="{base}r/accepted-insurance.html"><span class="ic"><svg viewBox="0 0 24 24"><path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5z"/></svg></span><div><h4>Accepted Insurance</h4><p>We work with most major plans — see the full list.</p></div></a>
  <a class="res-card" href="{base}r/cancellation-policy.html"><span class="ic"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></span><div><h4>Cancellation Policy</h4><p>Please give us 24 hours&rsquo; notice to reschedule a visit.</p></div></a>
 </div>
</div></section>

<section class="section soft" id="contact"><div class="wrap">
 <div class="center" style="max-width:560px;margin:0 auto 40px"><span class="eyebrow" style="justify-content:center">Schedule a Visit</span>
  <h2 style="font-size:40px;margin:16px 0 8px">Request your appointment.</h2>
  <p class="lead">Tell us a little about you and our office will reach out to confirm — often the same week.</p></div>
 <div class="c-in">{appt_form(base)}{contact_aside(base)}</div>
</div></section>
'''
    schema=home_schema()
    return page("Heart Vein & Vascular | Dr. Babak Alex Vakili, MD, FACC — Cardiology · Vein · Vascular · Longwood, FL",
        "Heart Vein & Vascular — advanced, personal cardiovascular, vein & vascular care in Longwood / Orlando, FL. Dr. Babak Alex Vakili, MD, FACC, FSCAI — 20+ years. Your Heart, Your Health, Our Focus.",
        base,"index.html",body,schema=schema)

# ---------------- JSON-LD schema ----------------
def home_schema():
    revs=[]
    for r in REVIEWS[:6]:
        revs.append('{"@type":"Review","author":{"@type":"Person","name":%s},"reviewRating":{"@type":"Rating","ratingValue":"5","bestRating":"5"},"reviewBody":%s}'
            %(json.dumps(r["name"]), json.dumps(re.sub(r'\s+',' ',r["text"])[:300])))
    data='''{"@context":"https://schema.org","@type":["MedicalClinic","MedicalBusiness"],
"name":"Heart Vein & Vascular","url":"%s/","telephone":"+1-407-990-1921",
"image":"%s/img/family.jpg","priceRange":"$$","email":"%s",
"address":{"@type":"PostalAddress","streetAddress":"2170 W State Road 434, Ste 190","addressLocality":"Longwood","addressRegion":"FL","postalCode":"32779","addressCountry":"US"},
"geo":{"@type":"GeoCoordinates","latitude":28.7036,"longitude":-81.3942},
"openingHoursSpecification":{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],"opens":"08:00","closes":"16:30"},
"medicalSpecialty":["Cardiovascular","Vascular"],
"aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0","reviewCount":"%d"},
"review":[%s],
"employee":{"@type":"Physician","name":"Babak Alex Vakili, MD, FACC, FSCAI, CPI","jobTitle":"Interventional Cardiologist","medicalSpecialty":["Cardiovascular","Vascular"],"alumniOf":"New York University"}}'''%(SITE,SITE,EMAIL,len(REVIEWS),",".join(revs))
    return '<script type="application/ld+json">%s</script>'%data

def proc_schema(title, desc, canonical, cat_label):
    return ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"MedicalWebPage","name":%s,"description":%s,"url":%s,'
            '"about":{"@type":"MedicalProcedure"},"isPartOf":{"@type":"MedicalClinic","name":"Heart Vein & Vascular","url":"%s/"},'
            '"breadcrumb":{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},{"@type":"ListItem","position":2,"name":%s},{"@type":"ListItem","position":3,"name":%s}]}}</script>'
            %(json.dumps(title),json.dumps(desc),json.dumps(SITE+"/"+canonical),SITE,SITE,json.dumps(cat_label),json.dumps(title)))

# ---------------- hub pages ----------------
def hub_intro(slug):
    for b in clean_blocks(slug):
        if b["type"]=="p" and len(b.get("text",""))>60:
            return b["text"]
    return ""

def cardgrid(items, base):
    cells=[]
    for t,s in items:
        img=page_img(s) or "img/care.jpg"
        cells.append(f'''<a class="pcard" href="{base}p/{s}.html"><div class="ph"><img src="{base}{img}" alt="{esc(t)}" loading="lazy"/></div>
   <div class="pb"><h3>{esc(t)}</h3><p>{esc(teaser(s))}</p><span class="more">Learn more <span class="ar"><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span></span></div></a>''')
    return f'<div class="cardgrid">{"".join(cells)}</div>'

def build_heart_hub():
    base=""
    intro=hub_intro("heart-procedures") or "At Heart Vein & Vascular, our Heart Services combine advanced diagnostics and targeted therapies to prevent, find, and treat cardiovascular disease."
    body=f'''<header class="pagehead"><div class="wrap"><div class="crumb"><a href="{base}index.html">Home</a> › <span>Heart Services</span></div>
 <span class="tag"><svg style="width:14px;height:14px" viewBox="0 0 24 24"><path d="M12 21s-7-4.5-9.5-9C1 9 2.5 5 6 5c2 0 3 1 4 2.5C11 6 12 5 14 5c3.5 0 5 4 3.5 7-2.5 4.5-9.5 9-9.5 9z"/></svg>Cardiology</span>
 <h1>Heart Services</h1><p class="intro">{esc(intro)}</p></div></header>
<section class="section"><div class="wrap">{cardgrid(HEART, base)}</div></section>
{cta_band(base)}'''
    return page("Heart Services — Cardiology | Heart Vein & Vascular, Longwood FL",
        "Advanced cardiac diagnostics and treatment at Heart Vein & Vascular in Longwood, FL — catheterization, stress testing, echocardiogram, Holter monitoring and more, with Dr. Babak Alex Vakili.",
        base,"heart.html",body,og_img="img/cardio.jpg")

def build_vein_hub():
    base=""
    intro=hub_intro("vein-procedures") or hub_intro("endovenous-services") or "Comfortable, minimally invasive relief from varicose and spider veins, leg swelling and venous disease — plus complete vascular screening and diagnostics."
    body=f'''<header class="pagehead"><div class="wrap"><div class="crumb"><a href="{base}index.html">Home</a> › <span>Vein &amp; Vascular Services</span></div>
 <span class="tag"><svg style="width:14px;height:14px" viewBox="0 0 24 24"><path d="M6 3v6a6 6 0 0 0 12 0V3"/></svg>Vein · Vascular · Diagnostics</span>
 <h1>Vein &amp; Vascular Services</h1><p class="intro">{esc(intro)}</p></div></header>
<section class="section"><div class="wrap">
 <h2 style="font-size:28px;margin-bottom:22px">Vein Treatments</h2>{cardgrid(VEIN, base)}
 <h2 style="font-size:28px;margin:54px 0 22px">Vascular Screening &amp; Diagnostics</h2>{cardgrid(VASC, base)}
 <h2 style="font-size:28px;margin:54px 0 22px">Helpful Information</h2>{cardgrid(INFO, base)}
</div></section>
{cta_band(base)}'''
    return page("Vein & Vascular Services | Heart Vein & Vascular, Longwood FL",
        "Minimally invasive vein treatment and complete vascular screening at Heart Vein & Vascular in Longwood, FL — sclerotherapy, VenaSeal, ablation, carotid & arterial duplex, AAA screening and more.",
        base,"vein-vascular.html",body,og_img="img/vascular-art.jpg")

def build_integrative_hub():
    base=""
    intro=hub_intro("integrative-medicine") or "Integrative therapies that complement your cardiovascular care — from IV vitamin infusions to advanced metabolic testing."
    body=f'''<header class="pagehead"><div class="wrap"><div class="crumb"><a href="{base}index.html">Home</a> › <span>Integrative Medicine</span></div>
 <span class="tag">Wellness</span><h1>Integrative Medicine</h1><p class="intro">{esc(intro)}</p></div></header>
<section class="section"><div class="wrap">{cardgrid(INTEG, base)}</div></section>
{cta_band(base)}'''
    return page("Integrative Medicine — IV Vitamins & Metabolic Testing | Heart Vein & Vascular",
        "Integrative medicine at Heart Vein & Vascular in Longwood, FL — IV vitamin therapy and advanced metabolic testing to complement your cardiovascular care.",
        base,"integrative.html",body,og_img="img/care.jpg")

def cta_band(base):
    return f'''<section class="section soft"><div class="wrap center" style="max-width:620px;margin:0 auto">
 <span class="eyebrow" style="justify-content:center">Ready When You Are</span>
 <h2 style="font-size:34px;margin:16px 0 10px">Have a question or ready to be seen?</h2>
 <p class="lead" style="margin-bottom:26px">Request an appointment and our office will reach out to confirm — often the same week. A physician referral is required for diagnostic services.</p>
 <div style="display:flex;gap:13px;justify-content:center;flex-wrap:wrap"><a class="btn" href="{base}book.html">Book an Appointment</a><a class="btn ghost" href="tel:+1{PHONE.replace('-','')}">Call {PHONE}</a></div>
</div></section>'''

# ---------------- procedure detail ----------------
def related_cards(slug, base, cat):
    pool=[(t,s) for t,s in (HEART+VEIN+VASC+INFO+INTEG) if PROC_CAT.get(s,("",""))[0]==cat and s!=slug][:3]
    if len(pool)<3:
        pool=[(t,s) for t,s in (HEART+VEIN+VASC) if s!=slug][:3]
    return cardgrid(pool, base)

def build_procedure(slug):
    base="../"
    cat,disp=PROC_CAT.get(slug,("heart",DATA[slug]["h1"]))
    cat_label, hub = CAT[cat]
    title_full=DATA[slug]["h1"] or disp
    desc=DATA[slug].get("meta_desc") or teaser(slug,150)
    img=page_img(slug)
    fig=f'<div class="proc-figure"><img src="{base}{img}" alt="{esc(disp)}"/></div>' if img else ""
    content=render_content(slug, base)
    # pull a preparation/risk callout if present
    canonical=f"p/{slug}.html"
    body=f'''<header class="pagehead"><div class="wrap"><div class="crumb"><a href="{base}index.html">Home</a> › <a href="{base}{hub}">{esc(cat_label)}</a> › <span>{esc(disp)}</span></div>
 <span class="tag">{esc(cat_label)}</span><h1>{esc(title_full)}</h1></div></header>
<section><div class="wrap"><div class="proc">
 <div class="proc-body">{fig}{content}
  <div class="callout"><b>Please note:</b> A physician referral is required for all diagnostic services. Have questions about whether this is right for you? <a href="{base}contact.html" style="color:var(--rose-d);font-weight:600;text-decoration:underline">Contact our office</a> or call <a href="tel:+1{PHONE.replace('-','')}" style="color:var(--rose-d);font-weight:600">{PHONE}</a>.</div>
 </div>
 <aside><div class="sidecard"><h4>Schedule this service</h4><p>Request an appointment and our office will reach out to confirm — often the same week.</p>
  <a class="btn" href="{base}book.html">Book Appointment</a>
  <a class="ph" href="tel:+1{PHONE.replace('-','')}"><svg style="width:16px;height:16px" viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2 3.1 2 2 0 0 1 4.1 1h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>{PHONE}</a>
  <div class="hours"><b>Office Hours</b><br>Mon–Fri 8:00 AM – 4:30 PM<br>Sat &amp; Sun: Closed<br><br><b>Address</b><br>2170 W State Road 434, Ste 190<br>Longwood, FL 32779</div></div></aside>
</div></div></section>
<section class="section soft related"><div class="wrap"><h2>Related {esc(cat_label.split(" ")[0])} services</h2><p class="lead center" style="margin-bottom:34px">More ways we care for you under one roof.</p>{related_cards(slug, base, cat)}</div></section>'''
    return page(f"{title_full} | Heart Vein & Vascular, Longwood FL", desc, base, canonical, body,
        og_img=(img if img else "img/family.jpg"), schema=proc_schema(title_full,desc,canonical,cat_label))

# ---------------- bio ----------------
def build_about():
    base=""
    body_blocks=render_content("doctor", base, skip_heads=BIO_SKIP_HEADS)
    img=local_img("https://heartveinvascular.com/wp-content/uploads/2024/08/drvakili-profile-e1723724981629.png") or "drvakili.png"
    body=f'''<header class="pagehead"><div class="wrap"><div class="crumb"><a href="{base}index.html">Home</a> › <span>Dr. Babak Alex Vakili</span></div>
 <span class="tag">Meet Your Physician</span><h1>Dr. Babak Alex Vakili, MD, FACC, FSCAI, CPI</h1>
 <p class="intro">Distinguished interventional cardiologist with subspecialty certifications in vascular medicine and venous &amp; lymphatic disorders — in private practice in the Orlando area since 2002.</p></div></header>
<section><div class="wrap"><div class="proc">
 <div class="proc-body"><div class="proc-figure" style="max-height:none"><img src="{base}{img}" alt="Dr. Babak Alex Vakili"/></div>{body_blocks}</div>
 <aside><div class="sidecard"><h4>Book with Dr. Vakili</h4><p>Request an appointment and our office will reach out to confirm.</p>
  <a class="btn" href="{base}book.html">Book Appointment</a>
  <a class="ph" href="tel:+1{PHONE.replace('-','')}">{PHONE}</a>
  <div class="hours"><b>Quick links</b><br><a href="{base}hospital-admissions.html" style="color:var(--rose)">Hospital Admissions →</a><br><a href="{base}office-location.html" style="color:var(--rose)">Office Location →</a><br><a href="{LINKEDIN}" target="_blank" rel="noopener" style="color:var(--rose)">LinkedIn ↗</a></div></div></aside>
</div></div></section>
{cta_band(base)}'''
    return page("About Dr. Babak Alex Vakili, MD, FACC, FSCAI | Heart Vein & Vascular",
        "Dr. Babak Alex Vakili is a distinguished interventional cardiologist in Longwood, FL with 20+ years' experience, former Chief of Cardiology at South Seminole Hospital. Board certifications & affiliations.",
        base,"about.html",body,og_img="drvakili.png")

def build_simple(slug, title, label, canonical, desc):
    base=""
    content=render_content(slug, base, skip_heads=BIO_SKIP_HEADS)
    body=f'''<header class="pagehead"><div class="wrap"><div class="crumb"><a href="{base}index.html">Home</a> › <a href="{base}about.html">Dr. Vakili</a> › <span>{esc(label)}</span></div>
 <span class="tag">Dr. Vakili</span><h1>{esc(title)}</h1></div></header>
<section><div class="wrap"><div class="proc"><div class="proc-body">{content}</div>
 <aside><div class="sidecard"><h4>Questions?</h4><p>Our office is happy to help.</p><a class="btn" href="{base}book.html">Book Appointment</a><a class="ph" href="tel:+1{PHONE.replace('-','')}">{PHONE}</a></div></aside>
</div></div></section>{cta_band(base)}'''
    return page(f"{title} | Heart Vein & Vascular", desc, base, canonical, body)

# ---------------- resource pages ----------------
def build_resource(slug, title, desc):
    base="../"
    content=render_content(slug, base)
    extra=""
    if slug=="patient-forms":
        extra=f'<div class="callout"><b>New patients:</b> Completing your forms before your visit saves time at check-in. Bring a photo ID, insurance card, and a list of current medications. Call <a href="tel:+1{PHONE.replace("-","")}" style="color:var(--rose-d);font-weight:600">{PHONE}</a> if you need forms emailed to you.</div>'
    body=f'''<header class="pagehead"><div class="wrap"><div class="crumb"><a href="{base}index.html">Home</a> › <a href="{base}resources.html">Patient Resources</a> › <span>{esc(title)}</span></div>
 <span class="tag">Patient Resources</span><h1>{esc(title)}</h1></div></header>
<section><div class="wrap"><div class="proc"><div class="proc-body">{content}{extra}</div>
 <aside><div class="sidecard"><h4>Patient Portal</h4><p>Access records, results &amp; messages securely via healow.</p><a class="btn" href="{PORTAL}" target="_blank" rel="noopener">Open Portal ↗</a><a class="ph" href="tel:+1{PHONE.replace('-','')}">{PHONE}</a></div></aside>
</div></div></section>'''
    return page(f"{title} | Heart Vein & Vascular", desc, base, f"r/{slug}.html", body)

def build_resources_hub():
    base=""
    cells=[]
    icons={"patient-forms":"M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z","patient-education":"M4 19V5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2z","prescription-refills":"M10.5 20.5 3.5 13.5a5 5 0 0 1 7-7l7 7a5 5 0 0 1-7 7z","accepted-insurance":"M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5z","cancellation-policy":"M12 7v5l3 2"}
    for t,s,k in RESOURCES:
        if k=="ext":
            cells.append(f'<a class="res-card" href="{s}" target="_blank" rel="noopener"><span class="ic"><svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18"/></svg></span><div><h4>{esc(t)} ↗</h4><p>Access records, results &amp; messages securely via healow.</p></div></a>')
        else:
            cells.append(f'<a class="res-card" href="{base}r/{s}.html"><span class="ic"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="{icons.get(s,"M12 7v5l3 2")}"/></svg></span><div><h4>{esc(t)}</h4><p>{esc(teaser(s,90))}</p></div></a>')
    body=f'''<header class="pagehead"><div class="wrap"><div class="crumb"><a href="{base}index.html">Home</a> › <span>Patient Resources</span></div>
 <span class="tag">For Our Patients</span><h1>Patient Resources</h1><p class="intro">Everything you need before and between visits — all in one place.</p></div></header>
<section class="section"><div class="wrap"><div class="res-grid">{"".join(cells)}</div></div></section>{cta_band(base)}'''
    return page("Patient Resources | Heart Vein & Vascular, Longwood FL",
        "Patient resources for Heart Vein & Vascular — patient portal, new-patient forms, education, prescription refills, accepted insurance and cancellation policy.",
        base,"resources.html",body)

# ---------------- contact / book / shop ----------------
def build_contact():
    base=""
    body=f'''<header class="pagehead"><div class="wrap"><div class="crumb"><a href="{base}index.html">Home</a> › <span>Contact</span></div>
 <span class="tag">Get In Touch</span><h1>Contact &amp; appointments.</h1><p class="intro">Request an appointment below, or reach our office directly. We&rsquo;re here Monday through Friday, 8:00 AM – 4:30 PM.</p></div></header>
<section class="section"><div class="wrap"><div class="c-in">{appt_form(base)}{contact_aside(base)}</div></div></section>'''
    return page("Contact Heart Vein & Vascular | Longwood, FL · (407) 990-1921",
        "Contact Heart Vein & Vascular in Longwood, FL. Call (407) 990-1921 or request an appointment online. 2170 W State Road 434, Ste 190, Longwood, FL 32779.",
        base,"contact.html",body)

def build_book():
    base=""
    body=f'''<header class="pagehead"><div class="wrap"><div class="crumb"><a href="{base}index.html">Home</a> › <span>Book an Appointment</span></div>
 <span class="tag">Schedule a Visit</span><h1>Book your appointment.</h1><p class="intro">Online self-scheduling is coming soon. In the meantime, request a visit below or call us — our office will confirm a time that works for you, often the same week.</p></div></header>
<section class="section"><div class="wrap">
 <div class="callout" style="max-width:760px;margin:0 auto 36px;text-align:center"><b>📅 Online booking is on the way.</b> &nbsp;We&rsquo;re integrating real-time self-scheduling. For now, use the request form below or call <a href="tel:+1{PHONE.replace('-','')}" style="color:var(--rose-d);font-weight:700">{PHONE}</a> — existing patients can also book through the <a href="{PORTAL}" target="_blank" rel="noopener" style="color:var(--rose-d);font-weight:700">Patient Portal ↗</a>.</div>
 <div class="c-in">{appt_form(base)}{contact_aside(base)}</div>
</div></section>'''
    return page("Book an Appointment | Heart Vein & Vascular, Longwood FL",
        "Book an appointment with Dr. Babak Alex Vakili at Heart Vein & Vascular in Longwood, FL. Request a visit online or call (407) 990-1921.",
        base,"book.html",body)

def build_shop():
    base=""
    content=render_content("shop", base)
    body=f'''<header class="pagehead"><div class="wrap"><div class="crumb"><a href="{base}index.html">Home</a> › <span>Shop</span></div>
 <span class="tag">Medical-Grade Products</span><h1>Products you can trust.</h1></div></header>
<section class="section"><div class="wrap" style="max-width:820px">{content}
 <div class="callout" style="margin-top:30px"><b>Interested in a product?</b> Ask our office at your next visit or call <a href="tel:+1{PHONE.replace('-','')}" style="color:var(--rose-d);font-weight:700">{PHONE}</a>. Online ordering is coming soon.</div>
</div></section>{cta_band(base)}'''
    return page("Shop — Medical-Grade Products | Heart Vein & Vascular",
        "Medical-grade products and supplements you can trust, recommended by Heart Vein & Vascular in Longwood, FL.",
        base,"shop.html",body)

# ---------------- main ----------------
def write(path, content):
    full=os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True) if os.path.dirname(path) else None
    open(full,"w").write(content)

def main():
    pages={}
    pages["index.html"]=build_home()
    pages["heart.html"]=build_heart_hub()
    pages["vein-vascular.html"]=build_vein_hub()
    pages["integrative.html"]=build_integrative_hub()
    pages["about.html"]=build_about()
    pages["hospital-admissions.html"]=build_simple("hospital-admissions","Hospital Admissions","Hospital Admissions","hospital-admissions.html","Hospital admissions and affiliations for Dr. Babak Alex Vakili — Heart Vein & Vascular, Longwood FL.")
    pages["office-location.html"]=build_simple("office-location","Office Location","Office Location","office-location.html","Heart Vein & Vascular office location — 2170 W State Road 434, Ste 190, Longwood, FL 32779.")
    pages["resources.html"]=build_resources_hub()
    pages["contact.html"]=build_contact()
    pages["book.html"]=build_book()
    pages["shop.html"]=build_shop()
    # procedure pages
    allproc=HEART+VEIN+VASC+INFO+INTEG
    for t,s in allproc:
        pages[f"p/{s}.html"]=build_procedure(s)
    # resource detail pages
    rdesc={"patient-forms":"New-patient forms for Heart Vein & Vascular — complete your paperwork before your visit.",
     "patient-education":"Patient education from Heart Vein & Vascular — trusted information on your heart, vein and vascular conditions.",
     "prescription-refills":"How to request prescription refills at Heart Vein & Vascular, Longwood FL.",
     "accepted-insurance":"Insurance plans accepted at Heart Vein & Vascular in Longwood, FL.",
     "cancellation-policy":"Heart Vein & Vascular appointment cancellation policy."}
    for t,s,k in RESOURCES:
        if k=="int":
            pages[f"r/{s}.html"]=build_resource(s,t,rdesc.get(s,t))
    # write all
    for path,html_ in pages.items():
        write(path, html_)
    # sitemap + robots
    urls=[k for k in pages.keys()]
    sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        loc=SITE+"/"+("" if u=="index.html" else u)
        pr="1.0" if u=="index.html" else ("0.8" if "/" not in u else "0.6")
        sm+=f"  <url><loc>{loc}</loc><priority>{pr}</priority></url>\n"
    sm+="</urlset>\n"
    write("sitemap.xml", sm)
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print(f"Generated {len(pages)} pages + sitemap.xml + robots.txt")
    print("  procedures:", len(allproc), "| resource pages:", sum(1 for _,_,k in RESOURCES if k=='int'))

if __name__=="__main__":
    main()
