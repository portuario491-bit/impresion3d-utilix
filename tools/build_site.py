#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py — genera todo el sitio Guía3D a partir de datos/productos.json.

No se escribe HTML de producto a mano: este script produce el home, las
páginas de categoría, una ficha por producto, el comparador, la guía de
compra, ofertas y lib/db.js. Volver a ejecutar tras cualquier cambio en
datos/productos.json.

Uso:  python3 tools/build_site.py
"""
import json
import os
import html
import datetime
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS_PATH = os.path.join(ROOT, "datos", "productos.json")
VER = datetime.date.today().strftime("%Y%m%d")
SITE_URL = "https://impresion3d.utilix.uno"
ADSENSE_TAG = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2829981614170975" crossorigin="anonymous"></script>'

with open(DATOS_PATH, encoding="utf-8") as f:
    PRODUCTOS = json.load(f)

NICHOS = ["impresora", "filamento", "accesorio"]
NICHO_LABEL = {"impresora": "Impresoras 3D", "filamento": "Filamento", "accesorio": "Accesorios"}
NICHO_LABEL_SING = {"impresora": "impresora", "filamento": "filamento", "accesorio": "accesorio"}
NICHO_SLUG_PAGE = {"impresora": "categoria-impresoras.html", "filamento": "categoria-filamento.html", "accesorio": "categoria-accesorios.html"}

ICONS_SVG = {
    "impresora": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9V3h12v6"/><rect x="5" y="13" width="14" height="8" rx="1"/><path d="M6 9H4a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2M18 9h2a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1h-2"/><circle cx="16.5" cy="11.5" r=".5" fill="currentColor"/></svg>',
    "filamento": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5.5" rx="6.5" ry="2.5"/><ellipse cx="12" cy="18.5" rx="6.5" ry="2.5"/><path d="M5.5 5.5v13M18.5 5.5v13"/><path d="M9 6c0 2.5 6 2.5 6 5.5S9 14.5 9 17"/></svg>',
    "accesorio": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="8.5" width="19" height="11" rx="1.5"/><path d="M8 8.5V6.5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M2.5 13h19M10.5 13v2M13.5 13v2"/></svg>',
    "comparador": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18M4.5 21h15"/><path d="M2.5 7h6M15.5 7h6"/><path d="M5.5 7l-3 6a3.2 3.2 0 0 0 6 0z"/><path d="M18.5 7l-3 6a3.2 3.2 0 0 0 6 0z"/></svg>',
    "ofertas": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20.4 12.9 11.6 4.1a2 2 0 0 0-1.4-.6H5a1 1 0 0 0-1 1v5.2c0 .5.2 1 .6 1.4l8.8 8.8a2 2 0 0 0 2.8 0l4.2-4.2a2 2 0 0 0 0-2.8Z"/><circle cx="8" cy="8" r="1.1" fill="currentColor" stroke="none"/></svg>',
    "paquete": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8 12 3 3 8l9 5 9-5Z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/></svg>',
    "escudo": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/></svg>',
}


def icon_svg(name, cls=""):
    svg = ICONS_SVG.get(name, ICONS_SVG["paquete"])
    return svg.replace("<svg ", f'<svg class="{cls}" ', 1) if cls else svg


NICHO_ICON = {"impresora": ICONS_SVG["impresora"], "filamento": ICONS_SVG["filamento"], "accesorio": ICONS_SVG["accesorio"]}

SCORE_AXES = {
    "impresora": [
        ("score_facilidad_uso", "Facilidad de uso"),
        ("score_calidad_impresion", "Calidad de impresión"),
        ("score_velocidad", "Velocidad"),
        ("score_fiabilidad", "Fiabilidad"),
        ("score_calidad_precio", "Calidad-precio"),
    ],
    "filamento": [
        ("score_facilidad_impresion", "Facilidad de impresión"),
        ("score_acabado", "Acabado"),
        ("score_resistencia", "Resistencia"),
        ("score_consistencia", "Consistencia"),
        ("score_calidad_precio", "Calidad-precio"),
    ],
    "accesorio": [
        ("score_utilidad", "Utilidad"),
        ("score_calidad_construccion", "Calidad de construcción"),
        ("score_facilidad_uso", "Facilidad de uso"),
        ("score_calidad_precio", "Calidad-precio"),
    ],
}

# (field, label, unit, group, better)  better: "max" | "min" | None (no highlight)
SPEC_FIELDS = {
    "impresora": [
        ("tipo", "Tipo", "", "General", None),
        ("cama_x_mm", "Cama X", "mm", "Dimensiones", "max"),
        ("cama_y_mm", "Cama Y", "mm", "Dimensiones", "max"),
        ("cama_z_mm", "Cama Z (altura)", "mm", "Dimensiones", "max"),
        ("auto_nivelado", "Auto-nivelado", "", "General", None),
        ("cama_caliente_max_c", "Temp. máx. cama", "°C", "General", "max"),
        ("velocidad_max_mms", "Velocidad máxima", "mm/s", "General", "max"),
        ("extrusor", "Extrusor", "", "General", None),
        ("pantalla", "Pantalla", "", "General", None),
        ("diametro_filamento_mm", "Diámetro de filamento", "mm", "General", None),
        ("nivel_ruido_db", "Nivel de ruido", "dB", "General", "min"),
        ("peso_kg", "Peso", "kg", "Dimensiones", None),
        ("garantia_meses", "Garantía", "meses", "General", "max"),
    ],
    "filamento": [
        ("material", "Material", "", "General", None),
        ("diametro_mm", "Diámetro", "mm", "General", None),
        ("peso_g", "Peso del rollo", "g", "General", "max"),
        ("tolerancia_diametro_mm", "Tolerancia de diámetro", "mm", "General", "min"),
        ("temp_boquilla_min_c", "Temp. boquilla mín.", "°C", "Temperaturas", None),
        ("temp_boquilla_max_c", "Temp. boquilla máx.", "°C", "Temperaturas", None),
        ("temp_cama_c", "Temp. cama", "°C", "Temperaturas", None),
        ("color", "Color", "", "General", None),
    ],
    "accesorio": [
        ("tipo_accesorio", "Tipo de accesorio", "", "General", None),
        ("compatibilidad", "Compatibilidad", "", "General", None),
        ("material", "Material", "", "General", None),
        ("cantidad", "Cantidad", "", "General", None),
    ],
}

CATEGORY_INTRO = {
    "impresora": "Comparativa de impresoras 3D FDM y de resina: cama de impresión, auto-nivelado, velocidad y fiabilidad, para elegir sin sorpresas. Consulta también la <a href=\"guia-mejor-impresora-2026.html\">guía de compra</a> si es tu primera impresora.",
    "filamento": "PLA, PETG, ABS, TPU: qué filamento usar según lo que vayas a imprimir, con temperaturas y consistencia de diámetro comparadas.",
    "accesorio": "Boquillas, herramientas y almacenaje: los accesorios que de verdad hacen falta para imprimir sin sobresaltos.",
}

CATEGORY_INTRO_SHORT = {
    "impresora": "Cama de impresión, auto-nivelado, velocidad y fiabilidad comparadas.",
    "filamento": "PLA, PETG, ABS, TPU: qué usar según lo que vayas a imprimir.",
    "accesorio": "Los accesorios que de verdad hacen falta para imprimir sin sobresaltos.",
}

RADAR_COLORS = ["#c2540c", "#0f6b5c", "#1f5fa8", "#a83f8f"]


# ---------------------------------------------------------------- helpers

def esc(s):
    return html.escape(str(s), quote=True) if s is not None else ""


def slug_ficha(p):
    return "producto-" + p["id"] + ".html"


def fmt_eur(v):
    if v is None:
        return None
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if s.endswith(",00"):
        s = s[:-3]
    return s + " €"


def fmt_val(v, unit=""):
    if v is None or v == "":
        return "—"
    if isinstance(v, bool):
        return "Sí" if v else "No"
    if unit:
        return f"{v} {unit}"
    return str(v)


def stars_html(rating):
    if rating is None:
        return '<span class="stars">Sin valorar</span>'
    full = int(round(rating))
    return f'<span class="stars">{"★" * full}{"☆" * (5 - full)}</span> <span>{rating:.1f}/5</span>'


def price_block_html(p):
    if p.get("isDemo"):
        return '<p class="precio-nota">Producto de ejemplo — sin precio real todavía.</p>'
    retail = p.get("retailPrice")
    disc = p.get("discountedPrice")
    fecha = p.get("precio_fecha")
    if disc is None and retail is None:
        return '<p class="precio-nota">Consulta el precio actual en Amazon.</p>'
    parts = [f'<span class="precio-actual">{fmt_eur(disc if disc is not None else retail)}</span>']
    if retail is not None and disc is not None and disc < retail:
        parts.append(f'<span class="precio-antes">{fmt_eur(retail)}</span>')
        parts.append('<span class="offer-badge">OFERTA</span>')
    fecha_txt = f" · {fecha}" if fecha else ""
    parts.append(f'<span class="precio-nota">Precio orientativo{fecha_txt} · consúltalo en Amazon</span>')
    return "\n".join(parts)


def buy_button_html(p, extra_class="", label=None):
    is_demo = p.get("isDemo")
    cls = "btn-comprar" + (" is-demo" if is_demo else "") + (" " + extra_class if extra_class else "")
    text = label or ("Ver opciones en Amazon" if is_demo else "Ver en Amazon")
    return (f'<a class="{cls}" href="{esc(p["affiliate_url"])}" target="_blank" '
            f'rel="sponsored nofollow noopener">{text}</a>')


def media_html(p, css_class="product-card-media"):
    imgs = p.get("images") or []
    if imgs:
        return f'<div class="{css_class}"><img src="{esc(imgs[0])}" alt="{esc(p["name"])}" loading="lazy" decoding="async"></div>'
    return f'<div class="{css_class}">{icon_svg(p["nicho"], "icon-nicho")}</div>'


def radar_canvas_html(elem_id, extra_class=""):
    return f'<canvas id="{elem_id}" class="{extra_class}" width="320" height="280" role="img" aria-label="Gráfico de valoraciones del editor"></canvas>'


def breadcrumb_schema(trail):
    """trail: lista de (nombre, path) — path relativo tipo 'index.html', SIEMPRE con item."""
    items = []
    for i, (name, path) in enumerate(trail, start=1):
        items.append(
            f'{{ "@type": "ListItem", "position": {i}, "name": {json.dumps(name, ensure_ascii=False)}, "item": "{SITE_URL}/{path}" }}'
        )
    sep = ",\n    "
    items_str = sep.join(items)
    return f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {items_str}
  ]
}}
</script>"""


# ---------------------------------------------------------------- shell

def page_shell(title, description, path, body, robots="index, follow", extra_head="", canonical=None):
    canon = canonical or f"{SITE_URL}/{path}"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="{robots}">

<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="assets/img/og-image.png">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary_large_image">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lexend:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="styles.css?v={VER}">
{ADSENSE_TAG}
{extra_head}
</head>
<body>
{header_html(path)}
{body}
{footer_html()}
<script defer src="lib/db.js?v={VER}"></script>
<script defer src="main.js?v={VER}"></script>
</body>
</html>
"""


def header_html(active_path):
    def cur(p):
        return " is-current" if p == active_path else ""

    items = [
        ("index.html", "Inicio"),
        ("categoria-impresoras.html", "Impresoras"),
        ("categoria-filamento.html", "Filamento"),
        ("categoria-accesorios.html", "Accesorios"),
        ("comparador.html", "Comparador"),
        ("guia-mejor-impresora-2026.html", "Guías"),
        ("ofertas.html", "Ofertas"),
    ]
    desktop_links = "\n      ".join(f'<a href="{p}" class="{cur(p).strip()}">{label}</a>' for p, label in items)
    mobile_links = "\n      ".join(f'<a href="{p}">{label}</a>' for p, label in items)
    return f"""<header class="site-header">
  <div class="container-wide header-row">
    <a class="brand" href="index.html">
      <span class="brand-mark" aria-hidden="true">▲</span>
      <span class="brand-name">Guía3D</span>
    </a>
    <nav class="header-nav" aria-label="Navegación principal">
      {desktop_links}
    </nav>
    <button type="button" class="nav-toggle" id="navToggle" aria-expanded="false" aria-controls="mobileNav" aria-label="Abrir menú">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
  </div>
  <div class="container-wide">
    <nav class="mobile-nav" id="mobileNav" aria-label="Navegación móvil">
      {mobile_links}
    </nav>
  </div>
</header>"""


def footer_html():
    return f"""<footer class="site-footer">
  <div class="container-wide">
    <div class="footer-cols">
      <div>
        <h4>Guía3D</h4>
        <p>Comparativas y guías de compra honestas sobre impresión 3D: impresoras, filamento y accesorios.</p>
      </div>
      <div>
        <h4>Catálogo</h4>
        <ul>
          <li><a href="categoria-impresoras.html">Impresoras</a></li>
          <li><a href="categoria-filamento.html">Filamento</a></li>
          <li><a href="categoria-accesorios.html">Accesorios</a></li>
          <li><a href="comparador.html">Comparador</a></li>
          <li><a href="ofertas.html">Ofertas</a></li>
        </ul>
      </div>
      <div>
        <h4>Legal</h4>
        <ul>
          <li><a href="como-elegimos.html">Cómo elegimos</a></li>
          <li><a href="privacidad.html">Privacidad</a></li>
          <li><a href="aviso-legal.html">Aviso legal</a></li>
        </ul>
      </div>
    </div>
    <p class="disclaimer-line">© {datetime.date.today().year} Guía3D · Utilix. Como Afiliados de Amazon, obtenemos ingresos por las compras que cumplen los requisitos aplicables. «Amazon» y el logo de Amazon son marcas de Amazon.com, Inc. o sus filiales. Los precios y la disponibilidad de los productos son los de Amazon.es en el momento de la compra.</p>
  </div>
</footer>"""


def ad_slot_html(sidebar=False):
    cls = "ad-slot ad-slot-sidebar" if sidebar else "ad-slot container-wide"
    return f"""<div class="{cls}" data-ad-slot>
  <span class="ad-label">ANUNCIO</span>
  <!-- PEGA AQUÍ TU CÓDIGO DE ADSENSE -->
</div>"""


def write(rel_path, content):
    full = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("  ✓", rel_path)


# ---------------------------------------------------------------- product card / ficha builders

def product_card_html(p):
    ribbon = '<span class="demo-ribbon">EJEMPLO</span>' if p.get("isDemo") else ""
    rating = stars_html(p.get("valoracion_media")) if not p.get("isDemo") else '<span class="stars">Producto de muestra</span>'
    price_disc = p.get("discountedPrice")
    price_retail = p.get("retailPrice")
    if p.get("isDemo") or (price_disc is None and price_retail is None):
        price_html = '<span class="product-card-price" style="font-size:.86rem;color:var(--text-muted);">Ver en Amazon</span>'
    else:
        before = f'<span class="price-before">{fmt_eur(price_retail)}</span>' if price_retail and price_disc and price_disc < price_retail else ""
        price_html = f'<span class="product-card-price">{before}{fmt_eur(price_disc if price_disc is not None else price_retail)}</span>'
    return f"""<article class="product-card">
  {ribbon}
  {media_html(p)}
  <div class="product-card-body">
    <span class="product-card-cat">{esc(p.get("categoria") or NICHO_LABEL.get(p["nicho"]))}</span>
    <h3><a href="{slug_ficha(p)}">{esc(p["name"])}</a></h3>
    <p class="card-desc">{esc(p.get("description") or "")}</p>
    <div class="product-card-foot">
      {price_html}
      <span class="product-card-rating">{rating}</span>
    </div>
    {buy_button_html(p, extra_class="", label=None)}
  </div>
</article>"""


def radar_data_attr(p):
    axes = SCORE_AXES[p["nicho"]]
    vals = [p.get(f) if p.get(f) is not None else 0 for f, _ in axes]
    labels = [label for _, label in axes]
    return esc(json.dumps({"labels": labels, "values": vals}))


def build_ficha(p):
    nicho = p["nicho"]
    is_demo = p.get("isDemo")
    imgs = p.get("images") or []
    if imgs:
        main_img = f'<img class="ficha-img-main" src="{esc(imgs[0])}" alt="{esc(p["name"])}" fetchpriority="high">'
        thumbs = "".join(f'<li><img src="{esc(u)}" alt="" class="{"is-active" if i == 0 else ""}"></li>' for i, u in enumerate(imgs))
    else:
        main_img = f'<div class="ficha-img-placeholder">{icon_svg(nicho, "icon-placeholder")}</div>'
        thumbs = ""

    demo_banner = ""
    if is_demo:
        demo_banner = ('<div class="demo-banner"><strong>Producto de ejemplo.</strong> Esta ficha muestra cómo se '
                        'verá una página de producto real cuando añadamos tus enlaces de afiliado de Amazon. '
                        'Ningún dato de esta ficha (specs, texto, puntuaciones) corresponde a un producto real.</div>')

    spec_rows = SPEC_FIELDS[nicho]
    groups = {}
    for field, label, unit, group, better in spec_rows:
        groups.setdefault(group, []).append((field, label, unit))
    specs_html = ""
    for group, rows in groups.items():
        rows_html = "".join(
            f'<tr><th scope="row">{esc(label)}</th><td>{esc(fmt_val(p.get(field), unit))}</td></tr>'
            for field, label, unit in rows
        )
        specs_html += f'<h3 style="font-size:.9rem;margin-top:1rem;color:var(--text-muted);">{esc(group)}</h3><table class="spec-table" data-specs>{rows_html}</table>'

    specs_extra = p.get("specs_extra") or {}
    specs_extra_html = ""
    if specs_extra:
        rows = "".join(f'<tr><th scope="row">{esc(k)}</th><td>{esc(v)}</td></tr>' for k, v in specs_extra.items())
        specs_extra_html = f'<details class="specs-extra"><summary>Otros datos</summary><table class="spec-table">{rows}</table></details>'

    pros = "".join(f"<li>{esc(x)}</li>" for x in (p.get("pros") or []))
    contras = "".join(f"<li>{esc(x)}</li>" for x in (p.get("contras") or []))

    resenas_html = ""
    if p.get("resenas_resumen"):
        resenas_html = f'<section class="ficha-resenas"><h2>Qué dicen los compradores</h2><p class="resenas-resumen">{esc(p["resenas_resumen"])}</p><p class="radar-note">Reseñas mostradas en Amazon en el momento de la captura.</p></section>'

    axes = SCORE_AXES[nicho]
    legend = "".join(
        f'<span><span class="dot" style="background:{RADAR_COLORS[0]}"></span>{esc(label)}: {p.get(f) if p.get(f) is not None else "—"}/10</span>'
        for f, label in axes
    )

    jsonld = ""
    if not is_demo and p.get("valoracion_media") is not None:
        jsonld = f"""<script type="application/ld+json">
{json.dumps({
            "@context": "https://schema.org", "@type": "Product",
            "name": p["name"], "brand": p.get("marca"),
            "image": p.get("images") or [],
            "offers": {"@type": "Offer", "price": str(p.get("discountedPrice") or p.get("retailPrice") or ""), "priceCurrency": "EUR", "availability": "https://schema.org/InStock"},
            "aggregateRating": {"@type": "AggregateRating", "ratingValue": str(p.get("valoracion_media")), "reviewCount": str(p.get("resenas_cantidad") or 1)}
        }, ensure_ascii=False, indent=2)}
</script>"""
    jsonld += breadcrumb_schema([("Guía3D", "index.html"), (NICHO_LABEL[nicho], NICHO_SLUG_PAGE[nicho]), (p["name"], slug_ficha(p))])

    body = f"""<main id="contenido" class="container-wide">
  <p class="breadcrumb" style="margin-top:1rem;"><a href="index.html">Guía3D</a> / <a href="{NICHO_SLUG_PAGE[nicho]}">{NICHO_LABEL[nicho]}</a> / {esc(p["name"])}</p>
  {demo_banner}
  <article class="ficha" data-producto-id="{esc(p['id'])}">
    <div class="ficha-layout">
      <section class="ficha-galeria" data-galeria>
        {main_img}
        <ul class="ficha-thumbs" data-thumbs>{thumbs}</ul>
      </section>

      <div>
        <header class="ficha-head">
          <p class="ficha-marca">{esc(p.get("marca") or "")}</p>
          <h1 class="ficha-nombre">{esc(p["name"])}</h1>
          <div class="ficha-rating">{stars_html(p.get("valoracion_media")) if not is_demo else "Producto de ejemplo"} {('· ' + str(p.get('resenas_cantidad')) + ' reseñas') if p.get('resenas_cantidad') else ''}</div>
          <div class="ficha-precio">{price_block_html(p)}</div>
          {buy_button_html(p)}
        </header>

        <section class="ficha-radar">
          <h2>Valoración del editor</h2>
          <div class="radar-wrap" data-radar='{radar_data_attr(p)}'>
            {radar_canvas_html("radarFicha")}
            <div class="radar-legend">{legend}</div>
          </div>
          <p class="radar-note">Puntuaciones editoriales de 0 a 10, comparables entre productos del mismo tipo. No son una puntuación oficial de Amazon.</p>
        </section>
      </div>
    </div>

    <section class="ficha-specs container">
      <h2>Ficha técnica</h2>
      {specs_html}
      {specs_extra_html}
    </section>

    <section class="ficha-editorial container">
      <div class="editorial-cuerpo">{p.get("cuerpo_editorial") or ""}</div>
      <div class="pros-contras">
        <ul class="pros">{pros}</ul>
        <ul class="contras">{contras}</ul>
      </div>
      <p class="ideal-para"><strong>Ideal para:</strong> {esc(p.get("ideal_para") or "")}</p>
    </section>

    <div class="container">{resenas_html}</div>

    <div class="container">
      <section class="ficha-comparar">
        <button class="btn-comparar-add" data-add-comparador="{esc(p['id'])}" data-nicho="{nicho}">+ Añadir al comparador</button>
      </section>
      {buy_button_html(p, extra_class="btn-repeat")}
      <p class="aviso-afiliados">Como Afiliados de Amazon, obtenemos ingresos por las compras que cumplen los requisitos aplicables. «Amazon» y el logo de Amazon son marcas de Amazon.com, Inc. o sus filiales.</p>
    </div>
  </article>
  {ad_slot_html()}
</main>"""

    title = f'{p["name"]} — ficha y valoración | Guía3D'
    desc = (p.get("description") or "")[:155]
    robots = "noindex, nofollow" if is_demo else "index, follow"
    return page_shell(title, desc, slug_ficha(p), body, robots=robots, extra_head=jsonld)


# ---------------------------------------------------------------- category pages

def build_category(nicho):
    items = [p for p in PRODUCTOS if p["nicho"] == nicho]
    cards = "\n".join(product_card_html(p) for p in items)
    empty = ""
    if not items:
        empty = f'<div class="empty-state"><div class="empty-icon">{icon_svg(nicho, "icon-empty")}</div><p>Todavía no hay productos en esta categoría. Vuelve pronto.</p></div>'
    demo_note = ""
    if all(p.get("isDemo") for p in items) and items:
        demo_note = '<div class="demo-banner"><strong>Catálogo de ejemplo.</strong> Los productos de esta página son de muestra, pendientes de sustituir por productos reales con enlaces de afiliado.</div>'

    body = f"""<main id="contenido">
  <section class="page-hero container-wide">
    <p class="breadcrumb"><a href="index.html">Guía3D</a> / {NICHO_LABEL[nicho]}</p>
    <h1>{NICHO_LABEL[nicho]}</h1>
    <p class="hero-sub">{CATEGORY_INTRO[nicho]}</p>
  </section>
  <div class="container-wide">
    {demo_note}
    <div class="catalog-grid">
      {cards}
    </div>
    {empty}
  </div>
  {ad_slot_html()}
</main>"""
    title = f"{NICHO_LABEL[nicho]}: comparativa y opiniones | Guía3D"
    desc = CATEGORY_INTRO_SHORT[nicho]
    crumbs = breadcrumb_schema([("Guía3D", "index.html"), (NICHO_LABEL[nicho], NICHO_SLUG_PAGE[nicho])])
    return page_shell(title, desc, NICHO_SLUG_PAGE[nicho], body, extra_head=crumbs)


# ---------------------------------------------------------------- home

def build_home():
    featured = [p for p in PRODUCTOS if p.get("isFeatured")][:6]
    cards = "\n".join(product_card_html(p) for p in featured)
    demo_note = ""
    if featured and all(p.get("isDemo") for p in featured):
        demo_note = '<div class="demo-banner"><strong>Catálogo de ejemplo.</strong> Los productos que ves ahora son de muestra para enseñar cómo funciona la web — pronto los sustituiremos por productos reales de Amazon.</div>'
    cat_cards = "\n".join(f"""<a class="guide-card" href="{NICHO_SLUG_PAGE[n]}">
      <span class="guide-card-icon" aria-hidden="true">{icon_svg(n, "icon-guide")}</span>
      <h2>{NICHO_LABEL[n]}</h2>
      <p>{CATEGORY_INTRO_SHORT[n]}</p>
      <span class="card-cta">Ver {NICHO_LABEL[n].lower()} →</span>
    </a>""" for n in NICHOS)

    body = f"""<main id="hub">
  <section class="hero container-wide">
    <span class="hero-kicker">{icon_svg("escudo")} Puntuaciones y specs reales, sin productos inventados</span>
    <h1>Compara impresoras 3D, filamento y accesorios antes de comprar</h1>
    <p class="hero-sub">Fichas completas, puntuaciones del editor y un comparador lado a lado para decidir con datos, no con intuición.</p>
  </section>

  <div class="hub-layout container-wide">
    <div>
      <section class="guide-grid" aria-label="Categorías" style="margin-bottom:2rem;">
        {cat_cards}
      </section>

      <h2 style="font-size:1.3rem;margin-bottom:1rem;">Destacados</h2>
      {demo_note}
      <div class="catalog-grid">
        {cards}
      </div>
    </div>
    <aside class="sidebar-ad-slot" aria-label="Publicidad">
      {ad_slot_html(sidebar=True)}
    </aside>
  </div>

  {ad_slot_html()}

  <section class="explain-section container-wide">
    <h2>Cómo elegimos</h2>
    <div class="explain-copy">
      <p>Cada producto tiene una <strong>ficha técnica completa</strong>, un <strong>gráfico de valoración del editor</strong> (0-10 en varios ejes) y un <strong>comparador</strong> para enfrentar varios modelos lado a lado. Los enlaces de compra son de afiliado de Amazon: si compras a través de ellos, podemos recibir una comisión sin coste extra para ti. Detalles de la metodología en <a href="como-elegimos.html">cómo elegimos</a>.</p>
    </div>
  </section>

  <section class="more-section container-wide">
    <h2>Guías de compra</h2>
    <div class="more-grid">
      <a class="more-card" href="guia-mejor-impresora-2026.html">
        <span class="card-icon" aria-hidden="true">{icon_svg("impresora", "icon-more")}</span>
        <h3>Mejor impresora 3D para empezar 2026</h3>
        <p>Nuestra recomendación por presupuesto y tipo de uso.</p>
      </a>
      <a class="more-card" href="comparador.html">
        <span class="card-icon" aria-hidden="true">{icon_svg("comparador", "icon-more")}</span>
        <h3>Comparador</h3>
        <p>Enfrenta varios productos lado a lado, con gráficos superpuestos.</p>
      </a>
      <a class="more-card" href="ofertas.html">
        <span class="card-icon" aria-hidden="true">{icon_svg("ofertas", "icon-more")}</span>
        <h3>Ofertas</h3>
        <p>Productos con descuento respecto a su precio habitual.</p>
      </a>
    </div>
  </section>
</main>"""
    return page_shell(
        "Comparativa de impresoras 3D, filamento y accesorios | Guía3D",
        "Fichas completas, puntuaciones del editor y comparador lado a lado de impresoras 3D, filamento y accesorios. Enlaces de afiliado de Amazon.",
        "index.html", body,
    )


# ---------------------------------------------------------------- comparador

def build_comparador():
    tabs = "\n      ".join(
        f'<button type="button" data-nicho-tab="{n}" class="{"is-active" if i == 0 else ""}">{icon_svg(n, "icon-tab")} {NICHO_LABEL[n]}</button>'
        for i, n in enumerate(NICHOS)
    )
    checklists = ""
    for n in NICHOS:
        items = [p for p in PRODUCTOS if p["nicho"] == n]
        rows = "".join(f'''<label class="comparador-check-item">
          <input type="checkbox" data-compare-check value="{esc(p["id"])}">
          {esc(p["name"])}
        </label>''' for p in items)
        checklists += f'<div class="comparador-checklist" data-nicho-panel="{n}" {"" if n == NICHOS[0] else "hidden"}>{rows}</div>'

    body = f"""<main id="contenido">
  <section class="page-hero container-wide">
    <p class="breadcrumb"><a href="index.html">Guía3D</a> / Comparador</p>
    <h1>Comparador</h1>
    <p class="hero-sub">Elige 2 o más productos del mismo tipo y compáralos lado a lado, con sus gráficos de valoración superpuestos.</p>
  </section>

  <div class="container-wide">
    <div class="comparador-picker">
      <h2>Elige productos a comparar</h2>
      <div class="comparador-nicho-tabs">
        {tabs}
      </div>
      {checklists}
    </div>

    <div id="comparadorResult" class="comparador-result" data-comparador-root>
      <div class="comparador-empty empty-state"><div class="empty-icon">{icon_svg("comparador", "icon-empty")}</div><p>Selecciona al menos 2 productos del mismo tipo para ver la comparativa.</p></div>
    </div>
  </div>
  {ad_slot_html()}
</main>"""
    return page_shell(
        "Comparador de impresoras 3D, filamento y accesorios | Guía3D",
        "Compara varios productos lado a lado: ficha técnica completa y gráfico de valoración superpuesto.",
        "comparador.html", body,
        extra_head=breadcrumb_schema([("Guía3D", "index.html"), ("Comparador", "comparador.html")]),
    )


# ---------------------------------------------------------------- buying guide

def build_guide():
    impresoras = [p for p in PRODUCTOS if p["nicho"] == "impresora"]
    demo_note = ""
    if impresoras and all(p.get("isDemo") for p in impresoras):
        demo_note = '<div class="demo-banner"><strong>Catálogo de ejemplo.</strong> Las recomendaciones de abajo son productos de muestra, pendientes de sustituir por modelos reales.</div>'
    shortlist = "\n".join(f"""<article class="product-card">
      {'<span class="demo-ribbon">EJEMPLO</span>' if p.get("isDemo") else ""}
      {media_html(p)}
      <div class="product-card-body">
        <span class="product-card-cat">{esc(p.get("categoria"))}</span>
        <h3><a href="{slug_ficha(p)}">{esc(p["name"])}</a></h3>
        <p class="card-desc">{esc(p.get("ideal_para") or "")}</p>
        {buy_button_html(p)}
      </div>
    </article>""" for p in impresoras)

    body = f"""<main id="contenido">
  <section class="page-hero container-wide">
    <p class="breadcrumb"><a href="index.html">Guía3D</a> / Mejor impresora 2026</p>
    <h1>Mejor impresora 3D para empezar en 2026</h1>
    <p class="hero-sub">Nuestra recomendación según presupuesto y tipo de uso, con los mismos criterios que usamos en todo el catálogo.</p>
  </section>

  <div class="article-layout container-wide">
    <div class="prose">
      <h2>Qué mirar antes de comprar</h2>
      <ul>
        <li><strong>Tamaño de cama:</strong> 220x220 mm cubre casi cualquier pieza doméstica.</li>
        <li><strong>Auto-nivelado:</strong> evita el ajuste manual, la causa más habitual de que fallen las primeras impresiones.</li>
        <li><strong>Cama caliente:</strong> imprescindible si más adelante quieres imprimir en PETG o ABS.</li>
        <li><strong>Nivel de ruido y comunidad:</strong> importa si la impresora va a estar en una zona habitada, y ayuda tener repuestos fáciles de encontrar.</li>
      </ul>

      {demo_note}

      <h2>Nuestra selección</h2>
      <div class="catalog-grid">
        {shortlist}
      </div>

      <p style="margin-top:1.4rem;"><a href="comparador.html" style="color:var(--accent);font-weight:700;">→ Compáralas lado a lado en el comparador</a></p>
    </div>
    <aside class="sidebar-ad-slot" aria-label="Publicidad">
      {ad_slot_html(sidebar=True)}
    </aside>
  </div>
  {ad_slot_html()}

  <section class="faq-section container-wide">
    <h2>Preguntas frecuentes</h2>
    <div class="faq-list">
      <details class="faq-item"><summary>¿FDM o resina para empezar?</summary><p>Para la gran mayoría de gente que empieza, FDM: es más barata de mantener y el filamento cuesta menos por pieza que la resina.</p></details>
      <details class="faq-item"><summary>¿Necesito auto-nivelado?</summary><p>No es obligatorio, pero facilita mucho la vida a quien empieza, evitando la causa más común de que fallen las primeras impresiones.</p></details>
    </div>
  </section>
</main>"""
    return page_shell(
        "Mejor impresora 3D para empezar 2026 | Guía3D",
        "Guía de compra: qué impresora 3D elegir según tu presupuesto y tipo de uso, con nuestra selección comparada.",
        "guia-mejor-impresora-2026.html", body,
        extra_head=breadcrumb_schema([("Guía3D", "index.html"), ("Mejor impresora 2026", "guia-mejor-impresora-2026.html")]),
    )


# ---------------------------------------------------------------- ofertas

def build_ofertas():
    ofertas = [p for p in PRODUCTOS if p.get("discountedPrice") is not None and p.get("retailPrice") is not None and p["discountedPrice"] < p["retailPrice"]]
    if ofertas:
        cards = "\n".join(product_card_html(p) for p in ofertas)
        content = f'<div class="catalog-grid">{cards}</div>'
    else:
        content = f'<div class="empty-state"><div class="empty-icon">{icon_svg("ofertas", "icon-empty")}</div><p>Todavía no tenemos ofertas activas registradas. Vuelve pronto — en cuanto añadamos productos reales, las rebajas aparecerán aquí automáticamente.</p></div>'

    body = f"""<main id="contenido">
  <section class="page-hero container-wide">
    <p class="breadcrumb"><a href="index.html">Guía3D</a> / Ofertas</p>
    <h1>Ofertas</h1>
    <p class="hero-sub">Productos con descuento respecto a su precio habitual en Amazon.es. Se actualiza cuando revisamos el catálogo.</p>
  </section>
  <div class="container-wide">{content}</div>
  {ad_slot_html()}
</main>"""
    return page_shell(
        "Ofertas en impresoras 3D, filamento y accesorios | Guía3D",
        "Productos de impresión 3D con descuento respecto a su precio habitual en Amazon.es.",
        "ofertas.html", body,
        extra_head=breadcrumb_schema([("Guía3D", "index.html"), ("Ofertas", "ofertas.html")]),
    )


# ---------------------------------------------------------------- db.js

def build_db_js():
    spec_fields_js = {
        nicho: [{"field": f, "label": label, "unit": unit, "better": better} for f, label, unit, group, better in rows]
        for nicho, rows in SPEC_FIELDS.items()
    }
    payload = {
        "productos": PRODUCTOS,
        "scoreAxes": SCORE_AXES,
        "specFields": spec_fields_js,
        "nichos": NICHOS,
        "updated": datetime.date.today().isoformat(),
    }
    return "(function () {\n  \"use strict\";\n  window.__DB__ = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n})();\n"


# ---------------------------------------------------------------- static legal / trust pages

def build_como_elegimos():
    body = """<main id="contenido">
  <section class="page-hero container-wide">
    <p class="breadcrumb"><a href="index.html">Guía3D</a> / Cómo elegimos</p>
    <h1>Cómo elegimos y puntuamos los productos</h1>
    <p class="hero-sub">La metodología detrás de cada ficha y cada puntuación, explicada sin letra pequeña.</p>
  </section>
  <div class="container-wide">
    <div class="prose">
      <h2>De dónde salen los datos</h2>
      <p>Cada producto del catálogo llega a partir de un enlace de afiliado de Amazon.es. A partir de ese enlace extraemos el título, la marca, el precio, la valoración media, el número de reseñas, las imágenes y la ficha técnica publicada por el vendedor. Cuando Amazon no publica un dato concreto, lo dejamos en blanco («—») en lugar de inventarlo.</p>

      <h2>Qué son las puntuaciones de 0 a 10</h2>
      <p>El gráfico de valoración de cada ficha (facilidad de uso, calidad de impresión, velocidad, etc.) <strong>no es una puntuación oficial de Amazon</strong>: es un cálculo editorial nuestro, hecho a partir de las especificaciones técnicas reales del producto, comparadas con el resto del catálogo de su misma categoría. Por ejemplo, la puntuación de velocidad de una impresora se calcula a partir de su velocidad máxima en mm/s, situada dentro del rango de velocidades que hemos visto en impresoras similares.</p>
      <p>Estas puntuaciones se recalculan cuando cambia el catálogo, para que sigan siendo comparables entre sí. Las verás siempre etiquetadas como «valoración del editor».</p>

      <h2>Por qué a veces falta un dato</h2>
      <p>Preferimos mostrar «—» a inventar una especificación. Si un dato no aparece en la ficha de Amazon ni en la documentación del fabricante, se queda en blanco.</p>

      <h2>Los enlaces de afiliado</h2>
      <p>Todos los botones «Ver en Amazon» usan nuestro enlace de afiliado de Amazon.es. Si compras a través de ellos, podemos recibir una pequeña comisión, sin ningún coste adicional para ti. Esto no influye en las puntuaciones ni en el orden en que mostramos los productos — nuestro criterio es siempre el mismo, tanto si el producto nos genera comisión como si no.</p>
    </div>
  </div>
</main>"""
    return page_shell(
        "Cómo elegimos y puntuamos los productos | Guía3D",
        "La metodología detrás de las puntuaciones y fichas de producto de Guía3D, explicada de forma transparente.",
        "como-elegimos.html", body,
        extra_head=breadcrumb_schema([("Guía3D", "index.html"), ("Cómo elegimos", "como-elegimos.html")]),
    )


def build_privacidad():
    body = """<main id="contenido">
  <div class="container" style="padding-block:2.5rem;">
    <h1 style="font-size:1.9rem; margin-bottom:1.2rem;">Política de privacidad</h1>
    <div class="prose">
      <p>Guía3D es un sitio de contenido informativo. No requiere registro ni cuenta de usuario, y no recopilamos nombre, correo electrónico ni ningún otro dato personal a través de formularios.</p>
      <p>Esta web puede mostrar anuncios de Google AdSense. Google y sus proveedores pueden utilizar cookies u otras tecnologías similares para mostrar publicidad relevante y medir su rendimiento. Puedes gestionar tus preferencias de anuncios desde <a href="https://adssettings.google.com/" style="color:var(--accent);">adssettings.google.com</a> y tus preferencias de cookies desde la configuración de tu navegador.</p>
      <p><strong>Enlaces de afiliado:</strong> algunos enlaces de esta web dirigen a Amazon.es a través del Programa de Afiliados de Amazon EU. Al hacer clic en uno de estos enlaces, Amazon puede colocar una cookie en tu navegador para reconocer que la visita procede de Guía3D si completas una compra. Esto no afecta al precio que pagas y no compartimos ningún dato personal tuyo con Amazon a través de este proceso.</p>
      <p><strong>Comparador:</strong> los productos que seleccionas en el comparador se guardan únicamente en tu propio navegador (almacenamiento local), nunca en un servidor nuestro.</p>
      <p>Para cualquier consulta sobre esta política, puedes escribir a: hola@utilix.uno</p>
    </div>
  </div>
</main>"""
    return page_shell(
        "Política de privacidad | Guía3D",
        "Política de privacidad de Guía3D: qué datos recogemos y cómo funcionan los enlaces de afiliado y los anuncios.",
        "privacidad.html", body, robots="noindex, follow",
    )


def build_aviso_legal():
    body = """<main id="contenido">
  <div class="container" style="padding-block:2.5rem;">
    <h1 style="font-size:1.9rem; margin-bottom:1.2rem;">Aviso legal</h1>
    <div class="prose">
      <p><!-- TODO (propietario del sitio): sustituye estos datos por los de tu titularidad real (nombre/razón social, NIF/CIF, domicilio, correo de contacto). -->Titular del sitio: Guía3D · Utilix · Contacto: hola@utilix.uno</p>
      <p><strong>Guía3D forma parte del Programa de Afiliados de Amazon EU</strong>, un programa de publicidad para afiliados diseñado para ofrecer a los sitios web un modo de obtener comisiones por publicidad, publicitando e incluyendo enlaces a Amazon.es y sitios afiliados de Amazon en la Unión Europea. Como Afiliados de Amazon, obtenemos ingresos por las compras adscritas que cumplen los requisitos aplicables.</p>
      <p>Los precios, la disponibilidad y las características de los productos mostrados en Amazon a través de nuestros enlaces son los vigentes en Amazon.es en el momento de la compra y pueden cambiar sin previo aviso. Guía3D no vende, envía ni gestiona directamente ningún producto: toda compra se realiza en Amazon.es bajo sus propias condiciones.</p>
      <p>Las puntuaciones y valoraciones del editor mostradas en cada ficha son cálculos propios, explicados en <a href="como-elegimos.html" style="color:var(--accent);">cómo elegimos</a>, y no deben confundirse con las valoraciones o reseñas oficiales de Amazon, que se muestran por separado y de forma identificada.</p>
      <p>Este sitio no se hace responsable del uso que se dé a los productos adquiridos a través de los enlaces de esta web, ni de incidencias de envío, garantía o postventa, que corresponden íntegramente a Amazon y al fabricante de cada producto.</p>
    </div>
  </div>
</main>"""
    return page_shell(
        "Aviso legal | Guía3D",
        "Aviso legal de Guía3D, incluida la divulgación del Programa de Afiliados de Amazon EU.",
        "aviso-legal.html", body, robots="noindex, follow",
    )


# ---------------------------------------------------------------- main

def main():
    print(f"Generando Guía3D (v={VER})...")
    write("index.html", build_home())
    for n in NICHOS:
        write(NICHO_SLUG_PAGE[n], build_category(n))
    for p in PRODUCTOS:
        write(slug_ficha(p), build_ficha(p))
    write("comparador.html", build_comparador())
    write("guia-mejor-impresora-2026.html", build_guide())
    write("ofertas.html", build_ofertas())
    write("como-elegimos.html", build_como_elegimos())
    write("privacidad.html", build_privacidad())
    write("aviso-legal.html", build_aviso_legal())
    write("lib/db.js", build_db_js())
    print(f"Listo: {len(PRODUCTOS)} productos, {len(NICHOS)} categorías, {3 + len(NICHOS) + len(PRODUCTOS) + 3} páginas HTML.")


if __name__ == "__main__":
    main()
