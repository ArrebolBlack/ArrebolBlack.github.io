# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build

```bash
python build.py                                # regenerate index.html, blog.html, blog/*.html
python build.py --config CONFIG --output OUTPUT  # override defaults
```

There is no test suite, linter, or package manager — the only build step is `python build.py` (stdlib-only).

## Architecture

This is a **static site generator** for a personal academic website. `build.py` reads `config.json` plus Markdown blog posts and emits HTML files at the repo root.

**Source of truth → outputs:**
- `config.json` — all site content (bio, news, publications, open-source projects, blog metadata, education, social links, nav). Edit this, not the generated HTML.
- `blog_src/<slug>/post.md` (+ `images/`) — long-form blog content. Registered in `config.json`'s `blog` array via a `file` field pointing to the `.md`.
- `build.py` → writes `index.html`, `blog.html`, and `blog/<slug>.html` per blog entry.
- CSS lives inline in `build.py` as the `_CSS` string constant and is injected into every page. There is no separate stylesheet.

**Page builders in `build.py`:**
- `build_html(cfg)` — homepage; sections are emitted conditionally based on `cfg["nav"]` (e.g. an item only renders if its name is in `nav`).
- `build_blog_page(cfg)` — blog index.
- `build_post_page(cfg, post)` — individual post page; rewrites relative image paths (`images/...` → `../blog_src/<slug>/images/...`, `assets/...` → `../assets/...`) because posts live one directory deep.

**Custom mini-Markdown (not CommonMark):**
- `parse_md_links` handles `[text](url)` and `**bold**` only. Used for bio/news/author strings.
- `inline_md` adds italics, inline code, and images.
- `md_to_html` is the full block-level parser (headings, lists, fenced code, blockquotes, images) used for blog post bodies.
- **Raw HTML passes through unescaped** in bio/news/description fields — useful for tags like `<s>`, `<br>`, but also a footgun.

## Adding a blog post

1. Copy `blog_src/_template/` to `blog_src/<your-slug>/`.
2. Edit `post.md`; put images in `images/` and reference them as `images/foo.png` (the builder rewrites the path).
3. Append an entry to `config.json`'s `blog` array with `"file": "blog_src/<your-slug>/post.md"`.
4. Run `python build.py`.

## Deployment notes

- Deployed via GitHub Pages from `ArrebolBlack/arrebolblack.github.io` (Giscus comments embed in `build.py` reference this repo's discussions).
- The `app/` directory is the old version and is gitignored — don't edit it.
