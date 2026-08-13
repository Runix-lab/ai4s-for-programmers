#!/usr/bin/env python3
"""Static site generator for ai4s.runixcloud.io.

Stdlib only, no build dependencies. Reads page metadata from content/pages.py and
body fragments from content/*.html, then emits a fully static, SEO-complete site
into dist/.

    python3 build.py            # build into dist/
    python3 build.py --check    # build into a temp dir and diff against dist/

The --check mode is what CI runs: it fails when dist/ is stale relative to the
sources, which is the only thing keeping a committed build directory honest.
"""

from __future__ import annotations

import argparse
import filecmp
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
LABS = ROOT / "labs"
DIST = ROOT / "dist"

sys.path.insert(0, str(CONTENT))
import pages as P  # noqa: E402  (content/pages.py)

ORIGIN = P.ORIGIN


# ---------------------------------------------------------------- helpers


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def url_for(slug: str) -> str:
    """Absolute URL for a page slug. The empty slug is the site root."""
    return f"{ORIGIN}/" if not slug else f"{ORIGIN}/{slug}/"


def href(slug: str) -> str:
    return "/" if not slug else f"/{slug}/"


def read_fragment(name: str) -> str:
    return (CONTENT / f"{name}.html").read_text(encoding="utf-8").strip()


# ---------------------------------------------------------------- SEO blocks


def json_ld(page: dict, index: dict) -> str:
    """Emit the structured data graph for one page.

    Every page carries BreadcrumbList; the type-specific node is layered on top.
    Google needs the breadcrumb to render the trail in results, and the Course /
    LearningResource nodes are what make the lesson pages eligible for the
    course-listing treatment.
    """
    blocks: list[dict] = []

    crumbs = [{"name": "首页", "slug": ""}]
    if page.get("parent") is not None:
        parent = index[page["parent"]]
        crumbs.append({"name": parent["crumb"], "slug": parent["slug"]})
    if page["slug"]:
        crumbs.append({"name": page["crumb"], "slug": page["slug"]})

    blocks.append({
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": c["name"],
                "item": url_for(c["slug"]),
            }
            for i, c in enumerate(crumbs)
        ],
    })

    kind = page.get("schema")
    if kind == "Course":
        blocks.append({
            "@type": "Course",
            "@id": url_for(page["slug"]) + "#course",
            "name": P.COURSE_NAME,
            "description": page["desc"],
            "url": url_for(page["slug"]),
            "inLanguage": "zh-CN",
            "isAccessibleForFree": True,
            "teaches": P.TEACHES,
            "educationalLevel": "Beginner",
            "provider": {"@type": "Organization", "name": P.ORG, "url": P.ORG_URL},
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
                "category": "Free",
                "availability": "https://schema.org/InStock",
            },
            "hasCourseInstance": {
                "@type": "CourseInstance",
                "courseMode": "online",
                "courseWorkload": "PT10H",
                "inLanguage": "zh-CN",
            },
        })
    elif kind == "Lesson":
        blocks.append({
            "@type": "LearningResource",
            "@id": url_for(page["slug"]) + "#lesson",
            "name": page["h1"],
            "description": page["desc"],
            "url": url_for(page["slug"]),
            "inLanguage": "zh-CN",
            "learningResourceType": "Lesson",
            "educationalLevel": "Beginner",
            "timeRequired": page.get("duration", "PT60M"),
            "isPartOf": {"@type": "Course", "@id": url_for("course") + "#course"},
            "teaches": page.get("teaches", []),
            "isAccessibleForFree": True,
            "author": {"@type": "Organization", "name": P.ORG, "url": P.ORG_URL},
        })
    elif kind == "Article":
        blocks.append({
            "@type": "Article",
            "headline": page["h1"],
            "description": page["desc"],
            "url": url_for(page["slug"]),
            "inLanguage": "zh-CN",
            "author": {"@type": "Organization", "name": P.ORG, "url": P.ORG_URL},
            "publisher": {"@type": "Organization", "name": P.ORG, "url": P.ORG_URL},
            "datePublished": P.PUBLISHED,
            "dateModified": P.UPDATED,
        })

    if page.get("faq"):
        blocks.append({
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
                for q, a in page["faq"]
            ],
        })

    if page["slug"] == "":
        blocks.append({
            "@type": "WebSite",
            "@id": ORIGIN + "/#website",
            "name": P.SITE_NAME,
            "url": ORIGIN + "/",
            "inLanguage": "zh-CN",
            "publisher": {"@type": "Organization", "name": P.ORG, "url": P.ORG_URL},
        })

    graph = {"@context": "https://schema.org", "@graph": blocks}
    return json.dumps(graph, ensure_ascii=False, separators=(",", ":"))


def head_block(page: dict, index: dict) -> str:
    slug = page["slug"]
    canonical = url_for(slug)
    og_image = f"{ORIGIN}/assets/og/{page.get('og', 'default')}.png"

    # hreflang is only emitted where a translation genuinely exists. Declaring an
    # alternate that 404s is worse than declaring none at all.
    alt = ""
    if page.get("lang_alt"):
        other = index[page["lang_alt"]]
        this_lang = page.get("lang", "zh-Hans")
        other_lang = other.get("lang", "zh-Hans")
        alt = (
            f'\n<link rel="alternate" hreflang="{this_lang}" href="{canonical}">'
            f'\n<link rel="alternate" hreflang="{other_lang}" href="{url_for(other["slug"])}">'
            f'\n<link rel="alternate" hreflang="x-default" href="{url_for(other["slug"] if other_lang.startswith("en") else slug)}">'
        )

    kw = ", ".join(page.get("keywords", []))
    kw_tag = f'\n<meta name="keywords" content="{esc(kw)}">' if kw else ""

    prev_next = ""
    if page.get("prev") is not None:
        prev_next += f'\n<link rel="prev" href="{url_for(index[page["prev"]]["slug"])}">'
    if page.get("next") is not None:
        prev_next += f'\n<link rel="next" href="{url_for(index[page["next"]]["slug"])}">'

    return f"""<!doctype html>
<html lang="{page.get('lang', 'zh-Hans')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(page['title'])}</title>
<meta name="description" content="{esc(page['desc'])}">{kw_tag}
<link rel="canonical" href="{canonical}">{alt}{prev_next}
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="author" content="{esc(P.ORG)}">
<meta property="og:type" content="{page.get('og_type', 'article')}">
<meta property="og:site_name" content="{esc(P.SITE_NAME)}">
<meta property="og:locale" content="{page.get('og_locale', 'zh_CN')}">
<meta property="og:title" content="{esc(page.get('og_title', page['title']))}">
<meta property="og:description" content="{esc(page['desc'])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(page.get('og_title', page['title']))}">
<meta name="twitter:description" content="{esc(page['desc'])}">
<meta name="twitter:image" content="{og_image}">
<meta name="theme-color" content="#f7f6f3" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#131519" media="(prefers-color-scheme:dark)">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="/favicon.ico" sizes="64x64">
<link rel="apple-touch-icon" href="/assets/favicon.png">
<link rel="stylesheet" href="/assets/style.css">
<link rel="sitemap" type="application/xml" href="/sitemap.xml">
<script type="application/ld+json">{json_ld(page, index)}</script>
</head>
<body>"""


# ---------------------------------------------------------------- chrome


def nav_block(page: dict) -> str:
    here = page["slug"]
    items = []
    for slug, label in P.NAV:
        cls = ' class="on"' if slug == here or (slug and here.startswith(slug + "/")) else ""
        items.append(f'<a href="{href(slug)}"{cls}>{esc(label)}</a>')
    # The mark is the course's own argument in miniature: one half indigo for
    # the biology side, one half green for the code side. Inlined rather than
    # linked so it paints with the first byte and matches the favicon exactly.
    logo = (
        # width/height are intrinsic on purpose: without them a stylesheet that
        # is slow or blocked leaves the mark filling the viewport. Same reason
        # the fills carry a literal fallback before the custom property.
        '<svg class="mark" viewBox="0 0 64 64" width="22" height="22" '
        'aria-hidden="true" focusable="false">'
        '<rect width="64" height="64" rx="14" fill="#2e3f8c" style="fill:var(--bio,#2e3f8c)"/>'
        '<path d="M32 0h18a14 14 0 0 1 14 14v36a14 14 0 0 1-14 14H32z" '
        'fill="#1c6b58" style="fill:var(--code,#1c6b58)"/>'
        '<path d="M20 44 L26 20 L32 44 M22.5 36 h7" stroke="#fff" stroke-width="3.6" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M44 22 v20" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/>'
        "</svg>"
    )
    return (
        '<a class="skip" href="#main">跳到正文</a>\n'
        '<div id="bar"></div>\n'
        '<nav aria-label="主导航"><div class="in">'
        f'<a class="brand" href="/">{logo}<b>AI4S</b><i>生物数据方向</i></a>{"".join(items)}'
        '<button id="theme" type="button" aria-label="切换深浅色">◐</button>'
        "</div></nav>"
    )


def crumb_block(page: dict, index: dict) -> str:
    if not page["slug"]:
        return ""
    parts = ['<a href="/">首页</a>']
    if page.get("parent") is not None:
        p = index[page["parent"]]
        parts.append(f'<a href="{href(p["slug"])}">{esc(p["crumb"])}</a>')
    parts.append(f"<span>{esc(page['crumb'])}</span>")
    return (
        '<nav class="crumb" aria-label="面包屑">' + '<i aria-hidden="true">/</i>'.join(parts) + "</nav>"
    )


def pager_block(page: dict, index: dict) -> str:
    prev_i, next_i = page.get("prev"), page.get("next")
    if prev_i is None and next_i is None:
        return ""
    out = ['<nav class="pager" aria-label="课程翻页">']
    if prev_i is not None:
        p = index[prev_i]
        out.append(f'<a class="p" href="{href(p["slug"])}" rel="prev"><small>上一节</small>{esc(p["crumb"])}</a>')
    else:
        out.append("<span></span>")
    if next_i is not None:
        n = index[next_i]
        out.append(f'<a class="n" href="{href(n["slug"])}" rel="next"><small>下一节</small>{esc(n["crumb"])}</a>')
    out.append("</nav>")
    return "".join(out)


FOOTER = f"""<footer>
<div class="fcol"><b>{esc(P.SITE_NAME)}</b>
<p>AI for Science 的<b>生物数据方向</b>：抗体与蛋白数据的采集、清洗与质量验证。
所有生物概念都映射到你已经懂的编程概念，每个知识点都配一个能跑的实验。<br>
内容免费，源码开放。</p></div>
<div class="fcol"><b>课程</b>
<a href="/study/">两天速成营</a><a href="/study/syllabus/">课程大纲</a><a href="/study/labs/">动手实验</a><a href="/study/quiz/">在线检验</a><a href="/study/exam/">结业考试</a></div>
<div class="fcol"><b>资源</b>
<a href="/study/glossary/">术语表</a><a href="/study/resources/">视频与资料</a><a href="/en/">English</a>
<a href="{P.REPO}" rel="noopener">GitHub 源码</a><a href="{P.ORG_URL}" rel="noopener">{esc(P.ORG)}</a></div>
<div class="fbot"><span>内容 CC BY-SA 4.0 · 代码 MIT · 最后更新 {P.UPDATED}</span>
<span>发现错误？<a href="{P.REPO}/issues" rel="noopener">提个 issue</a></span></div>
</footer>"""

def tail(page: dict) -> str:
    # quiz.js carries the whole 35-question bank, so it only ships to the pages
    # that actually render questions rather than riding along on every request.
    extra = '\n<script src="/assets/quiz.js" defer></script>' if page.get("quiz") else ""
    # cert.js must be parsed before quiz.js runs its grading handler, since the
    # quiz calls into the unlock hook that cert.js installs.
    if page.get("cert"):
        extra = '\n<script src="/assets/cert.js" defer></script>' + extra
    return f"""<script src="/assets/site.js" defer></script>{extra}
</body>
</html>
"""


# ---------------------------------------------------------------- render


def render(page: dict, index: dict) -> str:
    body = read_fragment(page["file"])
    hero = ""
    if page.get("h1"):
        badges = ""
        if page.get("badges"):
            badges = '<div class="badges">' + "".join(
                f"<span class=\"badge\">{b}</span>" for b in page["badges"]
            ) + "</div>"
        dek = f'<p class="dek">{page["dek"]}</p>' if page.get("dek") else ""
        eyebrow = f'<p class="eyebrow">{esc(page["eyebrow"])}</p>' if page.get("eyebrow") else ""
        hero = f"<header>{eyebrow}<h1>{page['h1']}</h1>{dek}{badges}</header>"

    return "\n".join([
        head_block(page, index),
        nav_block(page),
        '<div class="wrap">',
        crumb_block(page, index),
        '<main id="main">',
        hero,
        body,
        pager_block(page, index),
        "</main>",
        FOOTER,
        "</div>",
        tail(page),
    ])


# ---------------------------------------------------------------- sitemap etc.


def write_sitemap(out: Path, index: dict) -> None:
    urls = []
    for page in index.values():
        if page.get("noindex"):
            continue
        prio = page.get("priority", 0.6)
        urls.append(
            "  <url>\n"
            f"    <loc>{url_for(page['slug'])}</loc>\n"
            f"    <lastmod>{P.UPDATED}</lastmod>\n"
            f"    <changefreq>{page.get('changefreq', 'monthly')}</changefreq>\n"
            f"    <priority>{prio:.1f}</priority>\n"
            "  </url>"
        )
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n",
        encoding="utf-8",
    )

    (out / "robots.txt").write_text(
        "# https://www.robotstxt.org/robotstxt.html\n"
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "# AI crawlers are welcome — this material exists to be read and cited.\n"
        "User-agent: GPTBot\nAllow: /\n"
        "User-agent: ClaudeBot\nAllow: /\n"
        "User-agent: PerplexityBot\nAllow: /\n"
        "User-agent: Google-Extended\nAllow: /\n"
        "\n"
        f"Sitemap: {ORIGIN}/sitemap.xml\n",
        encoding="utf-8",
    )

    # Cloudflare Pages headers. Long-cache the fingerprint-free assets modestly;
    # HTML stays revalidated so a content fix goes live on the next request.
    (out / "_headers").write_text(
        "/*\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  X-Frame-Options: SAMEORIGIN\n"
        "  Permissions-Policy: geolocation=(), microphone=(), camera=()\n"
        "\n"
        "/assets/*\n"
        "  Cache-Control: public, max-age=3600, stale-while-revalidate=86400\n"
        "\n"
        "/*.html\n"
        "  Cache-Control: public, max-age=0, must-revalidate\n",
        encoding="utf-8",
    )

    # The course lived at the site root before it moved under /study/. These
    # keep any link made in between from 404-ing, and tell search engines the
    # move was permanent rather than letting both URLs compete.
    (out / "_redirects").write_text(
        "# course moved under /study/ (2026-08-13)\n"
        "/course/protein-as-string/*   /study/protein-as-string/   301\n"
        "/course/binding-and-affinity/* /study/binding-and-affinity/ 301\n"
        "/course/formats-and-ids/*     /study/formats-and-ids/     301\n"
        "/course/hands-on-day1/*       /study/hands-on-day1/       301\n"
        "/course/what-ai-does/*        /study/what-ai-does/        301\n"
        "/course/data-engineering/*    /study/data-engineering/    301\n"
        "/course/falsification/*       /study/falsification/       301\n"
        "/course/judgment/*            /study/judgment/            301\n"
        "/course/*                     /study/syllabus/            301\n"
        "/labs/*                       /study/labs/                301\n"
        "/quiz/*                       /study/quiz/                301\n"
        "/glossary/*                   /study/glossary/            301\n"
        "/resources/*                  /study/resources/           301\n"
        "\n# short aliases\n"
        "/s1  /study/protein-as-string/   301\n"
        "/s2  /study/binding-and-affinity/ 301\n"
        "/s3  /study/formats-and-ids/     301\n"
        "/s7  /study/falsification/       301\n"
        "/s8  /study/judgment/            301\n"
        "/course  /study/syllabus/        301\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------- og images


def build_og(out: Path, index: dict) -> None:
    """Render one 1200x630 PNG per OG variant using headless Chrome.

    Social crawlers do not render SVG, so a real raster is the only option. If
    Chrome is missing we skip rather than fail — the site is still valid, it just
    loses link previews, and CI on Linux should not hard-fail on that.
    """
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    ogdir = out / "assets" / "og"
    ogdir.mkdir(parents=True, exist_ok=True)

    variants = {}
    for page in index.values():
        v = page.get("og", "default")
        variants.setdefault(v, (page.get("og_headline", page["h1"]), page.get("og_kicker", "")))

    if not Path(chrome).exists():
        print("  ! Chrome not found — reusing checked-in OG images", file=sys.stderr)
        src = DIST / "assets" / "og"
        if src.exists():
            for f in src.glob("*.png"):
                shutil.copy2(f, ogdir / f.name)
        return

    tpl = (ASSETS / "og-template.html").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as td:
        for name, (headline, kicker) in variants.items():
            page_html = tpl.replace("{{HEADLINE}}", headline).replace("{{KICKER}}", kicker or P.SITE_NAME)
            f = Path(td) / f"{name}.html"
            f.write_text(page_html, encoding="utf-8")
            subprocess.run(
                [chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
                 "--force-device-scale-factor=1", "--window-size=1200,630",
                 f"--screenshot={ogdir / f'{name}.png'}", f.as_uri()],
                check=True, capture_output=True, timeout=90,
            )
    print(f"  og images: {len(variants)}")


# ---------------------------------------------------------------- build


STRIP_TAGS = re.compile(r"<[^>]+>")


def width(s: str) -> int:
    """Rough SERP display width. Search engines truncate on pixels, not code
    points, and a CJK glyph is about twice as wide as a Latin one — counting
    len() would happily wave through a Chinese title that gets cut in half."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def lint(index: dict, out: Path) -> list[str]:
    """Pre-flight SEO and integrity checks. These are the mistakes that are
    invisible in a browser but cost real search traffic."""
    problems: list[str] = []
    seen_title: dict[str, str] = {}
    seen_desc: dict[str, str] = {}

    for page in index.values():
        s = page["slug"] or "(root)"
        t, d = page["title"], page["desc"]
        if width(t) > 60:
            problems.append(f"{s}: title width {width(t)} (>60, truncated in SERP)")
        # width, not len: Google truncates Chinese meta descriptions at roughly
        # 78 CJK glyphs, which is ~156 in this measure.
        if not 110 <= width(d) <= 320:
            problems.append(f"{s}: description width {width(d)} (want 110–320)")
        if t in seen_title:
            problems.append(f"{s}: duplicate title with {seen_title[t]}")
        if d in seen_desc:
            problems.append(f"{s}: duplicate description with {seen_desc[d]}")
        seen_title[t], seen_desc[d] = s, s

        body = read_fragment(page["file"])
        if body.count("<h1") or (page.get("h1") and body.count("<h1")):
            problems.append(f"{s}: body contains an <h1>; the layout already emits one")

    # every internal link must resolve to a page we actually built
    known = {href(p["slug"]) for p in index.values()}
    for f in out.rglob("*.html"):
        rel = "/" + str(f.relative_to(out)).replace("index.html", "")
        for m in re.finditer(r'href="(/[^"#?]*)"', f.read_text(encoding="utf-8")):
            target = m.group(1)
            # anything carrying a file extension is a real file on disk, not a
            # page — /sitemap.xml must not be normalised into /sitemap.xml/
            if re.search(r"\.[a-z0-9]{2,4}$", target):
                if not (out / target.lstrip("/")).exists():
                    problems.append(f"{rel}: dead file link {target}")
                continue
            if not target.endswith("/"):
                target += "/"
            if target not in known:
                problems.append(f"{rel}: dead internal link {target}")
    return problems


def build(out: Path, quiet: bool = False) -> list[str]:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    index = {i: p for i, p in enumerate(P.PAGES)}
    for i, page in index.items():
        page.setdefault("crumb", page.get("h1", ""))
        page.setdefault("slug", "")

    for page in index.values():
        d = out if not page["slug"] else out / page["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(render(page, index), encoding="utf-8")

    shutil.copytree(ASSETS, out / "assets", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("og-template.html"))
    # labs/ is deliberately NOT copied into the site: the lab sources live on
    # GitHub, and shipping the cached structure files would add ~11 MB of
    # payload that no page ever links to.
    write_sitemap(out, index)
    build_og(out, index)
    # crawlers and older browsers probe /favicon.ico directly; the PNG is served
    # under that name on purpose — every current browser sniffs the content type.
    shutil.copy2(ASSETS / "favicon.png", out / "favicon.ico")
    (out / "404.html").write_text(render(P.NOT_FOUND, index), encoding="utf-8")

    problems = lint(index, out)
    if not quiet:
        n_html = len(list(out.rglob("*.html")))
        print(f"  {len(index)} pages, {n_html} html files -> {out}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="build to a temp dir and fail if dist/ is out of date")
    args = ap.parse_args()

    if args.check:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "dist"
            problems = build(tmp, quiet=True)
            # OG PNGs are re-rendered by Chrome and are not byte-reproducible, so
            # compare structure and text only.
            stale = diff_tree(tmp, DIST, skip={"assets/og"})
            if stale:
                print("dist/ is stale — run `python3 build.py` and commit:", file=sys.stderr)
                for s in stale[:40]:
                    print("  " + s, file=sys.stderr)
                return 1
            for p in problems:
                print("lint: " + p, file=sys.stderr)
            if problems:
                return 1
            print("dist/ is up to date; lint clean")
            return 0

    problems = build(DIST)
    for p in problems:
        print("lint: " + p, file=sys.stderr)
    return 1 if problems else 0


def diff_tree(a: Path, b: Path, skip: set[str]) -> list[str]:
    out = []
    if not b.exists():
        return ["dist/ does not exist"]
    for f in sorted(a.rglob("*")):
        rel = f.relative_to(a)
        if any(str(rel).startswith(s) for s in skip) or f.is_dir():
            continue
        other = b / rel
        if not other.exists():
            out.append(f"missing in dist/: {rel}")
        elif not filecmp.cmp(f, other, shallow=False):
            out.append(f"differs: {rel}")
    for f in sorted(b.rglob("*")):
        rel = f.relative_to(b)
        if any(str(rel).startswith(s) for s in skip) or f.is_dir():
            continue
        if not (a / rel).exists():
            out.append(f"stale in dist/: {rel}")
    return out


if __name__ == "__main__":
    sys.exit(main())
