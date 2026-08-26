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
    "impresora": "Comparativa de impresoras 3D FDM y de resina: cama de impresión, auto-nivelado, velocidad y fiabilidad, para elegir sin sorpresas. Consulta también <a href=\"como-elegir-tu-primera-impresora-3d.html\">cómo elegir tu primera impresora</a> o <a href=\"que-impresora-3d-comprar.html\">qué impresora comprar</a> si aún no lo tienes claro.",
    "filamento": "PLA, PETG, ABS, TPU: qué filamento usar según lo que vayas a imprimir, con temperaturas y consistencia de diámetro comparadas. Ver también <a href=\"mejor-filamento-pla-calidad-precio.html\">mejor PLA calidad-precio</a>.",
    "accesorio": "Boquillas, herramientas y almacenaje: los accesorios que de verdad hacen falta para imprimir sin sobresaltos. Ver también <a href=\"accesorios-imprescindibles-para-impresora-3d.html\">accesorios imprescindibles</a>.",
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


def is_activo(p):
    """False = producto oculto (p.ej. sin enlace de afiliado válido todavía).
    No aparece en home, categorías, comparador, ofertas ni guías, pero su
    ficha se sigue generando (noindex,nofollow) para poder reactivarlo sin
    perder datos: basta con poner "activo": true en productos.json."""
    return p.get("activo", True) is not False


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


# ---------------------------------------------------------------- schema.org helpers

def breadcrumb_jsonld(items):
    """items: lista de (nombre, path-relativo-o-None-para-el-actual)."""
    entries = []
    for i, (name, path) in enumerate(items, start=1):
        entry = {"@type": "ListItem", "position": i, "name": name}
        if path:
            entry["item"] = f"{SITE_URL}/{path}"
        entries.append(entry)
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": entries}
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def itemlist_jsonld(products, name=None):
    entries = [
        {"@type": "ListItem", "position": i, "url": f"{SITE_URL}/{slug_ficha(p)}", "name": p["name"]}
        for i, p in enumerate(products, start=1)
    ]
    data = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": entries}
    if name:
        data["name"] = name
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def article_jsonld(title, description, path, date_published=None):
    """date_published: ISO date real (día en que se publicó de verdad). Si no se conoce
    con certeza (p.ej. contenido preexistente sin fecha registrada), se omite en vez
    de inventarla — Google trata datePublished ausente mejor que uno incorrecto."""
    data = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "description": description,
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{SITE_URL}/{path}"},
        "dateModified": datetime.date.today().isoformat(),
        "author": {"@type": "Organization", "name": "Guía3D"},
        "publisher": {"@type": "Organization", "name": "Guía3D"},
    }
    if date_published:
        data["datePublished"] = date_published
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def comparar_cta_html(nicho, ids, label="Comparar estos modelos en el comparador →"):
    """CTA que enlaza al comparador con los productos ya preseleccionados (?nicho=&ids=)."""
    ids_param = ",".join(ids)
    return (f'<a class="btn-comprar btn-comparar-cta" href="comparador.html?nicho={nicho}&amp;ids={esc(ids_param)}">'
            f'{esc(label)}</a>')


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
    elif not is_activo(p):
        motivo = p.get("motivo_oculto") or "Pendiente de enlace de afiliado válido de Amazon.es"
        demo_banner = (f'<div class="demo-banner"><strong>Producto oculto.</strong> {esc(motivo)}. '
                        'No aparece en home, categorías, comparador, ofertas ni guías hasta que se reactive.</div>')

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

    ARTICULOS_POR_NICHO = {
        "impresora": [
            ("que-impresora-3d-comprar.html", "Qué impresora 3D comprar"),
            ("mejor-impresora-3d-calidad-precio.html", "Mejor impresora 3D calidad-precio"),
        ],
        "filamento": [("mejor-filamento-pla-calidad-precio.html", "Mejor filamento PLA calidad-precio")],
        "accesorio": [("accesorios-imprescindibles-para-impresora-3d.html", "Accesorios imprescindibles")],
    }
    articulos_html = ""
    enlaces_art = ARTICULOS_POR_NICHO.get(nicho) or []
    if enlaces_art and not is_demo:
        items = "".join(f'<li><a href="{href}">{esc(txt)}</a></li>' for href, txt in enlaces_art)
        articulos_html = f'<section class="ficha-resenas"><h2>Guías relacionadas</h2><ul>{items}</ul></section>'

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
    jsonld += breadcrumb_jsonld([("Guía3D", "index.html"), (NICHO_LABEL[nicho], NICHO_SLUG_PAGE[nicho]), (p["name"], None)])

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

    <div class="container">{resenas_html}{articulos_html}</div>

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
    robots = "noindex, nofollow" if (is_demo or not is_activo(p)) else "index, follow"
    return page_shell(title, desc, slug_ficha(p), body, robots=robots, extra_head=jsonld)


# ---------------------------------------------------------------- category pages

def build_category(nicho):
    items = [p for p in PRODUCTOS if p["nicho"] == nicho and is_activo(p)]
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
    schema = breadcrumb_jsonld([("Guía3D", "index.html"), (NICHO_LABEL[nicho], None)])
    if items:
        schema += itemlist_jsonld(items, name=NICHO_LABEL[nicho])
    return page_shell(title, desc, NICHO_SLUG_PAGE[nicho], body, extra_head=schema)


# ---------------------------------------------------------------- home

def build_home():
    featured = [p for p in PRODUCTOS if p.get("isFeatured") and is_activo(p)][:6]
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
      <a class="more-card" href="como-elegir-tu-primera-impresora-3d.html">
        <span class="card-icon" aria-hidden="true">{icon_svg("escudo", "icon-more")}</span>
        <h3>Cómo elegir tu primera impresora 3D</h3>
        <p>La guía completa: qué mirar antes de comprar.</p>
      </a>
      <a class="more-card" href="que-impresora-3d-comprar.html">
        <span class="card-icon" aria-hidden="true">{icon_svg("impresora", "icon-more")}</span>
        <h3>Qué impresora 3D comprar</h3>
        <p>Árbol de decisión rápido por presupuesto y uso.</p>
      </a>
      <a class="more-card" href="mejor-impresora-3d-calidad-precio.html">
        <span class="card-icon" aria-hidden="true">{icon_svg("escudo", "icon-more")}</span>
        <h3>Mejor impresora 3D calidad-precio</h3>
        <p>Ranking por relación entre specs y precio.</p>
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
        items = [p for p in PRODUCTOS if p["nicho"] == n and is_activo(p)]
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
    schema = breadcrumb_jsonld([("Guía3D", "index.html"), ("Comparador", None)])
    return page_shell(
        "Comparador de impresoras 3D, filamento y accesorios | Guía3D",
        "Compara varios productos lado a lado: ficha técnica completa y gráfico de valoración superpuesto.",
        "comparador.html", body, extra_head=schema,
    )


# ---------------------------------------------------------------- buying guide

def build_guide():
    impresoras = [p for p in PRODUCTOS if p["nicho"] == "impresora" and is_activo(p)]
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
    <p class="breadcrumb"><a href="index.html">Guía3D</a> / Guías / Mejor impresora 2026</p>
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
    schema = breadcrumb_jsonld([("Guía3D", "index.html"), ("Guías", None), ("Mejor impresora 2026", None)])
    schema += article_jsonld(
        "Mejor impresora 3D para empezar 2026",
        "Guía de compra: qué impresora 3D elegir según tu presupuesto y tipo de uso.",
        "guia-mejor-impresora-2026.html",
    )  # datePublished real desconocida (contenido preexistente) -> se omite, no se inventa
    return page_shell(
        "Mejor impresora 3D para empezar 2026 | Guía3D",
        "Guía de compra: qué impresora 3D elegir según tu presupuesto y tipo de uso, con nuestra selección comparada.",
        "guia-mejor-impresora-2026.html", body, extra_head=schema,
    )


# ---------------------------------------------------------------- ofertas

def build_ofertas():
    ofertas = [p for p in PRODUCTOS if is_activo(p) and p.get("discountedPrice") is not None and p.get("retailPrice") is not None and p["discountedPrice"] < p["retailPrice"]]
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
    schema = breadcrumb_jsonld([("Guía3D", "index.html"), ("Ofertas", None)])
    return page_shell(
        "Ofertas en impresoras 3D, filamento y accesorios | Guía3D",
        "Productos de impresión 3D con descuento respecto a su precio habitual en Amazon.es.",
        "ofertas.html", body, extra_head=schema,
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


# ---------------------------------------------------------------- artículos (comparativas y guías de compra)

def producto(pid):
    for p in PRODUCTOS:
        if p["id"] == pid:
            return p
    raise KeyError(pid)


ARTICULOS = []  # se rellena con cada build_art_*(); (slug, title_seo) para sitemap/hub


def registrar(slug, title_seo):
    ARTICULOS.append((slug, title_seo))


def mini_card_html(p):
    return f"""<a class="more-card" href="{slug_ficha(p)}">
    {media_html(p, css_class="guide-card-icon")}
    <h3>{esc(p["name"])}</h3>
    <p>{esc(p.get("destacado_editorial") or "")}</p>
  </a>"""


def related_section(products, title="Alternativas relacionadas"):
    cards = "\n".join(mini_card_html(p) for p in products)
    return f"""<section class="more-section">
      <h2>{esc(title)}</h2>
      <div class="more-grid">{cards}</div>
    </section>"""


def quick_answer(html_text):
    return f'<div class="demo-banner" style="background:var(--surface-soft);border-color:var(--border);"><strong>Respuesta rápida:</strong> {html_text}</div>'


def article_page(slug, title, meta_desc, breadcrumb_items, h1, hero_sub, prose_html, extra_schema=""):
    schema = breadcrumb_jsonld(breadcrumb_items)
    schema += article_jsonld(title, meta_desc, slug, datetime.date.today().isoformat())
    schema += extra_schema
    crumbs = " / ".join(
        f'<a href="{p}">{esc(n)}</a>' if p else esc(n) for n, p in breadcrumb_items
    )
    body = f"""<main id="contenido">
  <section class="page-hero container-wide">
    <p class="breadcrumb">{crumbs}</p>
    <h1>{esc(h1)}</h1>
    <p class="hero-sub">{esc(hero_sub)}</p>
  </section>
  <div class="article-layout container-wide">
    <div class="prose">
      {prose_html}
    </div>
    <aside class="sidebar-ad-slot" aria-label="Publicidad">
      {ad_slot_html(sidebar=True)}
    </aside>
  </div>
  {ad_slot_html()}
</main>"""
    registrar(slug, title)
    return page_shell(title, meta_desc, slug, body, extra_head=schema)


def spec_diff_table(products, fields):
    """fields: lista de (campo, etiqueta, unidad, mejor). products: lista de dicts producto."""
    head = "<tr><th>Especificación</th>" + "".join(f"<th>{esc(p['name'])}</th>" for p in products) + "</tr>"
    rows = ""
    for field, label, unit, _group, better in fields:
        vals = [p.get(field) for p in products]
        best_idx = None
        nums = [v for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if better and nums:
            target = max(nums) if better == "max" else min(nums)
            best_idx = [i for i, v in enumerate(vals) if v == target]
        cells = ""
        for i, v in enumerate(vals):
            disp = fmt_val(v, unit)
            cls = ' class="is-best"' if best_idx and i in best_idx else ""
            cells += f"<td{cls}>{esc(disp)}</td>"
        rows += f"<tr><th scope=\"row\">{esc(label)}</th>{cells}</tr>"
    return f'<div class="compare-table-wrap"><table class="compare-table"><thead>{head}</thead><tbody>{rows}</tbody></table></div>'


def precio_frase(p):
    return fmt_eur(p.get("discountedPrice") if p.get("discountedPrice") is not None else p.get("retailPrice"))


# ---- 1. mejor impresora 3D para principiantes -----------------------------

def build_art_principiantes():
    ender = producto("creality-ender-3-v3-se")
    adv = producto("flashforge-adventurer-5m")
    prose = f"""
      {quick_answer(f'Para empezar sin gastar mucho, la <a href="{slug_ficha(ender)}">{esc(ender["name"])}</a> ({precio_frase(ender)}) es la más sencilla de nuestro catálogo por precio: nivelación automática y montaje rápido. Si el presupuesto da para más, la <a href="{slug_ficha(adv)}">{esc(adv["name"])}</a> ({precio_frase(adv)}) tiene la puntuación de facilidad de uso más alta ({adv["score_facilidad_uso"]}/10) al venir cerrada y prácticamente lista de caja.')}

      <h2>Qué mirar si nunca has impreso en 3D</h2>
      <ul>
        <li><strong>Auto-nivelado:</strong> evita el ajuste manual de la cama, la causa más habitual de que las primeras impresiones fallen.</li>
        <li><strong>Extrusor directo</strong> (frente a bowden): empuja el filamento con más precisión, sobre todo con materiales flexibles.</li>
        <li><strong>Comunidad y repuestos:</strong> Creality y FlashForge tienen pieza de repuesto y tutoriales abundantes en español.</li>
        <li><strong>Cámara cerrada:</strong> no es imprescindible para PLA, pero ayuda si más adelante imprimes PETG.</li>
      </ul>

      <h2>Nuestras dos recomendaciones, según especificaciones</h2>
      {spec_diff_table([ender, adv], SPEC_FIELDS["impresora"])}
      <p class="radar-note">Valoraciones editoriales de 0 a 10 calculadas a partir de las especificaciones reales de cada producto, comparables solo entre impresoras de este catálogo. Metodología en <a href="como-elegimos.html">cómo elegimos</a>.</p>

      <h3>{esc(ender["name"])}: para quién es</h3>
      <p>{esc(ender.get("ideal_para") or "")}</p>
      <h3>{esc(adv["name"])}: para quién es</h3>
      <p>{esc(adv.get("ideal_para") or "")}</p>

      <p style="margin-top:1.4rem;">{comparar_cta_html("impresora", [ender["id"], adv["id"]], "Comparar Ender-3 V3 SE vs Adventurer 5M en el comparador →")}</p>
      <p class="aviso-afiliados">Los botones "Ver en Amazon" son enlaces de afiliado: si compras a través de ellos, podemos recibir una comisión sin coste extra para ti.</p>

      {related_section([producto("flashforge-ad5x")], "También te puede interesar")}

      <section class="faq-section" style="margin-top:2rem;">
        <h2>Preguntas frecuentes</h2>
        <div class="faq-list">
          <details class="faq-item"><summary>¿Necesito calibrar la impresora si tiene auto-nivelado?</summary><p>El auto-nivelado resuelve la nivelación de la cama, pero conviene ajustar el offset del eje Z y calibrar el slicer (Cura, Orca Slicer) en las primeras impresiones para sacarle el máximo partido, según indican varias reseñas de estos modelos.</p></details>
          <details class="faq-item"><summary>¿Puedo imprimir PETG o solo PLA como principiante?</summary><p>Ambos modelos admiten PETG y TPU además de PLA, según ficha técnica. El PLA sigue siendo el más fácil para empezar por su temperatura de impresión más baja.</p></details>
        </div>
      </section>
    """
    return article_page(
        "mejor-impresora-3d-para-principiantes.html",
        "Mejor impresora 3D para principiantes en 2026 | Guía3D",
        "Qué impresora 3D elegir si nunca has impreso antes: comparativa de facilidad de uso entre los modelos de nuestro catálogo, con specs reales.",
        [("Guía3D", "index.html"), ("Guías", "guia-mejor-impresora-2026.html"), ("Mejor impresora 3D para principiantes", None)],
        "Mejor impresora 3D para principiantes",
        "Comparamos facilidad de uso, auto-nivelado y montaje entre las impresoras de nuestro catálogo, según sus especificaciones reales.",
        prose,
    )


# ---- 2 y 3. mejores impresoras por presupuesto -----------------------------

def build_art_presupuesto(limite_eur, slug, related_limite=None):
    candidatas = [p for p in PRODUCTOS if p["nicho"] == "impresora" and is_activo(p)
                  and (p.get("discountedPrice") or p.get("retailPrice") or 9e9) <= limite_eur]
    siguiente = [p for p in PRODUCTOS if p["nicho"] == "impresora" and is_activo(p)
                 and (p.get("discountedPrice") or p.get("retailPrice") or 0) > limite_eur]
    siguiente.sort(key=lambda p: p.get("discountedPrice") or p.get("retailPrice") or 9e9)

    if len(candidatas) == 1:
        p = candidatas[0]
        honesto = (f'<p><strong>Aviso de transparencia:</strong> ahora mismo, en nuestro catálogo, solo tenemos '
                   f'una impresora que cueste {limite_eur}€ o menos: la <a href="{slug_ficha(p)}">{esc(p["name"])}</a> '
                   f'a {precio_frase(p)}. Preferimos decírtelo claramente en vez de rellenar la lista con productos '
                   f'que no vendemos. Iremos añadiendo más modelos en este rango a medida que los incorporemos.</p>')
        pick_html = f"""<div class="catalog-grid">{product_card_html(p)}</div>"""
    else:
        honesto = ""
        pick_html = f'<div class="catalog-grid">{"".join(product_card_html(p) for p in candidatas)}</div>'

    sig_html = ""
    if siguiente:
        s = siguiente[0]
        precio_s = s.get("discountedPrice") or s.get("retailPrice") or 0
        stretch_pct = (precio_s - limite_eur) / limite_eur if limite_eur else 1
        if candidatas and stretch_pct <= 0.15:
            # está lo bastante cerca del límite como para ser una decisión real de "¿estiro o no?"
            base = candidatas[0]
            diff_eur = round(precio_s - limite_eur)
            sig_html = (f'<h2>¿Merece la pena estirar {diff_eur}€ más?</h2>'
                        f'<p>La <a href="{slug_ficha(s)}">{esc(s["name"])}</a> cuesta {precio_frase(s)} — solo '
                        f'{diff_eur}€ más que el límite de esta página. Antes de decidir, esto es lo que cambia respecto '
                        f'a la {esc(base["name"])}:</p>'
                        f'{spec_diff_table([base, s], SPEC_FIELDS["impresora"])}'
                        f'<p style="margin-top:1.4rem;">{comparar_cta_html("impresora", [base["id"], s["id"]], "Comparar ambas en el comparador →")}</p>')
        else:
            sig_html = (f'<h2>Si puedes estirar el presupuesto un poco más</h2>'
                        f'<p>Por encima de los {limite_eur}€, la siguiente opción de nuestro catálogo es la '
                        f'<a href="{slug_ficha(s)}">{esc(s["name"])}</a>, a {precio_frase(s)} — bastante por encima '
                        f'de este rango, así que solo tiene sentido si tu presupuesto real es mayor. '
                        f'{esc(s.get("destacado_editorial") or "")}</p>')

    prose = f"""
      {quick_answer(f'{"Nuestra recomendación por debajo de " + str(limite_eur) + "€ es la " + esc(candidatas[0]["name"]) + " (" + precio_frase(candidatas[0]) + ")." if candidatas else "Ahora mismo no tenemos ninguna impresora en este rango de precio en catálogo."}')}

      {honesto}
      <h2>Impresoras por {limite_eur}€ o menos en nuestro catálogo</h2>
      {pick_html if candidatas else '<p>Vuelve pronto — iremos añadiendo modelos en este rango.</p>'}

      {sig_html}

      <h2>Qué esperar por debajo de {limite_eur}€</h2>
      <p>En esta franja de precio, lo habitual es encontrar impresoras FDM de estructura abierta, cama de alrededor de 220×220 mm y auto-nivelado en los modelos más recientes. No suele haber cámara cerrada ni impresión multicolor — esas funciones aparecen a partir de la gama media-alta.</p>
    """
    return article_page(
        slug,
        f"Mejores impresoras 3D por menos de {limite_eur} euros | Guía3D",
        f"Qué impresora 3D comprar con un presupuesto de {limite_eur}€ o menos, con precios reales y actualizados de nuestro catálogo.",
        [("Guía3D", "index.html"), ("Impresoras", "categoria-impresoras.html"), (f"Menos de {limite_eur}€", None)],
        f"Mejores impresoras 3D por menos de {limite_eur} euros",
        f"Qué impresora 3D comprar con {limite_eur}€ o menos, con precios y especificaciones reales de nuestro catálogo.",
        prose,
    )


# ---- 4. mejor impresora calidad-precio -------------------------------------

def build_art_calidad_precio():
    impresoras = sorted([p for p in PRODUCTOS if p["nicho"] == "impresora" and is_activo(p)],
                         key=lambda p: p.get("score_calidad_precio") or 0, reverse=True)
    ganadora = impresoras[0]
    prose = f"""
      {quick_answer(f'Según nuestras puntuaciones editoriales, la impresora con mejor relación calidad-precio del catálogo es la <a href="{slug_ficha(ganadora)}">{esc(ganadora["name"])}</a> ({ganadora["score_calidad_precio"]}/10 en calidad-precio, {precio_frase(ganadora)}).')}

      <h2>Ranking por calidad-precio</h2>
      <div class="catalog-grid">{"".join(product_card_html(p) for p in impresoras)}</div>
      <p class="radar-note">La puntuación de calidad-precio es un cálculo editorial nuestro (specs reales frente a precio), no una puntuación oficial de Amazon. Metodología en <a href="como-elegimos.html">cómo elegimos</a>.</p>

      <h2>Comparativa de especificaciones</h2>
      {spec_diff_table(impresoras, SPEC_FIELDS["impresora"])}

      <p style="margin-top:1.4rem;">{comparar_cta_html("impresora", [p["id"] for p in impresoras], "Comparar las tres en el comparador →")}</p>
      <p class="aviso-afiliados">Los botones "Ver en Amazon" son enlaces de afiliado: si compras a través de ellos, podemos recibir una comisión sin coste extra para ti.</p>
    """
    return article_page(
        "mejor-impresora-3d-calidad-precio.html",
        "Mejor impresora 3D calidad-precio en 2026 | Guía3D",
        "Ranking de impresoras 3D por relación calidad-precio, con puntuación editorial calculada a partir de especificaciones reales.",
        [("Guía3D", "index.html"), ("Impresoras", "categoria-impresoras.html"), ("Mejor calidad-precio", None)],
        "Mejor impresora 3D calidad-precio",
        "Comparamos las impresoras de nuestro catálogo por relación entre especificaciones y precio.",
        prose,
        extra_schema=itemlist_jsonld(impresoras, name="Mejor impresora 3D calidad-precio"),
    )


# ---- 5. qué impresora 3D comprar (decisión rápida) -------------------------

def build_art_que_comprar():
    ender = producto("creality-ender-3-v3-se")
    adv = producto("flashforge-adventurer-5m")
    ad5x = producto("flashforge-ad5x")
    prose = f"""
      {quick_answer('Depende de tu presupuesto y de si quieres montarla y calibrarla o que venga lista de caja. Sigue el árbol de decisión de abajo, o compara los tres modelos directamente.')}

      <h2>Árbol de decisión rápido</h2>
      <ul>
        <li><strong>Presupuesto ajustado, no te importa calibrar un poco:</strong> <a href="{slug_ficha(ender)}">{esc(ender["name"])}</a> ({precio_frase(ender)}).</li>
        <li><strong>Quieres que funcione bien desde el primer intento, sin trastear:</strong> <a href="{slug_ficha(adv)}">{esc(adv["name"])}</a> ({precio_frase(adv)}), cerrada y con nivelación de un clic.</li>
        <li><strong>Quieres imprimir en varios colores sin comprar un AMS aparte:</strong> <a href="{slug_ficha(ad5x)}">{esc(ad5x["name"])}</a> ({precio_frase(ad5x)}), la única con módulo multicolor automático del catálogo.</li>
      </ul>

      <h2>Las tres, lado a lado</h2>
      {spec_diff_table([ender, adv, ad5x], SPEC_FIELDS["impresora"])}

      <p style="margin-top:1.4rem;">{comparar_cta_html("impresora", [ender["id"], adv["id"], ad5x["id"]], "Ver las tres en el comparador →")}</p>

      <h2>Si prefieres una guía más completa</h2>
      <p>Esta página es un atajo rápido. Para entender a fondo qué mirar en una impresora 3D (tamaño de cama, extrusor, materiales, etc.) antes de decidir, consulta <a href="como-elegir-tu-primera-impresora-3d.html">cómo elegir tu primera impresora 3D</a>.</p>
      <p class="aviso-afiliados">Los botones "Ver en Amazon" son enlaces de afiliado: si compras a través de ellos, podemos recibir una comisión sin coste extra para ti.</p>
    """
    return article_page(
        "que-impresora-3d-comprar.html",
        "Qué impresora 3D comprar en 2026: guía rápida | Guía3D",
        "Árbol de decisión rápido para elegir impresora 3D según presupuesto y tipo de uso, con las tres impresoras de nuestro catálogo comparadas.",
        [("Guía3D", "index.html"), ("Impresoras", "categoria-impresoras.html"), ("Qué impresora comprar", None)],
        "Qué impresora 3D comprar",
        "Un árbol de decisión rápido: presupuesto, facilidad de uso o multicolor, y a qué modelo te lleva cada uno.",
        prose,
    )


# ---- 6/7. merece la pena X -------------------------------------------------

def build_art_merece_la_pena(pid, slug):
    p = producto(pid)
    alternativas = [q for q in PRODUCTOS if q["nicho"] == p["nicho"] and q["id"] != pid and is_activo(q)]
    pros = "".join(f"<li>{esc(x)}</li>" for x in (p.get("pros") or []))
    contras = "".join(f"<li>{esc(x)}</li>" for x in (p.get("contras") or []))
    prose = f"""
      {quick_answer(f'Sobre el papel, sí, dentro de su rango de precio ({precio_frase(p)}): {esc(p.get("destacado_editorial") or "")} Su punto débil según las reseñas: {esc((p.get("contras") or [""])[0])}')}

      <h2>Lo que dice la ficha técnica</h2>
      <p>{p.get("cuerpo_editorial") or ""}</p>

      <h2>Ventajas, según especificaciones y reseñas</h2>
      <ul class="pros">{pros}</ul>
      <h2>Desventajas, según especificaciones y reseñas</h2>
      <ul class="contras">{contras}</ul>

      <h2>¿Para quién merece la pena?</h2>
      <p>{esc(p.get("ideal_para") or "")}</p>

      <h2>Lo que dicen los compradores</h2>
      <p>{esc(p.get("resenas_resumen") or "")}</p>
      <p class="radar-note">Resumen de reseñas públicas en Amazon.es en el momento de la captura ({esc(p.get("precio_fecha") or "")}). No hemos probado físicamente esta unidad — este resumen se basa en documentación del fabricante y reseñas verificadas de compradores.</p>

      <p style="margin-top:1.4rem;">{buy_button_html(p, extra_class="btn-repeat")}</p>
      <p class="aviso-afiliados">Como Afiliados de Amazon, obtenemos ingresos por las compras que cumplen los requisitos aplicables.</p>

      {related_section(alternativas) if alternativas else ""}
    """
    return article_page(
        slug,
        f"¿Merece la pena la {p['name']}? | Guía3D",
        f"Analizamos si la {p['name']} merece la pena según su ficha técnica, precio y reseñas reales de Amazon.es — sin haberla probado físicamente.",
        [("Guía3D", "index.html"), (NICHO_LABEL[p["nicho"]], NICHO_SLUG_PAGE[p["nicho"]]), (f"¿Merece la pena la {p['name']}?", None)],
        f"¿Merece la pena la {p['name']}?",
        "Análisis basado en ficha técnica del fabricante y reseñas verificadas de compradores en Amazon.es. No la hemos probado físicamente.",
        prose,
    )


# ---- 8. mejor filamento PLA calidad-precio ---------------------------------

def build_art_pla():
    pla = [p for p in PRODUCTOS if p["nicho"] == "filamento" and is_activo(p) and p.get("material") == "PLA"]
    unico = len(pla) == 1
    destacado = pla[0] if pla else None
    honesto = ""
    if unico:
        honesto = (f'<p><strong>Aviso de transparencia:</strong> ahora mismo solo tenemos un filamento PLA en catálogo: '
                   f'el <a href="{slug_ficha(destacado)}">{esc(destacado["name"])}</a>. Te lo presentamos con sus pros y contras reales '
                   f'(incluida una advertencia real de una reseña sobre consistencia de diámetro), y añadimos criterios generales '
                   f'para que sepas qué mirar si comparas con otras marcas.</p>')
    prose = f"""
      {quick_answer(f'{"Nuestra única recomendación en catálogo ahora mismo es el " + esc(destacado["name"]) + " (" + precio_frase(destacado) + "/kg), fabricado en España." if destacado else "Todavía no tenemos filamento PLA en catálogo."}')}

      {honesto}

      {f'<div class="catalog-grid">{product_card_html(destacado)}</div>' if destacado else ""}

      <h2>Qué mirar en un PLA calidad-precio, en general</h2>
      <ul>
        <li><strong>Tolerancia de diámetro:</strong> cuanto más ajustada (±0,02-0,03 mm es buena), menos atascos y más consistencia entre bobinas.</li>
        <li><strong>Temperatura de impresión indicada:</strong> un rango amplio (190-230°C) suele señalar un PLA más tolerante a distintas impresoras.</li>
        <li><strong>Origen y trazabilidad:</strong> filamento fabricado en la UE con certificaciones ISO suele tener control de calidad más consistente lote a lote.</li>
        <li><strong>Reseñas verificadas de compradores</strong> antes que promesas de marketing en el envase.</li>
      </ul>

      {(f'<h2>Ficha técnica</h2>{spec_diff_table([destacado], SPEC_FIELDS["filamento"])}') if destacado else ''}

      {(f'<p style="margin-top:1.4rem;">{buy_button_html(destacado, extra_class="btn-repeat")}</p><p class="aviso-afiliados">Como Afiliados de Amazon, obtenemos ingresos por las compras que cumplen los requisitos aplicables.</p>') if destacado else ''}
    """
    return article_page(
        "mejor-filamento-pla-calidad-precio.html",
        "Mejor filamento PLA calidad-precio | Guía3D",
        "Qué filamento PLA comprar por relación calidad-precio: nuestra recomendación en catálogo y qué mirar en general al elegir uno.",
        [("Guía3D", "index.html"), ("Filamento", "categoria-filamento.html"), ("Mejor PLA calidad-precio", None)],
        "Mejor filamento PLA calidad-precio",
        "Nuestra recomendación en catálogo y los criterios generales para elegir un buen PLA sin sorpresas.",
        prose,
    )


# ---- 9. accesorios imprescindibles -----------------------------------------

def build_art_accesorios():
    accesorios = [p for p in PRODUCTOS if p["nicho"] == "accesorio" and is_activo(p)]
    ids_catalogo = {p.get("tipo_accesorio", "").lower() for p in accesorios}
    prose = f"""
      {quick_answer('Boquillas de repuesto y un calibre digital son los dos accesorios que más se repiten entre quienes ya llevan un tiempo imprimiendo — y son los dos que tenemos en catálogo con enlace de compra. Debajo añadimos otras categorías recomendadas en general, aunque todavía no tengamos un producto propio para cada una.')}

      <h2>En nuestro catálogo, con enlace de compra</h2>
      <div class="catalog-grid">{"".join(product_card_html(p) for p in accesorios)}</div>

      <h2>Otras categorías recomendadas en general</h2>
      <p>Estas categorías las recomienda de forma habitual la comunidad de impresión 3D, aunque todavía no tenemos un producto concreto en catálogo para cada una — las iremos añadiendo con enlace de afiliado real cuando las tengamos:</p>
      <ul>
        <li><strong>Espátula para despegar piezas</strong> de la cama sin dañarla.</li>
        <li><strong>Caja seca o gel de sílice</strong> para guardar el filamento, sobre todo PLA e higroscópicos como el nylon.</li>
        <li><strong>Alicates de corte fino</strong> para retirar soportes y rebabas.</li>
        <li><strong>Base de nivelación / hoja de acero PEI de repuesto</strong>, útil cuando la original se desgasta.</li>
      </ul>

      <p style="margin-top:1.4rem;"><a href="categoria-accesorios.html" style="color:var(--accent);font-weight:700;">→ Ver todos los accesorios en catálogo</a></p>
      <p class="aviso-afiliados">Los botones "Ver en Amazon" son enlaces de afiliado: si compras a través de ellos, podemos recibir una comisión sin coste extra para ti.</p>
    """
    return article_page(
        "accesorios-imprescindibles-para-impresora-3d.html",
        "Accesorios imprescindibles para tu impresora 3D | Guía3D",
        "Qué accesorios comprar para tu impresora 3D: los que tenemos en catálogo con enlace de compra, y otras categorías recomendadas en general.",
        [("Guía3D", "index.html"), ("Accesorios", "categoria-accesorios.html"), ("Imprescindibles", None)],
        "Accesorios imprescindibles para tu impresora 3D",
        "Los accesorios que de verdad se usan, con los que tenemos en catálogo y las categorías que iremos añadiendo.",
        prose,
        extra_schema=itemlist_jsonld(accesorios, name="Accesorios imprescindibles") if accesorios else "",
    )


# ---- hub: cómo elegir tu primera impresora 3D ------------------------------

def build_hub_como_elegir():
    prose = f"""
      <p>Esta es la guía completa: si es la primera vez que compras una impresora 3D, empieza aquí. Si ya sabes lo que buscas, ve directo a nuestras <a href="#comparativas">comparativas</a> o al <a href="comparador.html">comparador</a>.</p>

      <h2>1. FDM o resina</h2>
      <p>Para la gran mayoría de gente que empieza, FDM (filamento fundido) es la opción correcta: el material cuesta menos por pieza, no requiere manipular resina líquida ni alcohol isopropílico para el postprocesado, y las piezas son más resistentes mecánicamente. La resina da más detalle (útil para miniaturas), pero tiene más mantenimiento. Todo nuestro catálogo actual es FDM.</p>

      <h2>2. Tamaño de cama</h2>
      <p>220×220 mm cubre la inmensa mayoría de piezas domésticas y de repuesto. Solo necesitas más si ya sabes que vas a imprimir piezas grandes (cascos, soportes grandes, etc.).</p>

      <h2>3. Auto-nivelado</h2>
      <p>No es obligatorio, pero evita la causa más habitual de que fallen las primeras impresiones: una cama mal nivelada. Todas las impresoras de nuestro catálogo lo incluyen.</p>

      <h2>4. Extrusor directo vs bowden</h2>
      <p>El extrusor directo empuja el filamento justo encima de la boquilla, con más precisión — mejor para filamentos flexibles como el TPU. El bowden lo empuja desde más lejos con un tubo; el cabezal pesa menos pero el control es algo menos preciso. Las tres impresoras de nuestro catálogo usan extrusor directo.</p>

      <h2>5. Cámara abierta o cerrada</h2>
      <p>Para PLA no importa. Para PETG o materiales con fibra de carbono, una cámara cerrada da resultados más estables al evitar corrientes de aire.</p>

      <h2>6. Presupuesto: qué esperar en cada franja</h2>
      <ul>
        <li><strong>Hasta 200€:</strong> FDM abierta, cama ~220×220 mm, auto-nivelado en los modelos recientes.</li>
        <li><strong>200-350€:</strong> empiezan a aparecer estructuras cerradas (CoreXY) y velocidades más altas.</li>
        <li><strong>350€+:</strong> impresión multicolor, cámaras más grandes, más automatización.</li>
      </ul>

      <h2 id="comparativas">Sigue explorando</h2>
      <div class="more-grid">
        <a class="more-card" href="mejor-impresora-3d-para-principiantes.html"><h3>Mejor impresora 3D para principiantes</h3><p>Nuestra recomendación si nunca has impreso antes.</p></a>
        <a class="more-card" href="que-impresora-3d-comprar.html"><h3>Qué impresora 3D comprar</h3><p>Árbol de decisión rápido por presupuesto y uso.</p></a>
        <a class="more-card" href="mejor-impresora-3d-calidad-precio.html"><h3>Mejor impresora 3D calidad-precio</h3><p>Ranking por relación entre specs y precio.</p></a>
        <a class="more-card" href="mejores-impresoras-3d-por-menos-de-200-euros.html"><h3>Menos de 200€</h3><p>Qué comprar con presupuesto ajustado.</p></a>
        <a class="more-card" href="mejores-impresoras-3d-por-menos-de-300-euros.html"><h3>Menos de 300€</h3><p>Qué comprar con algo más de margen.</p></a>
        <a class="more-card" href="categoria-impresoras.html"><h3>Ver todas las impresoras</h3><p>Catálogo completo con fichas y specs.</p></a>
        <a class="more-card" href="comparador.html"><h3>Comparador</h3><p>Enfrenta varios modelos lado a lado.</p></a>
        <a class="more-card" href="categoria-filamento.html"><h3>Filamento</h3><p>PLA y qué mirar al elegirlo.</p></a>
        <a class="more-card" href="categoria-accesorios.html"><h3>Accesorios</h3><p>Lo que de verdad hace falta para imprimir sin sobresaltos.</p></a>
      </div>
    """
    return article_page(
        "como-elegir-tu-primera-impresora-3d.html",
        "Cómo elegir tu primera impresora 3D | Guía3D",
        "FDM o resina, tamaño de cama, auto-nivelado y presupuesto: qué mirar antes de comprar tu primera impresora 3D, con enlaces a todas nuestras comparativas.",
        [("Guía3D", "index.html"), ("Guías", "guia-mejor-impresora-2026.html"), ("Cómo elegir tu primera impresora 3D", None)],
        "Cómo elegir tu primera impresora 3D",
        "Los criterios que de verdad importan, explicados sin tecnicismos, con enlaces a todas nuestras comparativas y fichas.",
        prose,
    )


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
        "como-elegimos.html", body, extra_head="",
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


# ---------------------------------------------------------------- sitemap.xml

def build_sitemap(static_paths, product_paths, article_paths):
    today = datetime.date.today().isoformat()

    def url(path, priority, changefreq="monthly"):
        return (f"  <url><loc>{SITE_URL}/{path}</loc><lastmod>{today}</lastmod>"
                f"<changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>")

    entries = [url("index.html", "1.0", "weekly")]
    entries += [url(p, "0.8", "weekly") for p in static_paths]
    entries += [url(p, "0.9", "weekly") for p in article_paths]
    entries += [url(p, "0.7", "monthly") for p in product_paths]
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(entries) + "\n</urlset>\n")
    return xml


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

    ARTICULOS.clear()
    write("mejor-impresora-3d-para-principiantes.html", build_art_principiantes())
    write("mejores-impresoras-3d-por-menos-de-200-euros.html", build_art_presupuesto(200, "mejores-impresoras-3d-por-menos-de-200-euros.html"))
    write("mejores-impresoras-3d-por-menos-de-300-euros.html", build_art_presupuesto(300, "mejores-impresoras-3d-por-menos-de-300-euros.html"))
    write("mejor-impresora-3d-calidad-precio.html", build_art_calidad_precio())
    write("que-impresora-3d-comprar.html", build_art_que_comprar())
    write("merece-la-pena-ender-3-v3-se.html", build_art_merece_la_pena("creality-ender-3-v3-se", "merece-la-pena-ender-3-v3-se.html"))
    write("mejor-filamento-pla-calidad-precio.html", build_art_pla())
    write("accesorios-imprescindibles-para-impresora-3d.html", build_art_accesorios())
    write("como-elegir-tu-primera-impresora-3d.html", build_hub_como_elegir())

    static_paths = [NICHO_SLUG_PAGE[n] for n in NICHOS] + ["comparador.html", "guia-mejor-impresora-2026.html", "ofertas.html", "como-elegimos.html"]
    product_paths = [slug_ficha(p) for p in PRODUCTOS if is_activo(p) and not p.get("isDemo")]
    article_paths = [slug for slug, _ in ARTICULOS]
    write("sitemap.xml", build_sitemap(static_paths, product_paths, article_paths))

    print(f"Listo: {len(PRODUCTOS)} productos, {len(NICHOS)} categorías, {len(ARTICULOS)} artículos, "
          f"{3 + len(NICHOS) + len(PRODUCTOS) + 3 + len(ARTICULOS) + 1} páginas HTML + sitemap.")


if __name__ == "__main__":
    main()
