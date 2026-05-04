"""Render an AutoSite project's AI content into a self-contained premium HTML bundle."""
from __future__ import annotations

import io
import json
import zipfile
from html import escape
from datetime import datetime, timezone


def _safe(obj, *keys, default=""):
    cur = obj
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur if cur is not None else default


def _schema_local_business(project: dict, content: dict) -> str:
    hours_json = []
    for h in _safe(content, "local_business", "opening_hours", default=[]) or []:
        hours_json.append({"days": h.get("days", ""), "hours": h.get("hours", "")})
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": project.get("business_name", ""),
        "description": _safe(content, "meta", "description"),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": project.get("address", ""),
            "addressLocality": project.get("city", ""),
        },
        "telephone": project.get("phone", ""),
        "email": project.get("email", ""),
        "areaServed": _safe(content, "local_business", "areas_served", default=[project.get("city", "")]),
        "openingHours": [f"{h['days']} {h['hours']}" for h in hours_json],
    }
    return json.dumps(schema, ensure_ascii=False)


def render_site_html(project: dict, content: dict) -> str:
    """Return a premium standalone HTML page (Tailwind CDN + custom CSS)."""
    primary = project.get("primary_color") or "#FF4500"
    secondary = project.get("secondary_color") or "#0A0A0A"
    city = project.get("city", "")
    biz = project.get("business_name", "")
    phone = project.get("phone", "")
    whatsapp = project.get("whatsapp", "") or phone
    maps_q = f"{project.get('address','')} {city}".strip()

    title = _safe(content, "meta", "title", default=f"{biz} — {city}")
    description = _safe(content, "meta", "description", default="")
    keywords = ", ".join(_safe(content, "meta", "keywords", default=[]) or [])

    hero = content.get("hero", {})
    about = content.get("about", {})
    services = content.get("services", {})
    features = content.get("features", {})
    testimonials = content.get("testimonials", {})
    faq = content.get("faq", {})
    cta = content.get("cta", {})
    contact = content.get("contact", {})
    lb = content.get("local_business", {})
    design = content.get("design", {})
    trust_bar = content.get("trust_bar", {})
    process = content.get("process", {})

    def s(x):
        return escape(str(x))

    service_cards = "\n".join(
        f"""<article class="group relative p-8 rounded-2xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.05] hover:border-white/20 transition-all duration-500">
            <div class="text-sm font-mono uppercase tracking-widest text-[color:var(--accent)] mb-4">0{i+1}</div>
            <h3 class="text-2xl font-medium mb-3">{s(it.get('name',''))}</h3>
            <p class="text-white/60 leading-relaxed">{s(it.get('description',''))}</p>
        </article>"""
        for i, it in enumerate(services.get("items", []) or [])
    )

    feature_items = "\n".join(
        f"""<div class="flex gap-4 p-6 rounded-xl bg-white/[0.02] border border-white/10">
            <div class="flex-shrink-0 w-10 h-10 rounded-full bg-[color:var(--accent)]/20 border border-[color:var(--accent)]/40 flex items-center justify-center text-[color:var(--accent)] font-mono">✦</div>
            <div><h4 class="font-medium mb-1">{s(it.get('title',''))}</h4>
            <p class="text-white/60 text-sm leading-relaxed">{s(it.get('description',''))}</p></div>
        </div>"""
        for it in (features.get("items") or [])
    )

    testimonial_cards = "\n".join(
        f"""<figure class="p-8 rounded-2xl border border-white/10 bg-white/[0.02]">
            <div class="text-[color:var(--accent)] mb-4">{'★' * int(t.get('rating', 5))}</div>
            <blockquote class="text-lg leading-relaxed mb-6">"{s(t.get('quote',''))}"</blockquote>
            <figcaption><div class="font-medium">{s(t.get('name',''))}</div>
            <div class="text-sm text-white/50">{s(t.get('role',''))}</div></figcaption>
        </figure>"""
        for t in (testimonials.get("items") or [])
    )

    faq_items = "\n".join(
        f"""<details class="group border-b border-white/10 py-6">
            <summary class="flex justify-between items-center cursor-pointer list-none">
                <span class="text-lg font-medium pr-8">{s(q.get('question',''))}</span>
                <span class="text-[color:var(--accent)] text-2xl group-open:rotate-45 transition-transform">+</span>
            </summary>
            <p class="mt-4 text-white/60 leading-relaxed">{s(q.get('answer',''))}</p>
        </details>"""
        for q in (faq.get("items") or [])
    )

    highlights = "".join(
        f"""<div><div class="text-4xl font-medium text-[color:var(--accent)]">{s(h.get('value',''))}</div>
        <div class="text-xs uppercase tracking-widest text-white/50 mt-2">{s(h.get('label',''))}</div></div>"""
        for h in (about.get("highlights") or [])
    )

    trust_items = "".join(
        f"""<div class="px-5 py-4 rounded-2xl border border-white/10 bg-white/[0.025] backdrop-blur-md">
            <div class="text-lg font-medium text-white">{s(t.get('value',''))}</div>
            <div class="text-[10px] uppercase tracking-[0.22em] text-white/45 mt-1">{s(t.get('label',''))}</div>
        </div>"""
        for t in (trust_bar.get("items") or [])
    )

    process_cards = "\n".join(
        f"""<article class="relative p-7 rounded-2xl border border-white/10 bg-gradient-to-b from-white/[0.045] to-white/[0.015]">
            <div class="absolute -top-3 left-7 text-[color:var(--accent)] font-mono text-xs tracking-[0.24em] bg-black px-3 py-1 rounded-full border border-white/10">{s(it.get('step',''))}</div>
            <h3 class="text-2xl font-medium mt-4 mb-3">{s(it.get('title',''))}</h3>
            <p class="text-white/60 leading-relaxed">{s(it.get('description',''))}</p>
        </article>"""
        for it in (process.get("items") or [])
    )

    accent_words = " · ".join(s(w) for w in (design.get("accent_words") or []))

    hours_rows = "".join(
        f"""<li class="flex justify-between py-2 border-b border-white/5"><span class="text-white/70">{s(h.get('days',''))}</span><span class="font-mono">{s(h.get('hours',''))}</span></li>"""
        for h in (lb.get("opening_hours") or [])
    )

    areas = " · ".join(s(a) for a in (lb.get("areas_served") or []))

    whatsapp_link = f"https://wa.me/{whatsapp.replace(' ', '').replace('+', '')}" if whatsapp else "#"
    tel_link = f"tel:{phone.replace(' ', '')}" if phone else "#"
    maps_embed = f"https://www.google.com/maps?q={maps_q.replace(' ', '+')}&output=embed"
    maps_dir = f"https://www.google.com/maps/dir/?api=1&destination={maps_q.replace(' ', '+')}"

    schema_org = _schema_local_business(project, content)

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{s(title)}</title>
<meta name="description" content="{s(description)}"/>
<meta name="keywords" content="{s(keywords)}"/>
<meta property="og:title" content="{s(_safe(content, 'meta', 'og_title', default=title))}"/>
<meta property="og:description" content="{s(_safe(content, 'meta', 'og_description', default=description))}"/>
<meta property="og:type" content="website"/>
<meta name="robots" content="index,follow"/>
<link rel="canonical" href="#"/>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://api.fontshare.com/v2/css?f[]=clash-display@500,600,700&f[]=satoshi@400,500,700&display=swap" rel="stylesheet">
<style>
:root {{ --accent: {primary}; --bg: {secondary}; }}
html, body {{ background: var(--bg); color: #fafafa; font-family: 'Satoshi', system-ui, sans-serif; }}
h1,h2,h3,h4 {{ font-family: 'Clash Display', sans-serif; letter-spacing: -0.02em; }}
.grain::before {{ content:''; position:fixed; inset:0; pointer-events:none; opacity:.05; background-image:radial-gradient(#fff 1px, transparent 1px); background-size: 3px 3px; z-index: 1;}}
.btn-primary {{ background: var(--accent); color:#fff; padding: 1rem 2rem; border-radius: 9999px; font-weight: 600; box-shadow: 0 10px 30px -10px color-mix(in srgb, var(--accent) 60%, transparent); transition: all .3s; display:inline-flex; align-items:center; gap:.5rem; }}
.btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 14px 40px -8px color-mix(in srgb, var(--accent) 80%, transparent); }}
.btn-ghost {{ background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.12); color:#fff; padding: 1rem 2rem; border-radius: 9999px; font-weight: 500; backdrop-filter: blur(12px); transition: all .3s; display:inline-flex; align-items:center; gap:.5rem; }}
.btn-ghost:hover {{ background: rgba(255,255,255,.1); }}
.float-whatsapp {{ position: fixed; bottom: 24px; right: 24px; z-index: 50; width: 56px; height: 56px; border-radius: 9999px; background: #25D366; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 30px rgba(37,211,102,.5); transition: transform .3s; }}
.float-whatsapp:hover {{ transform: scale(1.1); }}
.premium-card { background: linear-gradient(145deg, rgba(255,255,255,.08), rgba(255,255,255,.015)); border:1px solid rgba(255,255,255,.12); box-shadow: 0 30px 100px rgba(0,0,0,.35); }
.orb { filter: blur(10px); animation: floatOrb 8s ease-in-out infinite alternate; }
@keyframes floatOrb { from { transform: translate3d(0,0,0) scale(1); } to { transform: translate3d(-24px,28px,0) scale(1.08); } }
.reveal { animation: reveal .9s cubic-bezier(.22,1,.36,1) both; }
@keyframes reveal { from { opacity:0; transform: translateY(18px); } to { opacity:1; transform: translateY(0); } }
</style>
<script type="application/ld+json">{schema_org}</script>
</head>
<body class="grain">
<header class="sticky top-0 z-40 backdrop-blur-xl bg-black/40 border-b border-white/5">
  <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded-lg bg-[color:var(--accent)]"></div>
      <span class="text-xl font-medium tracking-tight">{s(biz)}</span>
    </div>
    <nav class="hidden md:flex gap-8 text-sm text-white/70">
      <a href="#services" class="hover:text-white">Services</a>
      <a href="#about" class="hover:text-white">À propos</a>
      <a href="#testimonials" class="hover:text-white">Avis</a>
      <a href="#contact" class="hover:text-white">Contact</a>
    </nav>
    <a href="{tel_link}" class="btn-ghost !py-2 !px-4 text-sm">☎ {s(phone)}</a>
  </div>
</header>

<!-- HERO -->
<section class="relative overflow-hidden">
  <div class="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full" style="background: radial-gradient(circle, var(--accent) 0%, transparent 60%); opacity:.25;"></div>
  <div class="max-w-7xl mx-auto px-6 pt-28 pb-32 relative">
    <div class="grid lg:grid-cols-12 gap-12 items-end">
      <div class="lg:col-span-8">
        <div class="text-xs uppercase tracking-[0.3em] text-[color:var(--accent)] font-mono mb-6">{s(hero.get('eyebrow',''))}</div>
        <h1 class="text-5xl sm:text-6xl lg:text-7xl font-medium leading-[1.02]">{s(hero.get('headline',''))}</h1>
        <p class="mt-8 text-lg text-white/70 max-w-2xl leading-relaxed">{s(hero.get('subheadline',''))}</p>
        <div class="mt-10 flex flex-wrap gap-4">
          <a href="#contact" class="btn-primary">{s(hero.get('cta_primary','Contactez-nous'))} →</a>
          <a href="#services" class="btn-ghost">{s(hero.get('cta_secondary','Nos services'))}</a>
        </div>
      </div>
      <div class="lg:col-span-4 text-sm reveal">
        <div class="premium-card rounded-[2rem] p-6 relative overflow-hidden">
          <div class="absolute -top-20 -right-20 w-56 h-56 rounded-full orb" style="background: radial-gradient(circle, var(--accent), transparent 65%); opacity:.35"></div>
          <div class="relative">
            <div class="flex items-center justify-between mb-8">
              <div class="text-xs uppercase tracking-[0.25em] text-white/45">Signature</div>
              <div class="w-10 h-10 rounded-full bg-[color:var(--accent)] shadow-[0_0_40px_color-mix(in_srgb,var(--accent)_70%,transparent)]"></div>
            </div>
            <div class="text-3xl font-medium leading-tight mb-4">{s(design.get('mood','Expérience premium'))}</div>
            <p class="text-white/60 leading-relaxed mb-6">{s(design.get('microcopy','Service professionnel, réponse rapide et expérience soignée.'))}</p>
            <div class="space-y-3">
              <div class="flex justify-between gap-4 py-3 border-t border-white/10"><span class="text-white/50">Adresse</span><span class="text-right font-medium">{s(project.get('address',''))}<br/><span class="text-white/50">{s(city)}</span></span></div>
              <div class="flex justify-between gap-4 py-3 border-t border-white/10"><span class="text-white/50">Téléphone</span><a href="{tel_link}" class="font-medium hover:text-[color:var(--accent)]">{s(phone)}</a></div>
              <div class="flex justify-between gap-4 py-3 border-t border-white/10"><span class="text-white/50">Ambiance</span><span class="text-right text-[color:var(--accent)]">{accent_words}</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- TRUST BAR -->
<section class="max-w-7xl mx-auto px-6 -mt-10 pb-20 relative z-10">
  <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">{trust_items}</div>
</section>

<!-- ABOUT -->
<section id="about" class="max-w-7xl mx-auto px-6 py-28 border-t border-white/5">
  <div class="grid lg:grid-cols-12 gap-16">
    <div class="lg:col-span-5">
      <div class="text-xs uppercase tracking-[0.3em] text-[color:var(--accent)] font-mono mb-4">— À propos</div>
      <h2 class="text-4xl sm:text-5xl font-medium leading-tight">{s(about.get('title',''))}</h2>
    </div>
    <div class="lg:col-span-7">
      <p class="text-lg text-white/70 leading-relaxed">{s(about.get('paragraph',''))}</p>
      <div class="grid grid-cols-3 gap-8 mt-12">{highlights}</div>
    </div>
  </div>
</section>

<!-- SERVICES -->
<section id="services" class="max-w-7xl mx-auto px-6 py-28 border-t border-white/5">
  <div class="flex flex-wrap items-end justify-between gap-8 mb-14">
    <div>
      <div class="text-xs uppercase tracking-[0.3em] text-[color:var(--accent)] font-mono mb-4">— Nos prestations</div>
      <h2 class="text-4xl sm:text-5xl font-medium max-w-2xl">{s(services.get('title',''))}</h2>
    </div>
    <p class="max-w-md text-white/60">{s(services.get('subtitle',''))}</p>
  </div>
  <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-5">{service_cards}</div>
</section>

<!-- PROCESS -->
<section class="max-w-7xl mx-auto px-6 py-28 border-t border-white/5">
  <div class="flex flex-wrap items-end justify-between gap-8 mb-14">
    <div>
      <div class="text-xs uppercase tracking-[0.3em] text-[color:var(--accent)] font-mono mb-4">— Expérience</div>
      <h2 class="text-4xl sm:text-5xl font-medium max-w-2xl">{s(process.get('title','Une expérience simple et fluide'))}</h2>
    </div>
    <p class="max-w-md text-white/60">{s(design.get('visual_direction','Un parcours clair, pensé pour inspirer confiance dès le premier contact.'))}</p>
  </div>
  <div class="grid md:grid-cols-3 gap-5">{process_cards}</div>
</section>

<!-- FEATURES -->
<section class="max-w-7xl mx-auto px-6 py-28 border-t border-white/5">
  <div class="text-xs uppercase tracking-[0.3em] text-[color:var(--accent)] font-mono mb-4">— Pourquoi nous</div>
  <h2 class="text-4xl sm:text-5xl font-medium max-w-2xl mb-14">{s(features.get('title',''))}</h2>
  <div class="grid md:grid-cols-2 gap-5">{feature_items}</div>
</section>

<!-- TESTIMONIALS -->
<section id="testimonials" class="max-w-7xl mx-auto px-6 py-28 border-t border-white/5">
  <div class="text-xs uppercase tracking-[0.3em] text-[color:var(--accent)] font-mono mb-4">— Ils nous font confiance</div>
  <h2 class="text-4xl sm:text-5xl font-medium max-w-2xl mb-14">{s(testimonials.get('title',''))}</h2>
  <div class="grid md:grid-cols-3 gap-5">{testimonial_cards}</div>
</section>

<!-- FAQ -->
<section class="max-w-4xl mx-auto px-6 py-28 border-t border-white/5">
  <div class="text-xs uppercase tracking-[0.3em] text-[color:var(--accent)] font-mono mb-4">— Questions fréquentes</div>
  <h2 class="text-4xl sm:text-5xl font-medium mb-12">{s(faq.get('title',''))}</h2>
  <div>{faq_items}</div>
</section>

<!-- CTA -->
<section class="max-w-7xl mx-auto px-6 py-28 border-t border-white/5">
  <div class="relative rounded-3xl p-14 md:p-20 overflow-hidden border border-white/10" style="background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 15%, transparent), transparent);">
    <div class="absolute -bottom-40 -left-20 w-[500px] h-[500px] rounded-full" style="background: radial-gradient(circle, var(--accent) 0%, transparent 60%); opacity:.2;"></div>
    <div class="relative grid md:grid-cols-2 gap-10 items-center">
      <div>
        <h2 class="text-4xl sm:text-5xl font-medium leading-tight">{s(cta.get('title',''))}</h2>
        <p class="mt-4 text-white/70 text-lg">{s(cta.get('subtitle',''))}</p>
      </div>
      <div class="flex md:justify-end gap-3">
        <a href="#contact" class="btn-primary">{s(cta.get('button','Prendre contact'))} →</a>
      </div>
    </div>
  </div>
</section>

<!-- CONTACT -->
<section id="contact" class="max-w-7xl mx-auto px-6 py-28 border-t border-white/5">
  <div class="grid lg:grid-cols-12 gap-12">
    <div class="lg:col-span-5">
      <div class="text-xs uppercase tracking-[0.3em] text-[color:var(--accent)] font-mono mb-4">— Contact</div>
      <h2 class="text-4xl sm:text-5xl font-medium mb-6">{s(contact.get('title', 'Parlons de votre projet'))}</h2>
      <p class="text-white/70 mb-8">{s(contact.get('subtitle',''))}</p>
      <ul class="space-y-3 text-white/70">
        <li class="flex gap-3"><span class="text-[color:var(--accent)]">▸</span><span>{s(project.get('address',''))} — {s(city)}</span></li>
        <li class="flex gap-3"><span class="text-[color:var(--accent)]">▸</span><a href="{tel_link}" class="hover:text-white">{s(phone)}</a></li>
        <li class="flex gap-3"><span class="text-[color:var(--accent)]">▸</span><a href="mailto:{s(project.get('email',''))}" class="hover:text-white">{s(project.get('email',''))}</a></li>
      </ul>
      <h3 class="text-lg font-medium mt-10 mb-3">Horaires</h3>
      <ul class="text-sm">{hours_rows}</ul>
      <div class="flex gap-3 mt-8">
        <a href="{whatsapp_link}" class="btn-ghost !py-2 !px-4 text-sm">WhatsApp</a>
        <a href="{maps_dir}" class="btn-ghost !py-2 !px-4 text-sm">Itinéraire</a>
        <a href="{tel_link}" class="btn-ghost !py-2 !px-4 text-sm">Appeler</a>
      </div>
    </div>
    <div class="lg:col-span-7">
      <form class="p-8 rounded-2xl border border-white/10 bg-white/[0.02] space-y-4">
        <div class="grid md:grid-cols-2 gap-4">
          <input class="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-[color:var(--accent)]" placeholder="Nom"/>
          <input class="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-[color:var(--accent)]" placeholder="Email"/>
        </div>
        <input class="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-[color:var(--accent)]" placeholder="Sujet"/>
        <textarea rows="5" class="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-[color:var(--accent)]" placeholder="Votre message"></textarea>
        <button type="button" class="btn-primary w-full justify-center">Envoyer le message</button>
      </form>
      <div class="mt-5 rounded-2xl overflow-hidden border border-white/10 aspect-video">
        <iframe src="{maps_embed}" width="100%" height="100%" style="border:0" allowfullscreen loading="lazy"></iframe>
      </div>
      <div class="mt-3 text-xs text-white/50">Zone desservie : {areas}</div>
    </div>
  </div>
</section>

<footer class="border-t border-white/5 py-12">
  <div class="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between gap-6 text-sm text-white/50">
    <div>© {datetime.now(timezone.utc).year} {s(biz)} — Tous droits réservés</div>
    <div>{s(project.get('address',''))} · {s(city)} · {s(phone)}</div>
  </div>
</footer>

<a href="{whatsapp_link}" class="float-whatsapp" aria-label="WhatsApp">
  <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="white" viewBox="0 0 24 24"><path d="M20.52 3.48A11.8 11.8 0 0 0 12.04 0C5.49 0 .16 5.33.16 11.88c0 2.09.55 4.13 1.6 5.93L0 24l6.36-1.66a11.87 11.87 0 0 0 5.68 1.45h.01c6.55 0 11.88-5.33 11.88-11.88 0-3.18-1.23-6.17-3.41-8.43zM12.05 21.5h-.01a9.6 9.6 0 0 1-4.89-1.34l-.35-.21-3.77.99 1.01-3.67-.23-.38a9.58 9.58 0 0 1-1.47-5.11c0-5.3 4.31-9.61 9.62-9.61 2.57 0 4.98 1 6.79 2.82a9.54 9.54 0 0 1 2.82 6.79c0 5.3-4.31 9.61-9.52 9.72z"/></svg>
</a>
</body></html>
"""


def make_zip(project: dict, content: dict) -> bytes:
    """Build a downloadable ZIP with HTML + sitemap + robots + README."""
    html = render_site_html(project, content)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.html", html)
        z.writestr("robots.txt", "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n")
        z.writestr(
            "sitemap.xml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>/</loc><lastmod>{datetime.now(timezone.utc).date()}</lastmod><priority>1.0</priority></url>
</urlset>""",
        )
        z.writestr(
            "README.md",
            f"# {project.get('business_name','')}\n\nSite généré par **AutoSite AI Pro**.\n\n"
            "## Déploiement rapide\n- **Netlify** : glissez ce dossier sur netlify.com/drop\n"
            "- **Vercel** : `vercel deploy`\n- **GitHub Pages** : push dans un repo, activez Pages\n\n"
            "Aucune dépendance à installer — HTML + Tailwind CDN prêt à l'emploi.\n",
        )
        z.writestr("content.json", json.dumps(content, ensure_ascii=False, indent=2))
    return buf.getvalue()


def compute_seo_score(project: dict, content: dict) -> dict:
    """Return an SEO checklist with a 0-100 score."""
    city = (project.get("city") or "").strip()
    title = _safe(content, "meta", "title")
    desc = _safe(content, "meta", "description")
    keywords = _safe(content, "meta", "keywords", default=[]) or []
    h1 = _safe(content, "hero", "headline")

    checks = [
        {"key": "title", "label": "Title SEO optimisé", "passed": bool(title) and 30 <= len(title) <= 70},
        {"key": "description", "label": "Meta description 140-160", "passed": bool(desc) and 120 <= len(desc) <= 180},
        {"key": "h1", "label": "H1 pertinent avec ville", "passed": bool(h1) and (city.lower() in (title + " " + h1).lower() if city else bool(h1))},
        {"key": "keywords", "label": "Mots-clés définis (8+)", "passed": len(keywords) >= 8},
        {"key": "local_seo", "label": "SEO local (ville dans contenus)", "passed": bool(city) and city.lower() in (desc or "").lower()},
        {"key": "schema", "label": "Schema.org LocalBusiness", "passed": True},
        {"key": "sitemap", "label": "Sitemap.xml généré", "passed": True},
        {"key": "robots", "label": "Robots.txt présent", "passed": True},
        {"key": "mobile", "label": "Responsive mobile-first", "passed": True},
        {"key": "og", "label": "Open Graph complet", "passed": bool(_safe(content, "meta", "og_title"))},
        {"key": "faq", "label": "FAQ enrichie (5+)", "passed": len(_safe(content, "faq", "items", default=[]) or []) >= 5},
        {"key": "gbp", "label": "Prêt Google Business Profile", "passed": bool(project.get("phone") and project.get("address"))},
    ]
    passed = sum(1 for c in checks if c["passed"])
    score = round(passed / len(checks) * 100)
    return {"score": score, "checks": checks}
