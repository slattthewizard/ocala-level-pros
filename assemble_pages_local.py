#!/usr/bin/env python3
"""Assemble Astro pages from site-copy JSON, driven by a site config.

Usage: python assemble_pages.py <config.json>
Requires: the content workflow has written site-copy/*.json into the repo.
This is the generalized version of the script that built wenatcheewellpros.com,
including all post-audit improvements (call-first CTAs, AJAX form, schema set).
"""
import json, pathlib, sys

sys.stdout.reconfigure(encoding="utf-8")
cfg = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
REPO = pathlib.Path(r"C:\Users\DQA\boise") / cfg["siteSlug"]
COPY = REPO / "site-copy"
PAGES = REPO / "src" / "pages"
SITE = f"https://{cfg['domain']}"
PHONE = cfg["phoneDisplay"]
TEL = f"tel:{cfg['phoneTel']}"

PROVIDER = {
    "@type": ["Plumber", "LocalBusiness"],
    "@id": f"{SITE}/#organization",
    "name": cfg["brand"], "url": SITE,
    "logo": {"@type": "ImageObject", "url": f"{SITE}/images/og-image.webp"},
    "priceRange": "$$",
    "telephone": PHONE, "email": cfg["email"],
    "address": {"@type": "PostalAddress", "addressLocality": cfg["hubCity"],
                "addressRegion": cfg["region"], "addressCountry": cfg["country"]},
    "geo": {"@type": "GeoCoordinates", "latitude": cfg["geo"]["lat"], "longitude": cfg["geo"]["lng"]},
    "areaServed": [{"@type": "City", "name": cfg["hubCity"], "addressRegion": cfg["region"]}] +
                  [{"@type": "City", "name": c["city"], "addressRegion": cfg["region"]} for c in cfg["cities"]],
}

def faq_schema(faq):
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": f["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faq]}, ensure_ascii=False)

def breadcrumb_schema(items):
    return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [{"@type": "ListItem", "position": i+1, "name": n, "item": u}
                            for i, (n, u) in enumerate(items)]}, ensure_ascii=False)

def service_schema(name, desc, url):
    return json.dumps({"@context": "https://schema.org", "@type": "Service",
        "name": name, "description": desc, "url": url, "provider": PROVIDER}, ensure_ascii=False)

def faq_section(faq):
    blocks = "\n".join(
        f'''      <div style="background:#fff;border:1px solid #E4DCC8;border-radius:8px;padding:24px 28px;">
        <h3 style="font-family:'Poppins',sans-serif;font-size:18px;font-weight:800;color:#16332C;margin:0 0 10px;">{f["q"]}</h3>
        <p style="font-size:15px;line-height:1.75;color:#555;margin:0;">{f["a"]}</p>
      </div>''' for f in faq)
    return f'''<section style="padding:72px 24px;background:#F5F0E4;">
  <div style="max-width:860px;margin:0 auto;">
    <span class="kicker">FAQ</span>
    <h2 class="section-heading" style="font-size:clamp(24px,3.5vw,36px);margin:0 0 32px;">Frequently Asked Questions</h2>
    <div style="display:flex;flex-direction:column;gap:16px;">
{blocks}
    </div>
  </div>
</section>'''

def cta_banner(h=None):
    h = h or f"Need Help in {cfg['areaName']}? Call for Same-Day Service."
    return f'''<section style="background:linear-gradient(135deg, #1F6D5A 0%, #2A8570 50%, #1F6D5A 100%);padding:64px 24px;text-align:center;">
  <h2 style="font-family:'Poppins',sans-serif;font-size:clamp(26px,4vw,40px);font-weight:800;color:#fff;margin-bottom:16px;">{h}</h2>
  <p style="font-size:16px;color:rgba(255,255,255,0.8);margin-bottom:28px;max-width:520px;margin-left:auto;margin-right:auto;">Free written estimates. Emergency calls answered around the clock.</p>
  <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;">
    <a href="{TEL}" class="btn-cream">Call Now — {PHONE}</a>
    <a href="/#contact" class="btn-outline-white">Get Free Estimate</a>
  </div>
</section>'''

def hero(h1, sub, img=None, tag=None):
    img_html = f'''
    <div class="hero-img" style="border-radius:12px;overflow:hidden;box-shadow:0 24px 48px rgba(0,0,0,0.3);">
      <img src="/images/{img}.webp" alt="{h1}" width="800" height="533" style="width:100%;height:100%;object-fit:cover;display:block;" loading="eager" fetchpriority="high">
    </div>''' if img else ""
    tag_html = (f'<span style="display:inline-block;margin-bottom:12px;padding:4px 12px;border-radius:999px;font-size:11px;'
                f'font-weight:700;letter-spacing:0.12em;text-transform:uppercase;background:rgba(240,168,96,0.18);'
                f'color:#F0A860;border:1px solid rgba(240,168,96,0.3);">{tag}</span>') if tag else ""
    return f'''<section style="background:linear-gradient(135deg, #175445 0%, #1F6D5A 65%, #175445 100%);padding:72px 24px;">
  <div class="hero-grid" style="max-width:1180px;margin:0 auto;display:grid;grid-template-columns:1.1fr 0.9fr;gap:56px;align-items:center;">
    <div>
      {tag_html}
      <h1 style="font-family:'Poppins',sans-serif;font-weight:800;color:#fff;line-height:1.08;letter-spacing:-0.01em;font-size:clamp(30px,4.4vw,52px);margin:0 0 18px;">{h1}</h1>
      <p style="font-size:18px;line-height:1.7;color:rgba(255,255,255,0.85);max-width:540px;margin:0 0 28px;">{sub}</p>
      <div style="display:flex;flex-wrap:wrap;gap:16px;">
        <a href="{TEL}" class="btn-cream">Call Now — {PHONE}</a>
        <a href="/#contact" class="btn-outline-white">Get a Free Estimate</a>
      </div>
    </div>{img_html}
  </div>
</section>
<style>
  @media (max-width: 860px) {{ .hero-grid {{ grid-template-columns: 1fr !important; }} .hero-img {{ max-height: 320px; }} }}
</style>'''

def sections_html(sections):
    return "\n".join(f'''<section style="padding:0 24px;">
  <div style="max-width:860px;margin:0 auto 56px;">
    <h2 class="section-heading" style="font-size:clamp(22px,3vw,32px);margin:0 0 18px;">{s["heading"]}</h2>
    <div class="rich">{s["html"]}</div>
  </div>
</section>''' for s in sections)

RICH_CSS = '''<style is:global>
  .rich p { font-size: 16px; line-height: 1.8; color: #555; margin: 0 0 16px; }
  .rich ul { padding-left: 20px; margin: 0 0 16px; }
  .rich li { font-size: 16px; line-height: 1.8; color: #555; margin-bottom: 8px; }
  .rich strong { color: #2D3A35; }
  .rich a { color: #1F6D5A; font-weight: 600; text-decoration: none; }
  .rich a:hover { text-decoration: underline; }
</style>'''

def feature_grid(items, cols=3):
    cards = "\n".join(f'''      <div style="background:#fff;border:1px solid #E4DCC8;border-radius:10px;padding:26px;box-shadow:0 2px 8px rgba(22,51,44,0.05);">
        <h3 style="font-family:'Poppins',sans-serif;font-size:18px;font-weight:800;color:#16332C;margin:0 0 8px;">{it["title"]}</h3>
        <p style="font-size:14.5px;line-height:1.7;color:#555;margin:0;">{it["desc"]}</p>
      </div>''' for it in items)
    return f'''<div class="feat-grid" style="display:grid;grid-template-columns:repeat({cols},1fr);gap:20px;">
{cards}
</div>
<style>
  @media (max-width: 860px) {{ .feat-grid {{ grid-template-columns: 1fr !important; }} }}
</style>'''

def head_block(schemas):
    return "<Fragment slot=\"head\">\n" + "\n".join(
        f'<script type="application/ld+json">{s}</script>' for s in schemas) + f"\n{RICH_CSS}\n</Fragment>"

def page_shell(meta_title, meta_desc, url, head, body, rel="../../"):
    return f'''---
import Layout from '{rel}layouts/Layout.astro';
---

<Layout
  title={json.dumps(meta_title, ensure_ascii=False)}
  description={json.dumps(meta_desc, ensure_ascii=False)}
  canonical="{url}"
>
{head}

{body}

</Layout>
'''

def write_page(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"  wrote {path.relative_to(REPO)}")

def breadcrumb_nav(label):
    return f'''<nav aria-label="Breadcrumb" style="max-width:1180px;margin:0 auto;padding:16px 24px;">
  <ol style="list-style:none;padding:0;margin:0;display:flex;gap:8px;font-size:13px;color:#888;">
    <li><a href="/" style="color:#1F6D5A;text-decoration:none;">Home</a></li>
    <li>/</li>
    <li style="color:#2D3A35;">{label}</li>
  </ol>
</nav>'''

def build_service(svc):
    d = json.loads((COPY / f"{svc['slug']}.json").read_text(encoding="utf-8-sig"))
    url = f"{SITE}/{svc['slug']}/"
    head = head_block([
        service_schema(d["h1"], d["metaDescription"], url),
        breadcrumb_schema([("Home", SITE + "/"), (d["h1"], url)]),
        faq_schema(d["faq"]),
    ])
    body = "\n".join([
        breadcrumb_nav(d["h1"]),
        hero(d["h1"], d["heroSub"], svc["img"], tag="Our Services"),
        f'<section style="padding:72px 24px 40px;"><div style="max-width:860px;margin:0 auto;"><div class="rich">{d["introHtml"]}</div></div></section>',
        f'''<section style="padding:0 24px 64px;"><div style="max-width:1100px;margin:0 auto;">
    <span class="kicker">What We Handle</span>
    <h2 class="section-heading" style="font-size:clamp(22px,3vw,32px);margin:0 0 28px;">What's Included in Every Visit</h2>
    {feature_grid(d["features"], 3)}
  </div></section>''',
        sections_html(d["sections"]),
        faq_section(d["faq"]),
        cta_banner(),
    ])
    write_page(PAGES / svc["slug"] / "index.astro", page_shell(d["metaTitle"], d["metaDescription"], url, head, body))

def build_city(ct):
    d = json.loads((COPY / f"{ct['slug']}.json").read_text(encoding="utf-8-sig"))
    url = f"{SITE}/{ct['slug']}/"
    head = head_block([
        service_schema(f"{cfg['nicheShort'].title()} Service in {d['city']}, {cfg['region']}", d["metaDescription"], url),
        breadcrumb_schema([("Home", SITE + "/"), (d["h1"], url)]),
        faq_schema(d["faq"]),
    ])
    body = "\n".join([
        breadcrumb_nav(d["city"]),
        hero(d["h1"], d["heroSub"], ct["img"], tag="Service Area"),
        f'<section style="padding:72px 24px 40px;"><div style="max-width:860px;margin:0 auto;"><div class="rich">{d["introHtml"]}</div></div></section>',
        f'''<section style="padding:0 24px 64px;"><div style="max-width:1100px;margin:0 auto;">
    <span class="kicker">What We Do in {d["city"]}</span>
    <h2 class="section-heading" style="font-size:clamp(22px,3vw,32px);margin:0 0 28px;">Services for {d["city"]} Properties</h2>
    {feature_grid(d["services"], 2)}
  </div></section>''',
        sections_html(d["sections"]),
        faq_section(d["faq"]),
        cta_banner(f"Trouble in {d['city']}? We Can Be On Our Way."),
    ])
    write_page(PAGES / ct["slug"] / "index.astro", page_shell(d["metaTitle"], d["metaDescription"], url, head, body))

def build_home():
    d = json.loads((COPY / "home.json").read_text(encoding="utf-8-sig"))
    url = SITE + "/"
    biz = dict(PROVIDER); biz["@context"] = "https://schema.org"
    biz["description"] = d["metaDescription"]
    biz["image"] = f"{SITE}/images/og-image.webp"
    biz["hasOfferCatalog"] = {"@type": "OfferCatalog", "name": f"{cfg['nicheShort'].title()} Services",
        "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": c["title"]}} for c in d["serviceCards"]]}
    website = {"@context": "https://schema.org", "@type": "WebSite", "@id": f"{SITE}/#website",
               "url": SITE, "name": cfg["brand"], "publisher": {"@id": f"{SITE}/#organization"}}
    head = head_block([json.dumps(biz, ensure_ascii=False), json.dumps(website, ensure_ascii=False), faq_schema(d["faq"])])

    tiles = "\n".join(
        f'''      <a href="{t["href"]}" style="display:flex;flex-direction:column;background:#fff;border-radius:16px;overflow:hidden;text-decoration:none;box-shadow:0 4px 16px rgba(22,51,44,0.1);">
        <img src="/images/{t["img"]}.webp" alt="{t["alt"]}" width="700" height="560" style="width:100%;aspect-ratio:1.25/1;object-fit:cover;display:block;" loading="lazy">
        <span style="font-family:'Poppins',sans-serif;font-size:14.5px;font-weight:800;color:#16332C;padding:14px 12px;">{t["label"]}</span>
      </a>''' for t in d["tiles"])

    svc_cards = "\n".join(
        f'''      <a href="{c["href"]}" style="display:flex;flex-direction:column;background:#fff;border:1px solid #E4DCC8;border-radius:12px;padding:30px 26px;text-decoration:none;box-shadow:0 2px 8px rgba(22,51,44,0.06);">
        <h3 style="font-family:'Poppins',sans-serif;font-size:20px;font-weight:800;color:#16332C;margin:0 0 10px;">{c["title"]}</h3>
        <p style="font-size:14.5px;line-height:1.7;color:#555;margin:0 0 18px;flex:1;">{c["desc"]}</p>
        <span style="font-size:13px;font-weight:700;color:#E07B1F;letter-spacing:0.04em;text-transform:uppercase;">Learn More &#8594;</span>
      </a>''' for c in d["serviceCards"])

    why = "\n".join(
        f'''          <li style="display:flex;gap:14px;align-items:flex-start;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#E07B1F" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:3px;"><polyline points="20 6 9 17 4 12"/></svg>
            <div>
              <p style="font-family:'Poppins',sans-serif;font-size:17px;font-weight:800;color:#16332C;margin:0 0 4px;">{w["title"]}</p>
              <p style="font-size:14.5px;line-height:1.7;color:#5F6E67;margin:0;">{w["desc"]}</p>
            </div>
          </li>''' for w in d["whyUs"])

    steps = "\n".join(
        f'''      <div style="background:#fff;border-radius:16px;padding:34px 26px;box-shadow:0 4px 18px rgba(22,51,44,0.08);">
        <div style="width:54px;height:54px;border-radius:50%;background:#E07B1F;color:#fff;font-family:'Poppins',sans-serif;font-size:22px;font-weight:800;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;">{s["step"]}</div>
        <h3 style="font-family:'Poppins',sans-serif;font-size:18px;font-weight:800;color:#16332C;margin:0 0 10px;">{s["title"]}</h3>
        <p style="font-size:14.5px;line-height:1.7;color:#5F6E67;margin:0;">{s["desc"]}</p>
      </div>''' for s in d["processSteps"])

    faqs = "\n".join(
        f'''      <div style="background:#fff;border-radius:14px;padding:24px 28px;box-shadow:0 3px 12px rgba(22,51,44,0.06);">
        <h3 style="font-family:'Poppins',sans-serif;font-size:17px;font-weight:800;color:#16332C;margin:0 0 10px;">{f["q"]}</h3>
        <p style="font-size:15px;line-height:1.75;color:#5F6E67;margin:0;">{f["a"]}</p>
      </div>''' for f in d["faq"])

    body = f'''<!-- HERO + QUOTE FORM -->
<section id="contact" style="position:relative;overflow:hidden;background:#16332C;">
  <img src="/images/hero-panorama.webp" alt="{cfg['areaName']} manufactured home community" width="2000" height="950" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;" loading="eager" fetchpriority="high">
  <div style="position:absolute;inset:0;background:linear-gradient(100deg, rgba(22,51,44,0.86) 0%, rgba(22,51,44,0.62) 55%, rgba(22,51,44,0.38) 100%);"></div>
  <div class="home-hero-grid" style="position:relative;max-width:1220px;margin:0 auto;padding:64px 24px 72px;display:grid;grid-template-columns:1.05fr 0.95fr;gap:56px;align-items:center;">
    <div>
      <span style="display:inline-block;margin-bottom:18px;padding:7px 18px;border-radius:999px;font-family:'Poppins',sans-serif;font-size:12px;font-weight:600;letter-spacing:0.16em;text-transform:uppercase;background:rgba(255,255,255,0.14);color:#fff;border:1px solid rgba(255,255,255,0.35);backdrop-filter:blur(3px);">Licensed &amp; Insured · {cfg['areaName']}</span>
      <h1 style="font-family:'Poppins',sans-serif;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;color:#fff;line-height:1.3;font-size:clamp(25px,3.4vw,40px);margin:0 0 16px;text-shadow:0 2px 24px rgba(22,51,44,0.45);">{d['heroH1']}</h1>
      <p style="font-size:17px;line-height:1.7;color:rgba(255,255,255,0.92);max-width:560px;margin:0 0 26px;text-shadow:0 1px 12px rgba(22,51,44,0.5);">{d['heroSub']}</p>
      <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:28px;">
        <a href="{TEL}" class="btn-green" style="font-size:15px;padding:16px 34px;">Call Now — {PHONE}</a>
        <a href="/mobile-home-leveling-cost/" class="btn-white-outline" style="font-size:14px;">See Real Price Ranges</a>
      </div>
      <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:10px;">
        <li style="display:flex;align-items:center;gap:10px;color:rgba(255,255,255,0.95);font-size:14.5px;font-weight:600;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F0A860" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>Free written estimates — no pressure, no surprises</li>
        <li style="display:flex;align-items:center;gap:10px;color:rgba(255,255,255,0.95);font-size:14.5px;font-weight:600;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F0A860" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>Insurance tie-down certification letters, fast turnaround</li>
        <li style="display:flex;align-items:center;gap:10px;color:rgba(255,255,255,0.95);font-size:14.5px;font-weight:600;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F0A860" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>Most singlewide relevels done the same day</li>
      </ul>
    </div>
    <div>
      <form id="contact-form" novalidate style="background:#fff;border-radius:14px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 28px 60px rgba(0,0,0,0.35);">
        <p style="background:#1F6D5A;color:#fff;font-family:'Poppins',sans-serif;font-size:15px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;text-align:center;padding:16px 20px;margin:0;">Request a Free Quote Now</p>
        <div style="padding:26px 28px 28px;display:flex;flex-direction:column;gap:13px;">
          <input type="hidden" name="_subject" value="New estimate request — {cfg['domain']}">
          <div style="display:flex;flex-direction:column;gap:4px;">
            <label for="cf-name" style="font-family:'Poppins',sans-serif;font-size:13px;font-weight:600;color:#16332C;">Your name <span aria-hidden="true" style="color:#C0392B;">*</span></label>
            <input id="cf-name" type="text" name="name" autocomplete="name" required style="padding:12px 15px;border:1.5px solid #DDD5C2;border-radius:8px;font-family:inherit;font-size:15px;min-height:46px;">
          </div>
          <div style="display:flex;flex-direction:column;gap:4px;">
            <label for="cf-phone" style="font-family:'Poppins',sans-serif;font-size:13px;font-weight:600;color:#16332C;">Phone number <span aria-hidden="true" style="color:#C0392B;">*</span></label>
            <input id="cf-phone" type="tel" name="phone" autocomplete="tel" inputmode="tel" required style="padding:12px 15px;border:1.5px solid #DDD5C2;border-radius:8px;font-family:inherit;font-size:15px;min-height:46px;">
          </div>
          <div style="display:flex;flex-direction:column;gap:4px;">
            <label for="cf-city" style="font-family:'Poppins',sans-serif;font-size:13px;font-weight:600;color:#16332C;">City or area</label>
            <input id="cf-city" type="text" name="city" autocomplete="address-level2" style="padding:12px 15px;border:1.5px solid #DDD5C2;border-radius:8px;font-family:inherit;font-size:15px;min-height:46px;">
          </div>
          <div style="display:flex;flex-direction:column;gap:4px;">
            <label for="cf-message" style="font-family:'Poppins',sans-serif;font-size:13px;font-weight:600;color:#16332C;">What's going on with your home?</label>
            <textarea id="cf-message" name="message" rows="3" style="padding:12px 15px;border:1.5px solid #DDD5C2;border-radius:8px;font-family:inherit;font-size:15px;resize:vertical;"></textarea>
          </div>
          <button type="submit" id="cf-submit" class="btn-green" style="width:100%;font-size:15px;border-radius:8px;">Get My Free Estimate</button>
          <p style="font-size:12px;color:#8B968E;text-align:center;margin:0;line-height:1.6;">We'll call you back, usually within the hour during business hours.<br><strong style="color:#16332C;">Need someone now? Call <a href="{TEL}" style="color:#1F6D5A;">{PHONE}</a></strong></p>
          <p id="cf-error" role="alert" style="display:none;background:#FFF0F0;border:1px solid #FBBCBC;border-radius:8px;padding:10px 14px;font-size:14px;color:#C0392B;margin:0;"></p>
        </div>
      </form>
      <div id="cf-success" style="display:none;background:#fff;border-radius:14px;padding:40px 32px;box-shadow:0 28px 60px rgba(0,0,0,0.35);text-align:center;">
        <p style="font-family:'Poppins',sans-serif;font-size:21px;font-weight:700;color:#16332C;margin:0 0 10px;">We got your request!</p>
        <p style="font-size:15px;line-height:1.75;color:#5F6E67;margin:0 0 20px;">Expect a call back within the hour during business hours. Need help immediately?</p>
        <a href="{TEL}" class="btn-green">Call {PHONE}</a>
      </div>
    </div>
  </div>
</section>
<style>
  @media (max-width: 900px) {{ .home-hero-grid {{ grid-template-columns: 1fr !important; gap: 40px !important; }} }}
</style>

<!-- TRUST BAND -->
<section style="background:#1F6D5A;padding:30px 24px;">
  <div style="max-width:1220px;margin:0 auto;text-align:center;">
    <p style="font-family:'Poppins',sans-serif;font-size:clamp(17px,2.2vw,23px);font-weight:600;color:#fff;margin:0 0 6px;">Professional Mobile Home Services Across {cfg['areaName']}</p>
    <p style="font-family:'Poppins',sans-serif;font-size:12.5px;font-weight:600;letter-spacing:0.18em;text-transform:uppercase;color:#F0A860;margin:0 0 18px;">Leveling · Tie-Downs &amp; Certifications · Vapor Barriers · Skirting</p>
    <div style="display:flex;justify-content:center;align-items:center;gap:14px 36px;flex-wrap:wrap;color:rgba(255,255,255,0.92);font-size:13.5px;font-weight:600;">
      <span>Serving {cfg['counties']}</span>
      <span style="opacity:0.5;">|</span>
      <span>Licensed &amp; Insured in Florida</span>
      <span style="opacity:0.5;">|</span>
      <a href="{TEL}" style="color:#fff;font-family:'Poppins',sans-serif;font-size:16px;font-weight:700;text-decoration:none;">{PHONE}</a>
    </div>
  </div>
</section>

<!-- INTRO -->
<section style="padding:84px 24px 64px;background:#fff;">
  <div class="intro-grid" style="max-width:1120px;margin:0 auto;display:grid;grid-template-columns:0.9fr 1.1fr;gap:64px;align-items:center;">
    <div style="position:relative;">
      <div style="border-radius:18px;overflow:hidden;box-shadow:0 24px 56px rgba(22,51,44,0.22);aspect-ratio:1/1;">
        <img src="/images/about.webp" alt="{cfg['brand']} service crew" width="1024" height="1024" style="width:100%;height:100%;object-fit:cover;display:block;" loading="lazy">
      </div>
      <div style="position:absolute;bottom:-18px;right:-14px;background:#E07B1F;color:#fff;border-radius:14px;padding:14px 22px;box-shadow:0 10px 26px rgba(224,123,31,0.4);">
        <p style="font-family:'Poppins',sans-serif;font-size:20px;font-weight:800;margin:0;line-height:1;">24/7</p>
        <p style="font-size:11.5px;font-weight:700;margin:4px 0 0;letter-spacing:0.06em;text-transform:uppercase;">Emergency Line</p>
      </div>
    </div>
    <div>
      <span class="kicker">{d.get('introKicker', 'Your Local Crew')}</span>
      <h2 class="section-heading" style="font-size:clamp(26px,3.4vw,40px);margin:0 0 18px;">{d.get('introHeading', 'Your Local Crew')}</h2>
      <div class="rich">{d['aboutBlurb']}</div>
      <a href="/about/" class="btn-blue" style="margin-top:10px;">More About Us</a>
    </div>
  </div>
</section>
<style>
  @media (max-width: 900px) {{ .intro-grid {{ grid-template-columns: 1fr !important; gap: 44px !important; }} }}
</style>

<!-- TILES -->
<section id="services" style="padding:72px 24px 84px;background:#F5F0E4;">
  <div style="max-width:1120px;margin:0 auto;text-align:center;">
    <span class="kicker">Fast Emergency Service Available</span>
    <h2 class="section-heading" style="font-size:clamp(26px,3.4vw,40px);margin:0 0 40px;">{d.get('tilesHeading', "What's Going On at Your Place?")}</h2>
    <div class="tile-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:22px;">
{tiles}
    </div>
  </div>
</section>
<style>
  @media (max-width: 1000px) {{ .tile-grid {{ grid-template-columns: repeat(2,1fr) !important; }} }}
  @media (max-width: 520px) {{ .tile-grid {{ grid-template-columns: 1fr !important; }} }}
</style>

<!-- SERVICE CARDS -->
<section style="padding:0 24px 80px;background:#F5F0E4;">
  <div style="max-width:1100px;margin:0 auto;">
    <div class="svc-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:20px;">
{svc_cards}
    </div>
  </div>
</section>
<style>
  @media (max-width: 1000px) {{ .svc-grid {{ grid-template-columns: repeat(2,1fr) !important; }} }}
  @media (max-width: 600px) {{ .svc-grid {{ grid-template-columns: 1fr !important; }} }}
</style>

<!-- WHY -->
<section style="padding:84px 24px;background:#fff;">
  <div class="why-grid" style="max-width:1120px;margin:0 auto;display:grid;grid-template-columns:1.1fr 0.9fr;gap:64px;align-items:center;">
    <div>
      <span class="kicker">What Makes Us Different</span>
      <h2 class="section-heading" style="font-size:clamp(26px,3.4vw,40px);margin:0 0 28px;">{d.get('whyHeading', "You Know What You're Getting Before We Touch Anything")}</h2>
      <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:20px;">
{why}
      </ul>
    </div>
    <div style="display:flex;flex-direction:column;gap:20px;">
      <div style="border-radius:18px;overflow:hidden;box-shadow:0 18px 44px rgba(22,51,44,0.2);aspect-ratio:4/5;">
        <img src="/images/hero-800.webp" alt="{cfg['brand']} at work" width="800" height="800" style="width:100%;height:100%;object-fit:cover;display:block;" loading="lazy">
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        <div style="background:#1F6D5A;border-radius:14px;padding:24px;text-align:center;">
          <p style="font-family:'Poppins',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:0;line-height:1;">$0</p>
          <p style="font-size:12.5px;font-weight:700;color:rgba(255,255,255,0.85);margin:6px 0 0;letter-spacing:0.05em;text-transform:uppercase;">Estimate Fee</p>
        </div>
        <div style="background:#E07B1F;border-radius:14px;padding:24px;text-align:center;">
          <p style="font-family:'Poppins',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:0;line-height:1;">Same Day</p>
          <p style="font-size:12.5px;font-weight:700;color:rgba(255,255,255,0.85);margin:6px 0 0;letter-spacing:0.05em;text-transform:uppercase;">Most Repairs</p>
        </div>
      </div>
    </div>
  </div>
</section>
<style>
  @media (max-width: 900px) {{ .why-grid {{ grid-template-columns: 1fr !important; gap: 44px !important; }} }}
</style>

<!-- PROCESS -->
<section style="padding:76px 24px;background:#F5F0E4;">
  <div style="max-width:1020px;margin:0 auto;text-align:center;">
    <span class="kicker">How It Works</span>
    <h2 class="section-heading" style="font-size:clamp(26px,3.4vw,38px);margin:0 0 44px;">Three Steps. Most Repairs Done Same Day.</h2>
    <div class="steps-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:32px;">
{steps}
    </div>
  </div>
</section>
<style>
  @media (max-width: 760px) {{ .steps-grid {{ grid-template-columns: 1fr !important; }} }}
</style>

<!-- AREAS -->
<section style="padding:76px 24px 60px;background:#fff;">
  <div style="max-width:860px;margin:0 auto;text-align:center;">
    <span class="kicker">Service Areas</span>
    <h2 class="section-heading" style="font-size:clamp(24px,3vw,36px);margin:0 0 16px;">Serving {cfg['areaName']}</h2>
    <div class="rich" style="text-align:left;">{d['areaBlurb']}</div>
  </div>
</section>

<!-- FAQ -->
<section style="padding:72px 24px;background:#F5F0E4;">
  <div style="max-width:860px;margin:0 auto;">
    <span class="kicker">FAQ</span>
    <h2 class="section-heading" style="font-size:clamp(24px,3.5vw,36px);margin:0 0 32px;">Frequently Asked Questions</h2>
    <div style="display:flex;flex-direction:column;gap:16px;">
{faqs}
    </div>
  </div>
</section>

<!-- CALL BAND -->
<section style="position:relative;padding:84px 24px;overflow:hidden;">
  <img src="/images/city-1.webp" alt="" width="1600" height="900" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;" loading="lazy" aria-hidden="true">
  <div style="position:absolute;inset:0;background:linear-gradient(135deg, rgba(22,51,44,0.93) 0%, rgba(31,109,90,0.88) 100%);"></div>
  <div style="position:relative;max-width:780px;margin:0 auto;text-align:center;">
    <span class="kicker" style="color:#F0A860;">Free Estimate</span>
    <h2 style="font-family:'Poppins',sans-serif;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:#fff;font-size:clamp(22px,3.2vw,34px);line-height:1.3;margin:0 0 16px;">Describe the Problem. We'll Call Back With a Price.</h2>
    <p style="font-size:16px;line-height:1.8;color:rgba(255,255,255,0.88);margin:0 0 28px;">{d.get('contactBlurb', "You'll see your options in writing before deciding anything. Need help right now? Skip the form and call.")}</p>
    <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;">
      <a href="{TEL}" class="btn-green">Call {PHONE}</a>
      <a href="/#contact" class="btn-white-outline">Request a Free Quote</a>
    </div>
  </div>
</section>
<script>
(function(){{
  var form = document.getElementById('contact-form');
  var success = document.getElementById('cf-success');
  var errBox = document.getElementById('cf-error');
  var submitBtn = document.getElementById('cf-submit');
  if (!form) return;
  form.addEventListener('submit', function(e) {{
    e.preventDefault();
    errBox.style.display = 'none';
    submitBtn.disabled = true; submitBtn.textContent = 'Sending…';
    fetch('{cfg.get("formspreeEndpoint", "https://formspree.io/f/REPLACE_ME")}', {{
      method: 'POST', body: new FormData(form), headers: {{ 'Accept': 'application/json' }}
    }})
    .then(function(r){{ return r.json().then(function(d){{ return {{ok: r.ok, data: d}}; }}); }})
    .then(function(res){{
      if (res.ok) {{ form.style.display = 'none'; success.style.display = 'block'; }}
      else {{
        errBox.textContent = 'Something went wrong. Please try again or call us directly.';
        errBox.style.display = 'block';
        submitBtn.disabled = false; submitBtn.textContent = 'Get My Free Estimate';
      }}
    }})
    .catch(function(){{
      errBox.textContent = 'Could not send. Please call us at {PHONE}.';
      errBox.style.display = 'block';
      submitBtn.disabled = false; submitBtn.textContent = 'Get My Free Estimate';
    }});
  }});
}})();
</script>'''
    write_page(PAGES / "index.astro", page_shell(d["metaTitle"], d["metaDescription"], url, head, body, rel="../"))

def build_about():
    d = json.loads((COPY / "about.json").read_text(encoding="utf-8-sig"))
    url = f"{SITE}/about/"
    head = head_block([breadcrumb_schema([("Home", SITE + "/"), ("About", url)]), faq_schema(d["faq"])])
    body = "\n".join([
        hero(d["h1"], d["heroSub"], "about", tag="About Us"),
        f'<section style="padding:72px 24px 40px;"><div style="max-width:860px;margin:0 auto;"><div class="rich">{d["storyHtml"]}</div></div></section>',
        f'''<section style="padding:0 24px 64px;"><div style="max-width:1100px;margin:0 auto;">
    <span class="kicker">How We Work</span>
    <h2 class="section-heading" style="font-size:clamp(22px,3vw,32px);margin:0 0 28px;">What You Can Expect</h2>
    {feature_grid(d["values"], 2)}
  </div></section>''',
        faq_section(d["faq"]),
        cta_banner(),
    ])
    write_page(PAGES / "about" / "index.astro", page_shell(d["metaTitle"], d["metaDescription"], url, head, body))

def build_cost():
    d = json.loads((COPY / "cost.json").read_text(encoding="utf-8-sig"))
    slug = cfg["costPage"]["slug"]
    url = f"{SITE}/{slug}/"
    head = head_block([breadcrumb_schema([("Home", SITE + "/"), (cfg["costPage"]["title"], url)]), faq_schema(d["faq"])])
    rows = "\n".join(
        f'''        <tr>
          <td style="padding:13px 16px;border-bottom:1px solid #E4DCC8;color:#2D3A35;font-weight:500;">{r["item"]}</td>
          <td style="padding:13px 16px;border-bottom:1px solid #E4DCC8;color:#16332C;font-weight:700;white-space:nowrap;">{r["range"]}</td>
          <td style="padding:13px 16px;border-bottom:1px solid #E4DCC8;color:#555;">{r["note"]}</td>
        </tr>''' for r in d["costTable"])
    body = "\n".join([
        breadcrumb_nav(cfg["costPage"]["title"]),
        hero(d["h1"], d["heroSub"], "service-2", tag="Cost Guide"),
        f'<section style="padding:72px 24px 40px;"><div style="max-width:860px;margin:0 auto;"><div class="rich">{d["introHtml"]}</div></div></section>',
        f'''<section style="padding:0 24px 56px;"><div style="max-width:920px;margin:0 auto;">
    <h2 class="section-heading" style="font-size:clamp(22px,3vw,32px);margin:0 0 22px;">2026 Price Ranges</h2>
    <div style="overflow-x:auto;border:1px solid #E4DCC8;border-radius:10px;">
      <table style="width:100%;border-collapse:collapse;font-size:15px;min-width:560px;">
        <thead><tr>
          <th style="background:#16332C;color:#fff;padding:13px 16px;text-align:left;font-weight:700;">Service</th>
          <th style="background:#16332C;color:#fff;padding:13px 16px;text-align:left;font-weight:700;">Typical Range</th>
          <th style="background:#16332C;color:#fff;padding:13px 16px;text-align:left;font-weight:700;">Notes</th>
        </tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
    <p style="font-size:13px;color:#888;margin-top:12px;">Ranges reflect typical {cfg['areaName']} jobs. Your written estimate is based on your property, not averages.</p>
  </div></section>''',
        sections_html(d["sections"]),
        faq_section(d["faq"]),
        cta_banner("Want a Real Number Instead of a Range?"),
    ])
    write_page(PAGES / slug / "index.astro", page_shell(d["metaTitle"], d["metaDescription"], url, head, body))

def main():
    failed = []
    builders = [("home", build_home), ("about", build_about), ("cost", build_cost)]
    builders += [(s["slug"], (lambda sv: (lambda: build_service(sv)))(s)) for s in cfg["services"]]
    builders += [(c["slug"], (lambda ci: (lambda: build_city(ci)))(c)) for c in cfg["cities"]]
    for name, fn in builders:
        try:
            fn()
        except Exception as e:
            failed.append((name, str(e)))
    if failed:
        print("\nFAILED:")
        for n, e in failed: print(f"  {n}: {e}")
        sys.exit(1)
    print("\nAll pages assembled.")

if __name__ == "__main__":
    main()
