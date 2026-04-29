"""
build.py — Generate site from config.json + Markdown blog posts
Usage:  python build.py [--config CONFIG] [--output OUTPUT]
"""

import json
import re
import sys
import os
import html as _html_mod
from datetime import datetime

DEFAULT_CONFIG = "config.json"
DEFAULT_OUTPUT = "index.html"

SOCIAL_ICONS = {
    "email":   "https://cdn.simpleicons.org/gmail",
    "scholar": "https://cdn.simpleicons.org/googlescholar",
    "github":  "https://cdn.simpleicons.org/github",
    "twitter": "https://cdn.simpleicons.org/x",
    "linkedin":"https://cdn.simpleicons.org/linkedin",
    "bilibili":"https://cdn.simpleicons.org/bilibili",
    "orcid":   "https://cdn.simpleicons.org/orcid",
    "xiaohongshu":"https://cdn.simpleicons.org/xiaohongshu",
    "csdn":    "https://cdn.simpleicons.org/csdn",
    "huawei":  "https://cdn.simpleicons.org/huawei",
}

SOCIAL_LABELS = {
    "email": "Email", "scholar": "Google Scholar", "github": "GitHub",
    "twitter": "Twitter / X", "linkedin": "LinkedIn", "bilibili": "Bilibili",
    "orcid": "ORCID", "xiaohongshu": "小红书",
    "csdn": "CSDN", "huawei": "Huawei",
}

_CSS = """\
    :root{--fg:#101114;--muted:#5b606b;--link:#0b63ff;--bg:#ffffff;--card:#f7f8fb;--rule:#e6e8ef;--maxw:1000px;--radius:12px}
    *{box-sizing:border-box}
    html,body{margin:0;padding:0;background:var(--bg);color:var(--fg);font-family:"Source Sans Pro",system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;line-height:1.65}
    a{color:var(--link);text-decoration:none}
    a:hover{text-decoration:underline}
    .container{max-width:var(--maxw);margin:0 auto;padding:24px 16px}
    .site-header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:8px 0}
    .brand{font-weight:700;letter-spacing:.2px}
    .brand a{color:var(--fg);text-decoration:none}
    .brand a:hover{text-decoration:none}
    .nav{display:flex;gap:16px;flex-wrap:wrap}
    .rule{border:none;border-top:1px solid var(--rule);margin:28px 0}

    .profile{display:grid;grid-template-columns:300px 1fr;gap:20px;align-items:start}
    .avatar{width:300px;height:400px;border-radius:12px;object-fit:cover;background:#ddd}
    .subtitle{color:var(--muted);margin-top:-6px}
    .quicklinks{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0}
    .btn{display:inline-block;padding:6px 12px;border:1px solid var(--rule);border-radius:8px;background:#fff}
    .btn:hover{background:#f9fafb}
    .tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
    .tag{background:var(--card);padding:4px 10px;border-radius:999px;font-size:14px;color:#333}

    .social-links{display:flex;gap:12px;margin-top:10px}
    .social-links a{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:50%;background:var(--card);border:1px solid var(--rule);transition:background .2s,transform .2s}
    .social-links a:hover{background:var(--rule);transform:scale(1.1);text-decoration:none}
    .social-links a img{width:20px;height:20px}

    .news-scroll{max-height:205px;overflow-y:auto;scrollbar-width:thin;scrollbar-color:#9aa0ad transparent}
    .news-scroll::-webkit-scrollbar{width:6px}
    .news-scroll::-webkit-scrollbar-track{background:transparent}
    .news-scroll::-webkit-scrollbar-thumb{background:#9aa0ad;border-radius:3px}
    .news-scroll::-webkit-scrollbar-thumb:hover{background:var(--muted)}
    .news-list{list-style:none;padding-left:0;margin:0}
    .news-list li{display:flex;gap:12px;padding:10px 0;border-bottom:1px dashed var(--rule)}
    .news-date{white-space:nowrap;color:var(--muted);min-width:92px}

    .proj{display:grid;grid-template-columns:260px 1fr;align-items:start;gap:12px;background:var(--card);border:1px solid var(--rule);border-radius:var(--radius);padding:12px 14px;line-height:1.4}
    .proj+.proj{margin-top:14px}
    .teaser{width:100%;display:block;border-radius:6px;background:#ddd;overflow:hidden}
    .teaser img,.teaser video{width:100%;height:auto;max-height:200px;object-fit:contain;border-radius:6px;display:block}
    .teaser-dual{display:grid;grid-template-columns:1fr 1fr;gap:4px;width:100%}
    .teaser-dual img,.teaser-dual video{width:100%;height:100%;max-height:200px;object-fit:cover;border-radius:6px;display:block}
    .proj h3{margin:0 0 3px;line-height:1.2}
    .proj .meta{margin:0;line-height:1.25;font-size:14px;color:var(--muted)}
    .proj .info p{margin:6px 0 4px;line-height:1.4}
    .actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px}
    .btn{padding:4px 9px;font-size:14px;line-height:1.1}
    .proj-scroll{overflow-y:auto;scrollbar-width:thin;scrollbar-color:#9aa0ad transparent}
    .proj-scroll::-webkit-scrollbar{width:6px}
    .proj-scroll::-webkit-scrollbar-track{background:transparent}
    .proj-scroll::-webkit-scrollbar-thumb{background:#9aa0ad;border-radius:3px}
    .proj-scroll::-webkit-scrollbar-thumb:hover{background:var(--muted)}

    .blog-card{display:grid;grid-template-columns:260px 1fr;align-items:start;gap:12px;background:var(--card);border:1px solid var(--rule);border-radius:var(--radius);padding:12px 14px}
    .blog-card.no-cover{grid-template-columns:1fr}
    a.card-link{display:block;margin-top:14px}
    a.card-link:first-child{margin-top:0}
    a.card-link{color:inherit;text-decoration:none}
    a.card-link:hover{text-decoration:none}
    .blog-card-cover{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:6px;background:var(--rule)}
    .blog-card h3{margin:0 0 6px;font-size:1.05rem;line-height:1.3}
    .card-date{color:var(--muted);font-size:.85rem}
    .card-summary{color:var(--muted);font-size:.9rem;margin:6px 0 4px;line-height:1.5}

    .back-link{display:inline-flex;align-items:center;gap:4px;color:var(--muted);font-size:.9rem;margin-bottom:20px}
    .back-link:hover{color:var(--link)}
    .post-cover{width:100%;max-height:420px;object-fit:cover;border-radius:var(--radius);margin:16px 0 24px}
    .post-article h2{margin-top:36px;margin-bottom:10px;font-size:1.35rem;border-bottom:1px solid var(--rule);padding-bottom:6px}
    .post-article h3{margin-top:28px;margin-bottom:8px;font-size:1.15rem}
    .post-article h4{margin-top:22px;margin-bottom:6px;font-size:1.05rem;color:var(--muted)}
    .post-article p{margin:12px 0;line-height:1.75}
    .post-article img{max-width:100%;border-radius:8px;margin:16px 0}
    .post-article pre{background:var(--card);border:1px solid var(--rule);padding:16px;border-radius:8px;overflow-x:auto;line-height:1.5;font-size:.9rem}
    .post-article code{font-family:Consolas,Monaco,"Courier New",monospace;font-size:.9em}
    .post-article p code,.post-article li code{background:var(--card);padding:2px 6px;border-radius:4px;border:1px solid var(--rule)}
    .post-article blockquote{border-left:3px solid var(--link);padding:4px 0 4px 16px;margin:16px 0;color:var(--muted);background:var(--card);border-radius:0 8px 8px 0}
    .post-article blockquote p{margin:6px 0}
    .post-article ul,.post-article ol{padding-left:24px;margin:10px 0}
    .post-article li{margin:4px 0;line-height:1.65}
    .post-meta{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:8px}
    .post-date{color:var(--muted);font-size:.9rem}
    .post-divider{border:none;border-top:1px solid var(--rule);margin:32px 0}

    @media(max-width:900px){.proj{grid-template-columns:220px 1fr}.blog-card{grid-template-columns:220px 1fr}}
    @media(max-width:720px){.profile{grid-template-columns:1fr}.proj{grid-template-columns:1fr}.blog-card{grid-template-columns:1fr}.site-header{flex-direction:column;align-items:flex-start}}
"""


# ---------- Markdown helpers ----------

def parse_md_links(text):
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'<a href="\2" target="_blank">\1</a>',
        text,
    )
    return text


def inline_md(text):
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def md_to_html(text):
    lines = text.split('\n')
    parts = []
    i = 0
    in_code = False
    code_lines = []
    in_list = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith('```'):
            if in_code:
                escaped = '\n'.join(_html_mod.escape(l) for l in code_lines)
                parts.append('<pre><code>' + escaped + '</code></pre>')
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if in_list and not (stripped.startswith('- ') or stripped.startswith('* ') or stripped.startswith('  ')):
            parts.append('</ul>')
            in_list = False

        if stripped.startswith('####'):
            parts.append(f'<h4>{inline_md(stripped[4:].strip())}</h4>')
        elif stripped.startswith('###'):
            parts.append(f'<h3>{inline_md(stripped[3:].strip())}</h3>')
        elif stripped.startswith('##'):
            parts.append(f'<h2>{inline_md(stripped[2:].strip())}</h2>')
        elif stripped.startswith('# '):
            parts.append(f'<h1>{inline_md(stripped[1:].strip())}</h1>')
        elif stripped in ('---', '***', '___'):
            parts.append('<hr class="rule">')
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                parts.append('<ul>')
                in_list = True
            parts.append(f'<li>{inline_md(stripped[2:])}</li>')
        elif stripped.startswith('> '):
            parts.append(f'<blockquote><p>{inline_md(stripped[2:])}</p></blockquote>')
        elif stripped == '':
            parts.append('')
        else:
            parts.append(f'<p>{inline_md(stripped)}</p>')

        i += 1

    if in_list:
        parts.append('</ul>')
    if in_code:
        escaped = '\n'.join(_html_mod.escape(l) for l in code_lines)
        parts.append('<pre><code>' + escaped + '</code></pre>')

    return '\n'.join(parts)


# ---------- Component builders ----------

def build_social_links(links):
    parts = []
    for item in links:
        p = item["platform"].lower()
        icon = SOCIAL_ICONS.get(p, "https://cdn.simpleicons.org/link")
        label = SOCIAL_LABELS.get(p, p.capitalize())
        parts.append(
            f'          <a href="{item["url"]}" target="_blank" rel="noopener" title="{label}">\n'
            f'            <img src="{icon}" alt="{label}">\n'
            f'          </a>'
        )
    return "\n".join(parts)


def build_bio_paragraphs(bio):
    return "\n".join(f"        <p>{parse_md_links(p)}</p>" for p in bio)


def build_tags(tags):
    return "\n".join(f'          <span class="tag">{t}</span>' for t in tags)


def build_nav(nav_items, current="", rel_prefix=""):
    parts = []
    for item in nav_items:
        if item == "Blog":
            href = f"{rel_prefix}blog.html"
            style = ' style="font-weight:700"' if current == "Blog" else ''
            parts.append(f'<a href="{href}"{style}>{item}</a>')
        else:
            href = f"{rel_prefix}index.html#{item.lower().replace(' ', '-')}"
            parts.append(f'<a href="{href}">{item}</a>')
    return " ".join(parts)


def build_news(news_list):
    items = []
    for n in news_list:
        items.append(
            f'          <li>\n'
            f'            <span class="news-date">{n["date"]}</span>\n'
            f'            <span>{parse_md_links(n["content"])}</span>\n'
            f'          </li>'
        )
    return "\n".join(items)


def build_publications(pub_list):
    if not pub_list:
        return '        <p style="color:var(--muted)">Coming soon.</p>'
    parts = []
    for pub in pub_list:
        authors_str = ", ".join(parse_md_links(a) for a in pub["authors"])
        media = pub.get("image", "") or pub.get("video", "")
        if media:
            ext = media.rsplit(".", 1)[-1].lower() if "." in media else ""
            if ext in ("mp4", "webm", "ogg"):
                media_tag = (
                    f'        <a class="teaser" href="#" aria-label="Project website">\n'
                    f'          <video autoplay loop muted playsinline>\n'
                    f'            <source src="{media}" type="video/{ext}">\n'
                    f'          </video>\n'
                    f'        </a>'
                )
            else:
                media_tag = (
                    f'        <a class="teaser" href="#" aria-label="Project website">\n'
                    f'          <img src="{media}" alt="Teaser" loading="lazy">\n'
                    f'        </a>'
                )
        else:
            media_tag = (
                f'        <a class="teaser" href="#" aria-label="Project website">\n'
                f'        </a>'
            )

        links = []
        for lk in pub.get("links", []):
            links.append(
                f'          <a class="btn" href="{lk["url"]}" target="_blank" rel="noopener">{lk["label"]}</a>'
            )
        links_str = "\n".join(links)

        parts.append(
            f'      <article class="proj">\n'
            f'{media_tag}\n'
            f'        <div class="info">\n'
            f'          <h3>{pub["title"]}</h3>\n'
            f'          <p class="meta"><b>Venue/Year:</b> {pub["venue"]}</p>\n'
            f'          <p>{authors_str}</p>\n'
            f'          <div class="actions">\n'
            f'{links_str}\n'
            f'          </div>\n'
            f'        </div>\n'
            f'      </article>'
        )
    return "\n\n".join(parts)


def _media_tag(src, link="#"):
    ext = src.rsplit(".", 1)[-1].lower() if "." in src else ""
    if ext in ("mp4", "webm", "ogg"):
        return (
            f'<a class="teaser" href="{link}" aria-label="Project link">\n'
            f'  <video autoplay loop muted playsinline>\n'
            f'    <source src="{src}" type="video/{ext}">\n'
            f'  </video>\n'
            f'</a>'
        )
    else:
        return (
            f'<a class="teaser" href="{link}" aria-label="Project link">\n'
            f'  <img src="{src}" alt="Teaser" loading="lazy">\n'
            f'</a>'
        )


def build_opensource(os_list):
    if not os_list:
        return ""
    parts = []
    for proj in os_list:
        first_link = proj.get("links", [{}])[0].get("url", "#")
        images = proj.get("images", [])
        if images:
            if len(images) == 1:
                media_tag = f'        {_media_tag(images[0], first_link)}'
            else:
                items = "\n".join(
                    f'          {_media_tag(img, first_link)}' for img in images
                )
                media_tag = f'        <div class="teaser teaser-dual">\n{items}\n        </div>'
        elif proj.get("image"):
            media_tag = f'        {_media_tag(proj["image"], first_link)}'
        else:
            media_tag = '        <div class="teaser"></div>'

        links = []
        for lk in proj.get("links", []):
            links.append(
                f'          <a class="btn" href="{lk["url"]}" target="_blank" rel="noopener">{lk["label"]}</a>'
            )
        links_str = "\n".join(links)
        desc = proj.get("description", "")

        parts.append(
            f'      <article class="proj">\n'
            f'{media_tag}\n'
            f'        <div class="info">\n'
            f'          <h3>{proj["title"]}</h3>\n'
            f'          <p>{desc}</p>\n'
            f'          <div class="actions">\n'
            f'{links_str}\n'
            f'          </div>\n'
            f'        </div>\n'
            f'      </article>'
        )
    return "\n\n".join(parts)


def build_education(edu_list):
    items = []
    for i, edu in enumerate(edu_list):
        border = 'border-bottom:1px dashed var(--rule);' if i < len(edu_list) - 1 else ''
        period = edu.get("period", "")
        period_html = f'\n          <span style="float:right;color:var(--muted);">{period}</span>' if period else ""
        advisor_html = ""
        if edu.get("advisor"):
            adv_url = edu.get("advisor_url", "#")
            advisor_html = (
                f'<br><span style="color:var(--muted);font-size:14px;">'
                f'Advisor: <a href="{adv_url}">{edu["advisor"]}</a></span>'
            )
        items.append(
            f'        <li style="padding:8px 0;{border}">\n'
            f'          <strong>{edu["degree"]}</strong> &mdash; '
            f'<a href="{edu.get("school_url", "#")}">{edu["school"]}</a>\n'
            f'{period_html}\n'
            f'{advisor_html}\n'
            f'        </li>'
        )
    return "\n".join(items)


# ---------- Blog helpers ----------

def _blog_slug(post):
    f = post.get("file", "")
    if f:
        return os.path.splitext(os.path.basename(f))[0]
    return re.sub(r'[^a-z0-9]+', '-', post.get("title", "post").lower()).strip('-')


def _blog_card(post, rel_prefix=""):
    slug = _blog_slug(post)
    title = post.get("title", "")
    date = post.get("date", "")
    summary = post.get("summary", "")
    image = post.get("image", "")
    tags = post.get("tags", [])
    tags_html = " ".join(f'<span class="tag">{t}</span>' for t in tags)
    cover_html = f'<img class="blog-card-cover" src="{rel_prefix}{image}" alt="{title}" loading="lazy">' if image else ""
    no_cover = " no-cover" if not image else ""
    return (
        f'    <a href="{rel_prefix}blog/{slug}.html" class="card-link">\n'
        f'    <article class="blog-card{no_cover}">\n'
        f'      {cover_html}\n'
        f'      <div>\n'
        f'        <h3>{title}</h3>\n'
        f'        <span class="card-date">{date}</span>\n'
        f'        <p class="card-summary">{summary}</p>\n'
        f'        <div class="tags">{tags_html}</div>\n'
        f'      </div>\n'
        f'    </article>\n'
        f'    </a>'
    )


# ---------- Page template ----------

def _page_html(cfg, title, body_html, current="", rel_prefix=""):
    nav = cfg.get("nav", ["About", "News", "Contact", "Research", "Blog"])
    year = datetime.now().year
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{cfg["name"]}'s personal website." />
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{cfg["name"]}'s personal website.">
  <meta property="og:type" content="website">
  <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
{_CSS}
  </style>
</head>
<body>
  <div class="container">
    <header class="site-header" aria-label="Site header">
      <div class="brand"><a href="{rel_prefix}index.html">{cfg["name"]}</a></div>
      <nav class="nav" aria-label="Primary">
        {build_nav(nav, current=current, rel_prefix=rel_prefix)}
      </nav>
    </header>
    <hr class="rule"/>
{body_html}
    <footer style="margin-top:40px;text-align:center;color:#aaa;font-size:13px;">
      <p>&copy; {year} {cfg["name"]}. Last updated: {datetime.now().strftime("%B %Y")}.</p>
    </footer>
  </div>
</body>
</html>'''


# ---------- Page builders ----------

def build_html(cfg):
    display_name = cfg["name"]
    if cfg.get("name_cn"):
        display_name = f'{cfg["name"]} ({cfg["name_cn"]})'

    nav = cfg.get("nav", ["About", "News", "Contact", "Research"])
    contact_email = cfg["contact"].get("email", "")
    contact_office = cfg["contact"].get("office", "")

    emails = [e.strip() for e in contact_email.split("|") if e.strip()]
    email_links = " | ".join(f'<a href="mailto:{e}">{e}</a>' for e in emails)
    contact_html = f'      <p>Email: {email_links}</p>\n'
    if contact_office:
        contact_html += f'      <p>Office: {contact_office}</p>\n'

    sections = []

    if "News" in nav:
        sections.append(f'''
    <hr class="rule"/>

    <section id="news" aria-label="News">
      <h2>News</h2>
      <div class="news-scroll">
        <ul class="news-list">
{build_news(cfg.get("news", []))}
        </ul>
      </div>
    </section>''')

    if "Contact" in nav:
        sections.append(f'''
    <hr class="rule"/>

    <section id="contact" aria-label="Contact">
      <h2>Contact</h2>
{contact_html}
    </section>''')

    if "Research" in nav:
        sections.append(f'''
    <hr class="rule"/>

    <section id="research" aria-label="Research projects">
      <h2>Research Projects</h2>
      <p> * Equally contributed, &dagger; corresponding author.</p>
      <div class="proj-scroll" id="proj-scroll">
{build_publications(cfg.get("publications", []))}
      </div>
    </section>''')

    if "Open Source" in nav:
        sections.append(f'''
    <hr class="rule"/>

    <section id="open-source" aria-label="Open Source">
      <h2>Open Source</h2>
{build_opensource(cfg.get("opensource", []))}
    </section>''')

    if "Blog" in nav:
        blog_list = cfg.get("blog", [])
        blog_cards = "\n\n".join(_blog_card(p) for p in blog_list[:3])
        sections.append(f'''
    <hr class="rule"/>

    <section id="blog" aria-label="Blog">
      <h2>Blog</h2>
{blog_cards}
      <p style="margin-top:14px;"><a href="blog.html">See all posts &rarr;</a></p>
    </section>''')

    if "Education" in nav:
        sections.append(f'''
    <hr class="rule"/>

    <section id="education" aria-label="Education">
      <h2>Education</h2>
      <ul style="list-style:none;padding:0;margin:0;">
{build_education(cfg.get("education", []))}
      </ul>
    </section>''')

    sections_html = "\n".join(sections)

    body = f'''
    <section id="about" class="profile" aria-label="About">
      <img class="avatar" src="{cfg.get("avatar", "assets/images/photo.jpg")}" alt="Portrait" loading="lazy">
      <div>
        <h1>{display_name}</h1>
        <p class="subtitle">{cfg["title"]} &middot; {cfg["affiliation"]}</p>
{build_bio_paragraphs(cfg.get("bio", []))}
        <div class="tags">
{build_tags(cfg.get("research_tags", []))}
        </div>
        <div class="social-links">
{build_social_links(cfg.get("social_links", []))}
        </div>
      </div>
    </section>
{sections_html}
    <script>
    const projScroll = document.getElementById('proj-scroll');
    if (projScroll) {{
      const si = document.querySelectorAll('#proj-scroll > .proj');
      if (si.length >= 3) {{
        const avgH = Array.from(si).slice(0,3).reduce((s,el) => s + el.getBoundingClientRect().height + 14, 0) / Math.min(si.length,3);
        projScroll.style.maxHeight = Math.round(avgH * 3) + 'px';
      }} else {{
        projScroll.style.maxHeight = '600px';
      }}
    }}
    </script>

    <hr class="rule"/>

    <section id="say-anything" aria-label="Say Anything">
      <h2>Say Anything</h2>
      <div class="giscus"></div>
      <script src="https://giscus.app/client.js"
        data-repo="ArrebolBlack/arrebolblack.github.io"
        data-repo-id="R_kgDOSMj__A"
        data-category="Announcements"
        data-category-id="DIC_kwDOSMj__M4C768D"
        data-mapping="specific"
        data-term="Say Anything"
        data-strict="1"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="top"
        data-theme="preferred_color_scheme"
        data-lang="zh-CN"
        data-loading="lazy"
        crossorigin="anonymous"
        async>
      </script>
    </section>'''

    return _page_html(cfg, cfg["name"], body)


def build_blog_page(cfg):
    blog_list = cfg.get("blog", [])
    if not blog_list:
        body = '    <h2>Blog</h2>\n    <p style="color:var(--muted)">No posts yet. Stay tuned!</p>'
        return _page_html(cfg, f'{cfg["name"]} · Blog', body, current="Blog")
    cards = "\n\n".join(_blog_card(p) for p in blog_list)
    body = f'    <h2>Blog</h2>\n\n{cards}'
    return _page_html(cfg, f'{cfg["name"]} · Blog', body, current="Blog")


def build_post_page(cfg, post):
    slug = _blog_slug(post)
    title = post.get("title", "")
    date = post.get("date", "")
    image = post.get("image", "")
    tags = post.get("tags", [])
    tags_html = " ".join(f'<span class="tag">{t}</span>' for t in tags)
    md_file = post.get("file", "")

    if md_file and os.path.isfile(md_file):
        with open(md_file, "r", encoding="utf-8") as f:
            md_text = f.read()
        content_html = md_to_html(md_text)
    else:
        content_html = f'<p>{parse_md_links(post.get("summary", ""))}</p>'

    cover_html = f'<img class="post-cover" src="../{image}" alt="{title}">' if image else ""

    # Fix relative image paths: blog_src/<slug>/images/* and assets/*
    post_dir = os.path.dirname(md_file) if md_file else ""
    content_html = content_html.replace('src="assets/', 'src="../assets/')
    if post_dir:
        content_html = content_html.replace('src="images/', f'src="../{post_dir}/images/')

    body = f'''    <a class="back-link" href="../blog.html">&larr; Back to Blog</a>
    <article class="post-article">
      <h1>{title}</h1>
      <div class="post-meta">
        <span class="post-date">{date}</span>
        <div class="tags">{tags_html}</div>
      </div>
      {cover_html}
      {content_html}
    </article>
    <hr class="post-divider">
    <a class="back-link" href="../blog.html">&larr; Back to Blog</a>'''

    return _page_html(cfg, f'{cfg["name"]} · {title}', body, current="Blog", rel_prefix="../")


# ---------- Main ----------

def main():
    config_path = DEFAULT_CONFIG
    output_path = DEFAULT_OUTPUT

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--config" and i + 1 < len(args):
            config_path = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        else:
            i += 1

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(build_html(cfg))
    print(f"[OK] Generated {output_path}")

    with open("blog.html", "w", encoding="utf-8") as f:
        f.write(build_blog_page(cfg))
    print("[OK] Generated blog.html")

    blog_list = cfg.get("blog", [])
    if blog_list:
        os.makedirs("blog", exist_ok=True)
        for post in blog_list:
            slug = _blog_slug(post)
            post_html = build_post_page(cfg, post)
            path = os.path.join("blog", f"{slug}.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(post_html)
            print(f"[OK] Generated {path}")


if __name__ == "__main__":
    main()
