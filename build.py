#!/usr/bin/env python3
"""Build the website from the LaTeX CV (Awesome-CV) plus web-only data files.

Sources
  cv-src/            clone of https://github.com/zang09/CV_HaebeomJung (content of record)
  data/*.json        web-only metadata: hero, news, logos, links, previews, selections
  content/*.html     bio snippets
  templates/base.html page shell (head, nav, footer)

Outputs (committed, and regenerated in CI before deploy)
  index.html, news/, publications/, experience/, honors/, vitae/
  assets/pdf/CV_HaebeomJung.pdf  (copied from cv-src/cv.pdf when present)

Usage
  python3 build.py            # clone/update cv-src, build pages, copy PDF if present
  python3 build.py --pdf      # also compile the PDF with latexmk/xelatex and copy it into assets/pdf/
  python3 build.py --no-fetch # do not touch cv-src (CI checks it out itself)
  python3 build.py --ci       # copy cv-src/cv.pdf into assets/pdf/ (used by the workflow)

The committed assets/pdf/CV_HaebeomJung.pdf is only replaced with --pdf or --ci, so an
ad-hoc local compile never overwrites the deployed PDF by accident.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CV_REPO = "https://github.com/zang09/CV_HaebeomJung.git"
# A sibling clone named CV_HaebeomJung/ (e.g. one you cloned yourself) is used if present.
CV_DIR = next((d for d in (ROOT / "CV_HaebeomJung", ROOT / "cv-src") if d.exists()), ROOT / "cv-src")
SITE_URL = "https://www.haebeom.com"


# ----------------------------------------------------------------------------
# CV source management
# ----------------------------------------------------------------------------
def ensure_cv_source(fetch: bool) -> None:
    if not CV_DIR.exists():
        if not fetch:
            sys.exit("cv-src/ is missing; run without --no-fetch or clone it manually.")
        print("Cloning CV repository …")
        subprocess.run(["git", "clone", "--depth", "1", CV_REPO, str(CV_DIR)], check=True)
    elif fetch:
        print("Updating CV repository …")
        subprocess.run(["git", "-C", str(CV_DIR), "pull", "--ff-only", "-q"], check=False)


def build_pdf() -> None:
    if shutil.which("latexmk") is None:
        sys.exit("latexmk not found; install TeX Live or drop --pdf.")
    print("Compiling cv.pdf with xelatex …")
    subprocess.run(
        ["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "cv.tex"],
        cwd=CV_DIR,
        check=True,
        stdout=subprocess.DEVNULL,
    )


def copy_pdf() -> None:
    src = CV_DIR / "cv.pdf"
    dst = ROOT / "assets" / "pdf" / "CV_HaebeomJung.pdf"
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        print(f"Copied {src.relative_to(ROOT)} → {dst.relative_to(ROOT)}")
    else:
        print("cv-src/cv.pdf not found; keeping the existing PDF.")


# ----------------------------------------------------------------------------
# Minimal LaTeX reader for Awesome-CV macros
# ----------------------------------------------------------------------------
def strip_comments(tex: str) -> str:
    out = []
    for line in tex.splitlines():
        buf, i = [], 0
        while i < len(line):
            ch = line[i]
            if ch == "\\" and i + 1 < len(line):
                buf.append(line[i : i + 2])
                i += 2
                continue
            if ch == "%":
                break
            buf.append(ch)
            i += 1
        out.append("".join(buf))
    return "\n".join(out)


def read_group(s: str, i: int) -> tuple[str, int]:
    """Read one {...} group starting at index i (skipping whitespace). Returns (content, next_index)."""
    while i < len(s) and s[i].isspace():
        i += 1
    if i >= len(s) or s[i] != "{":
        return "", i
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1 : j], j + 1
        j += 1
    raise ValueError("unbalanced braces")


MACROS = {
    "cvsection": 1,
    "cvsubsection": 1,
    "cventry": 5,
    "cvhonor": 4,
    "cvbrief": 2,
    "cvskill": 2,
}


def parse_tex(path: Path) -> list[dict]:
    """Return the macros of a section file in document order."""
    tex = strip_comments(path.read_text(encoding="utf-8"))
    items = []
    for m in re.finditer(r"\\(cvsection|cvsubsection|cventry|cvhonor|cvbrief|cvskill|begin\{cvparagraph\})", tex):
        name = m.group(1)
        if name.startswith("begin"):
            end = tex.find(r"\end{cvparagraph}", m.end())
            items.append({"type": "cvparagraph", "args": [tex[m.end() : end].strip()]})
            continue
        args, i = [], m.end()
        for _ in range(MACROS[name]):
            g, i = read_group(tex, i)
            args.append(g.strip())
        items.append({"type": name, "args": args})
    return items


def parse_items(group: str) -> list[str]:
    """Extract \\item {...} texts from a cvitems block."""
    out, i = [], 0
    while True:
        j = group.find(r"\item", i)
        if j < 0:
            break
        g, i = read_group(group, j + 5)
        if g:
            out.append(g.strip())
        else:  # \item without braces: take until next \item or \end
            k = group.find(r"\item", j + 5)
            e = group.find(r"\end", j + 5)
            stop = min(x for x in (k, e, len(group)) if x >= 0)
            out.append(group[j + 5 : stop].strip())
            i = stop
    return out


def tex_to_html(s: str) -> str:
    """Convert the small LaTeX subset used in the CV to inline HTML."""
    if not s:
        return ""
    s = s.replace(r"\&", "\u0000AMP\u0000")
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = s.replace("\u0000AMP\u0000", "&amp;")
    # links: \href{url}{text}
    def href(m):
        return f'<a href="{m.group(1)}" target="_blank" rel="noopener">{m.group(2)}</a>'
    for _ in range(3):
        s = re.sub(r"\\href\{([^{}]*)\}\{((?:[^{}]|\{[^{}]*\})*)\}", href, s)
    # formatting
    for _ in range(3):
        s = re.sub(r"\\textbf\{((?:[^{}]|\{[^{}]*\})*)\}", r"<strong>\1</strong>", s)
        s = re.sub(r"\\textit\{((?:[^{}]|\{[^{}]*\})*)\}", r"<em>\1</em>", s)
        s = re.sub(r"\\(?:small|scriptsize|footnotesize|normalsize|large)\{((?:[^{}]|\{[^{}]*\})*)\}", r"\1", s)
        s = re.sub(r"\\phantom\{[^{}]*\}", "", s)
        s = re.sub(r"\\vspace\{[^{}]*\}", "", s)
    s = re.sub(r"\$\^\{?\*\}?\$", "<sup>*</sup>", s)
    s = s.replace(r"{\enskip\cdotp\enskip}", " · ").replace(r"\enskip\cdotp\enskip", " · ")
    s = s.replace(r"\cdotp", "·").replace(r"\enskip", " ").replace(r"\quad", " ")
    s = s.replace(r"\\", " ").replace("~", "&nbsp;")
    s = re.sub(r"\\(?:small|scriptsize|footnotesize|normalsize|large|textbf|textit)\b", "", s)
    s = s.replace("{", "").replace("}", "")
    s = s.replace(" - ", " – ").replace("---", "—").replace("--", "–")
    return re.sub(r"\s+", " ", s).strip()


def tex_to_text(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", tex_to_html(s)))


MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def start_key(dates: str) -> int:
    """Sort key from a date string such as 'Dec. 2021 - Apr. 2022', '2023-2025', '2018'."""
    m = re.search(r"([A-Za-z]{3})[a-z]*\.?\s+(\d{4})", dates)
    if m:
        return int(m.group(2)) * 12 + MONTHS.index(m.group(1).lower()[:3])
    m = re.search(r"\d{4}", dates)
    return int(m.group(0)) * 12 if m else 0


def year_of(dates: str) -> str:
    m = re.search(r"\d{4}", dates)
    return m.group(0) if m else ""


def nice_dates(d: str) -> str:
    return tex_to_html(d).replace(" - ", " – ")


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
def load_json(name: str):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def load_snippet(name: str) -> str:
    return (ROOT / "content" / name).read_text(encoding="utf-8").strip()


def split_role(title: str) -> tuple[str, str]:
    """'Software · Robotics Engineer (Full-time)' -> ('Software / Robotics Engineer', 'Full-time')."""
    t = tex_to_text(title)
    m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", t)
    role, note = (m.group(1), m.group(2)) if m else (t, "")
    role = role.replace(" · ", " / ")
    return role, note


def find_meta(entries: list[dict], text: str) -> dict:
    """Find the first metadata entry whose 'match' substring occurs in text (case-insensitive)."""
    low = text.lower()
    for e in entries:
        if e.get("match", "").lower() in low:
            return e
    return {}


# ----------------------------------------------------------------------------
# HTML building blocks
# ----------------------------------------------------------------------------
CHEVRON = (
    '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">'
    '<path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.2" '
    'stroke-linecap="round" stroke-linejoin="round" /></svg>'
)


def toggle(cls: str, controls: str, closed: str, opened: str, toggle_class: str | None = None) -> str:
    extra = f' data-toggle-class="{toggle_class}"' if toggle_class else ""
    return (
        f'<button type="button" class="bio-toggle {cls}" aria-expanded="false" aria-controls="{controls}"{extra}>'
        f'<span class="when-closed">{closed}</span><span class="when-open">{opened}</span>{CHEVRON}</button>'
    )


def logo_tile(org: dict, name: str, cls: str, root: str) -> str:
    if org.get("logo"):
        flush = " flush" if org.get("flush") else ""
        return f'<div class="{cls}{flush}"><img src="{root}assets/img/logos/{org["logo"]}" alt="{html.escape(name)} logo" loading="lazy" /></div>'
    initials = "".join(w[0] for w in re.findall(r"[A-Za-z]+", name))[:3].upper() or "?"
    return f'<div class="{cls} mono" aria-hidden="true">{initials}</div>'


def link_or_text(name: str, url: str | None) -> str:
    return f'<a href="{url}" target="_blank" rel="noopener">{name}</a>' if url else name


# ----------------------------------------------------------------------------
# Section renderers
# ----------------------------------------------------------------------------
class Site:
    def __init__(self, fetch: bool):
        self.site = load_json("site.json")
        self.news = load_json("news.json")
        self.pub_meta = load_json("publications.json")
        self.orgs = load_json("orgs.json")
        self.honor_meta = load_json("honors.json")
        self.tpl = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")

        cvtex = strip_comments((CV_DIR / "cv.tex").read_text(encoding="utf-8"))
        self.section_files = [f for f in re.findall(r"\\input\{([^}]+)\}", cvtex) if f.startswith("cv/")]
        self.sections = {f: parse_tex(CV_DIR / f"{f}.tex") for f in self.section_files}

    # --- helpers over parsed CV -------------------------------------------
    def entries(self, section: str) -> list[dict]:
        return [m for m in self.sections.get(section, []) if m["type"] == "cventry"]

    def section_title(self, section: str) -> str:
        for m in self.sections.get(section, []):
            if m["type"] == "cvsection":
                return tex_to_html(m["args"][0])
        return section

    def org_meta(self, name: str) -> dict:
        key = tex_to_text(name)
        return self.orgs.get(key) or find_meta([dict(v, match=k) for k, v in self.orgs.items()], key)

    def work_entries(self) -> list[dict]:
        out = []
        for e in self.entries("cv/working_experience"):
            title, org, loc, dates, body = e["args"]
            role, note = split_role(title)
            out.append(dict(kind="work", role=role, note=note, org=tex_to_text(org), loc=tex_to_text(loc),
                            dates=nice_dates(dates), key=start_key(dates), items=[tex_to_html(i) for i in parse_items(body)]))
        return out

    def edu_entries(self) -> list[dict]:
        out = []
        hide_gpa = self.site.get("hide_gpa", True)
        for e in self.entries("cv/education"):
            degree, inst, loc, dates, body = e["args"]
            items = [tex_to_html(i) for i in parse_items(body)]
            if hide_gpa:
                items = [i for i in items if "GPA" not in i]
            out.append(dict(kind="edu", role=tex_to_text(degree), note="", org=tex_to_text(inst), loc=tex_to_text(loc),
                            dates=nice_dates(dates), key=start_key(dates), items=items))
        return out

    def publications(self) -> list[dict]:
        out = []
        for e in self.entries("cv/publications"):
            authors, title, venue, date, _ = e["args"]
            title_text = tex_to_text(title)
            meta = find_meta(self.pub_meta, title_text)
            auth = tex_to_html(authors).replace(", and ", ", ").replace(" and ", ", ")
            auth = auth.replace("<strong>Haebeom Jung</strong>", '<span class="me">Haebeom Jung</span>')
            out.append(dict(title=title_text, authors=auth, venue=tex_to_text(venue), date=tex_to_text(date),
                            under_review="review" in tex_to_text(venue).lower(), meta=meta))
        return out

    def honors(self) -> list[dict]:
        out, group = [], ""
        for m in self.sections.get("cv/awards", []):
            if m["type"] == "cvsubsection":
                label = tex_to_text(m["args"][0])
                group = label if label.lower() not in ("international", "domestic") else group
            elif m["type"] == "cvhonor":
                award, event, loc, dates = m["args"]
                video = re.search(r"\\href\{([^}]*)\}", event)
                event_text = re.sub(r"\s*\[Video\]\s*", "", tex_to_text(event)).strip()
                meta = find_meta(self.honor_meta, f"{event_text} {award} {dates}")
                out.append(dict(
                    group=group,
                    year=year_of(dates),
                    dates=nice_dates(dates),
                    title=meta.get("title") or f"{tex_to_text(award)}, {event_text}",
                    award=tex_to_text(award),
                    event=event_text,
                    awarder=meta.get("awarder") or tex_to_text(loc),
                    summary=meta.get("summary", ""),
                    news=meta.get("news"),
                    video=meta.get("video") or (video.group(1) if video else None),
                    selected=bool(meta.get("selected")),
                ))
        out.sort(key=lambda h: int(h["year"] or 0), reverse=True)
        return out

    # --- page fragments ----------------------------------------------------
    def nav(self, root: str, current: str) -> str:
        links = [("Home", "index.html"), ("News", "news/index.html"), ("Publications", "publications/index.html"),
                 ("Experience", "experience/index.html"), ("Honors", "honors/index.html")]
        out = []
        for label, href in links:
            cur = ' aria-current="page"' if href == current else ""
            out.append(f'          <a href="{root}{href}"{cur}>{label}</a>')
        return "\n".join(out)

    def page(self, *, root: str, current: str, title: str, desc: str, path: str, main: str, ldjson: str = "") -> str:
        full_title = "Haebeom Jung" if current == "index.html" else f"{title} · Haebeom Jung"
        return (self.tpl
                .replace("{{ROOT}}", root)
                .replace("{{TITLE}}", full_title)
                .replace("{{DESC}}", html.escape(desc, quote=True))
                .replace("{{URL}}", SITE_URL + path)
                .replace("{{NAV}}", self.nav(root, current))
                .replace("{{LDJSON}}", ldjson)
                .replace("{{MAIN}}", main))

    def subpage(self, *, current: str, title: str, lede: str, desc: str, path: str, body: str) -> str:
        lede_html = f'\n          <p class="page-lede">{lede}</p>' if lede else ""
        main = f'''    <main id="main" class="container container-narrow">
      <section class="section page-section">
        <div class="section-head page-head">
          <h1>{title}</h1>{lede_html}
        </div>
{body}
      </section>
    </main>'''
        return self.page(root="../", current=current, title=html.unescape(re.sub("<[^>]+>", "", title)), desc=desc, path=path, main=main)

    # news -----------------------------------------------------------------
    def news_list(self, items: list[dict], root: str) -> str:
        lis = []
        for n in items:
            body = n["html"].replace('href="/', f'href="{root}')
            lis.append(f'''          <li>
            <time datetime="{n["date"]}">{n["label"]}</time>
            <p>{body}</p>
          </li>''')
        return "\n".join(lis)

    # publications ----------------------------------------------------------
    def pub_cards(self, pubs: list[dict], root: str) -> str:
        cards = []
        for i, p in enumerate(pubs):
            m = p["meta"]
            slug = m.get("slug", f"pub{i}")
            prev = m.get("preview")
            media = ""
            if prev:
                base = f"{root}assets/img/papers/{prev}"
                url = m.get("project") or m.get("arxiv") or "#"
                media = f'''            <a class="pub-media" href="{url}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true">
              <img src="{base}.jpg" alt="" loading="lazy" />
              <video muted loop playsinline preload="metadata" poster="{base}.jpg">
                <source src="{base}.mp4" type="video/mp4" />
                <source src="{base}.webm" type="video/webm" />
              </video>
            </a>
'''
            tags = "".join(f'<span class="venue-tag">{t}</span>' for t in m.get("tags", [p["venue"]]))
            venue_full = m.get("venue_full", "")
            links = []
            for key, label in (("project", "Project"), ("arxiv", "arXiv"), ("code", "Code")):
                if m.get(key):
                    links.append(f'<a class="pl {key}" href="{m[key]}" target="_blank" rel="noopener">{label}</a>')
            if m.get("doi"):
                links.append(f'<a class="doi" href="https://doi.org/{m["doi"]}" target="_blank" rel="noopener">DOI</a>')
            bib = ""
            if m.get("bibtex"):
                links.append(f'<button type="button" class="bib-toggle" aria-expanded="false" aria-controls="bib-{slug}">BibTeX</button>')
                bib = f'\n              <pre class="bib" id="bib-{slug}" hidden>{html.escape(m["bibtex"].strip())}</pre>'
            title_link = m.get("project") or m.get("arxiv")
            title_html = f'<a href="{title_link}" target="_blank" rel="noopener">{html.escape(p["title"])}</a>' if title_link else html.escape(p["title"])
            cards.append(f'''          <li class="card pub">
{media}            <div class="pub-body">
              <p class="pub-venue">{tags} {venue_full}</p>
              <h3 class="pub-title">{title_html}</h3>
              <p class="pub-authors">{p["authors"]}</p>
              <p class="pub-links">{"".join(links)}</p>{bib}
            </div>
          </li>''')
        return "\n".join(cards)

    # honors ----------------------------------------------------------------
    def honor_cards(self, honors: list[dict]) -> str:
        cards = []
        for h in honors:
            meta_bits = [h["awarder"]]
            if h["summary"]:
                meta_bits.append(h["summary"])
            links = []
            if h["news"]:
                links.append(f'<a class="honor-link news" href="{h["news"]}" target="_blank" rel="noopener">News</a>')
            if h["video"]:
                links.append(f'<a class="honor-link video" href="{h["video"]}" target="_blank" rel="noopener">Video</a>')
            links_html = f'\n              <p class="honor-links">{"".join(links)}</p>' if links else ""
            cards.append(f'''          <li class="card">
            <time>{h["year"]}</time>
            <div>
              <p class="honor-title">{html.escape(h["title"])}</p>
              <p class="honor-meta">{" · ".join(html.escape(b) for b in meta_bits)}</p>{links_html}
            </div>
          </li>''')
        return "\n".join(cards)

    # experience -------------------------------------------------------------
    def exp_cards(self, entries: list[dict], root: str) -> str:
        cards = []
        for i, e in enumerate(entries):
            org = self.org_meta(e["org"])
            note = e["note"] or org.get("note", "") if e["kind"] == "work" else org.get("note", "")
            note_html = f'\n              <p class="exp-note">{note}</p>' if note else ""
            details = ""
            if e["items"]:
                lis = "".join(f"\n                <li>{it}</li>" for it in e["items"])
                cid = f"exp-{e['kind']}-{i}"
                details = f'''
              {toggle("exp-toggle", cid, "Details", "Hide details")}
              <ul class="exp-details" id="{cid}" hidden>{lis}
              </ul>'''
            cards.append(f'''          <li class="card exp">
            {logo_tile(org, e["org"], "exp-logo", root)}
            <div class="exp-body">
              <h3 class="exp-title">{html.escape(e["role"])}</h3>
              <p class="exp-org">{link_or_text(html.escape(e["org"]), org.get("url"))} · {html.escape(e["loc"])}</p>
              <p class="exp-dates">{e["dates"]}</p>{note_html}{details}
            </div>
          </li>''')
        return "\n".join(cards)

    # home timeline --------------------------------------------------------------
    def timeline(self, entries: list[dict], root: str, show: int) -> str:
        lis = []
        for i, e in enumerate(sorted(entries, key=lambda x: x["key"], reverse=True)):
            org = self.org_meta(e["org"])
            title = e["role"] + (f" · {e['note'].lower()}" if e["kind"] == "work" and e["note"] and "military" in e["note"].lower() else "")
            sub = org.get("summary") or (e["items"][0] if e["items"] else "")
            hidden = ' class="tl-item tl-more" hidden' if i >= show else ' class="tl-item"'
            lis.append(f'''          <li{hidden}>
            {logo_tile(org, e["org"], "tl-logo", root)}
            <div class="tl-body">
              <div class="tl-head">
                <span class="tl-place">{html.escape(e["org"])}</span>
                <span class="tl-time">{e["dates"]}</span>
              </div>
              <p class="tl-title">{html.escape(title)}</p>
              <p class="tl-sub">{sub}</p>
            </div>
          </li>''')
        more = toggle("tl-toggle", "tl-list", "Show more", "Show less", "tl-more") if len(entries) > show else ""
        return f'''        <div class="card tl-card">
          <ul class="tl" id="tl-list">
{chr(10).join(lis)}
          </ul>
          {more}
        </div>'''

    # vitae (mirrors the CV section order) ---------------------------------------
    def vitae_body(self) -> str:
        parts = [f'''        <div class="cv-actions">
          <a class="btn-primary" href="../assets/pdf/CV_HaebeomJung.pdf" target="_blank" rel="noopener">
            <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
              <path d="M12 3v12m0 0l-4-4m4 4l4-4M4 17v2a2 2 0 002 2h12a2 2 0 002-2v-2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            Download CV (PDF)
          </a>
          <span class="cv-updated">Generated from the LaTeX CV</span>
        </div>''']

        def row(left, title, sub="", extra="", items=None):
            sub_html = f'\n              <p class="cv-sub">{sub}</p>' if sub else ""
            extra_html = f'\n              <p class="cv-extra">{extra}</p>' if extra else ""
            items_html = ""
            if items:
                items_html = '\n              <ul class="cv-items">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
            return f'''          <li>
            <span class="cv-when">{left}</span>
            <div>
              <p class="cv-title">{title}</p>{sub_html}{extra_html}{items_html}
            </div>
          </li>'''

        hide_gpa = self.site.get("hide_gpa", True)
        for sec in self.section_files:
            macros = self.sections[sec]
            title = self.section_title(sec)
            rows, sub_label = [], ""
            for m in macros:
                t, a = m["type"], m["args"]
                if t == "cvsubsection":
                    sub_label = tex_to_html(a[0])
                    if sub_label.lower() not in ("international", "domestic"):
                        rows.append(f'          <li class="cv-sublabel">{sub_label}</li>')
                elif t == "cventry":
                    a0, a1, a2, a3, a4 = (tex_to_html(x) for x in a[:4]) if False else (None,) * 5
                    items = [tex_to_html(i) for i in parse_items(a[4])]
                    if hide_gpa:
                        items = [i for i in items if "GPA" not in i]
                    body_text = tex_to_html(a[4]) if not items and a[4].strip() else ""
                    if sec == "cv/publications":
                        rows.append(row(tex_to_html(a[2]), tex_to_html(a[1]), tex_to_html(a[0])))
                    elif sec in ("cv/patents", "cv/fundings"):
                        sub = " · ".join(x for x in (tex_to_html(a[0]), tex_to_html(a[2])) if x)
                        rows.append(row(nice_dates(a[3]), tex_to_html(a[1]), sub, body_text))
                    elif sec == "cv/ongoing":
                        rows.append(row(nice_dates(a[3]), tex_to_html(a[1]), tex_to_html(a[0]), items=items))
                    else:  # education, experience, extracurricular …
                        role = tex_to_html(a[0]).replace(" · ", " / ")
                        sub = " · ".join(x for x in (tex_to_html(a[1]), tex_to_html(a[2])) if x)
                        rows.append(row(nice_dates(a[3]), role, sub, items=items))
                elif t == "cvhonor":
                    award, event, loc, dates = (tex_to_html(x) for x in a)
                    rows.append(row(nice_dates(dates), f"{award}, {event}", loc))
                elif t == "cvbrief":
                    rows.append(row(tex_to_html(a[0]), "", items=[tex_to_html(i) for i in parse_items(a[1])]))
                elif t == "cvskill":
                    rows.append(row(tex_to_html(a[0]), tex_to_html(a[1])))
                elif t == "cvparagraph":
                    rows.append(f'          <li><p class="cv-sub">{tex_to_html(a[0])}</p></li>')
            if rows:
                parts.append(f'''        <h2 class="group-title">{title}</h2>
        <ul class="card cv-list">
{chr(10).join(rows)}
        </ul>''')
        return "\n".join(parts)

    # --- pages -------------------------------------------------------------------
    def build(self) -> None:
        s = self.site
        work, edu = self.work_entries(), self.edu_entries()
        pubs = self.publications()
        honors = self.honors()
        pubs_public = [p for p in pubs if not p["under_review"]]

        # ---------------- home
        hero_links = "".join(
            f'''
            <li>
              <a href="{l["url"]}"{'' if l["url"].startswith("mailto:") else ' target="_blank" rel="noopener"'}>
                {l["icon"]}
                {l["label"]}
              </a>
            </li>''' for l in s["links"])
        affils = "".join(f'\n            <li>{link_or_text(html.escape(a["name"]), a.get("url"))}</li>' for a in s["affiliations"])
        topics = "".join(f"\n            <li>{html.escape(t)}</li>" for t in s["topics"])
        selected_honors = [h for h in honors if h["selected"]]
        home_main = f'''    <main id="main" class="container">
      <!-- ================= Hero ================= -->
      <section class="card hero" id="about">
        <div class="hero-text">
          <h1 class="name">{s["name"]}</h1>
          <p class="role">{s["role"]}</p>
          <p class="affil">
            <a href="{s["department_url"]}" target="_blank" rel="noopener">{s["department"]}</a><br />
            <a href="{s["university_url"]}" target="_blank" rel="noopener">{s["university"]}</a>
          </p>
          <p class="email"><span class="obf" data-user="{s["email_user"]}" data-domain="{s["email_domain"]}">{s["email_user"]} [at] {s["email_domain"].replace(".", " [dot] ")}</span></p>

          <div class="affiliations">
            <h2>Current Affiliations</h2>
            <ul>{affils}
            </ul>
          </div>

          <ul class="topics" aria-label="Research interests">{topics}
          </ul>
          <ul class="links" aria-label="Contact and profiles">{hero_links}
          </ul>
        </div>
        <img class="portrait" src="assets/img/profile.jpg" width="756" height="1000" alt="Portrait of {s["name"]}" />
      </section>

      <!-- ================= About ================= -->
      <section class="card prose" aria-label="About">
        {load_snippet("bio_short.html")}
        <div class="bio-more" id="bio-more" hidden>
          {load_snippet("bio_full.html")}
        </div>
        {toggle("", "bio-more", "Read full bio", "Show less")}
      </section>

      <!-- ================= News ================= -->
      <section id="news" class="section">
        <div class="section-head">
          <h2>Latest news</h2>
          <a class="more-link" href="news/index.html">All news →</a>
        </div>
        <ul class="card news">
{self.news_list(self.news[: s.get("home_news", 4)], "")}
        </ul>
      </section>

      <!-- ================= Publications ================= -->
      <section id="publications" class="section">
        <div class="section-head">
          <h2>Publications</h2>
          <a class="more-link" href="publications/index.html">All publications →</a>
        </div>
        <ol class="pubs">
{self.pub_cards([p for p in pubs_public if p["meta"].get("selected", True)], "")}
        </ol>
      </section>

      <!-- ================= Vitae ================= -->
      <section id="vitae" class="section">
        <div class="section-head">
          <h2>Vitæ</h2>
          <a class="more-link" href="vitae/index.html">Full CV →</a>
        </div>
{self.timeline(work + edu, "", s.get("home_timeline", 3))}
      </section>

      <!-- ================= Honors ================= -->
      <section id="honors" class="section">
        <div class="section-head">
          <h2>Selected honors</h2>
          <a class="more-link" href="honors/index.html">All honors →</a>
        </div>
        <ul class="honors">
{self.honor_cards(selected_honors)}
        </ul>
      </section>
    </main>'''
        ldjson = f'''
    <script type="application/ld+json">
      {json.dumps(s["ldjson"], ensure_ascii=False, indent=8).replace(chr(10), chr(10) + "      ")}
    </script>'''
        self.write("index.html", self.page(root="", current="index.html", title="Haebeom Jung", desc=s["description"], path="/", main=home_main, ldjson=ldjson))

        # ---------------- news
        self.write("news/index.html", self.subpage(
            current="news/index.html", title="News", lede="Papers, talks, and milestones, newest first.",
            desc="Recent news and announcements from Haebeom Jung.", path="/news/",
            body=f'        <ul class="card news">\n{self.news_list(self.news, "../")}\n        </ul>'))

        # ---------------- publications
        self.write("publications/index.html", self.subpage(
            current="publications/index.html", title="Publications",
            lede=f'Hover a thumbnail to play the preview. See also <a href="{s["scholar_url"]}" target="_blank" rel="noopener">Google Scholar</a>.',
            desc="Publications by Haebeom Jung on 3D reconstruction, Gaussian splatting, and LiDAR–camera calibration.", path="/publications/",
            body=f'        <ol class="pubs">\n{self.pub_cards(pubs_public, "../")}\n        </ol>'))

        # ---------------- experience
        exp_body = f'''        <h2 class="group-title">Industry</h2>
        <ul class="exp-list">
{self.exp_cards(work, "../")}
        </ul>

        <h2 class="group-title">Education</h2>
        <ul class="exp-list">
{self.exp_cards(edu, "../")}
        </ul>'''
        self.write("experience/index.html", self.subpage(
            current="experience/index.html", title="Experience", lede="",
            desc="Industry and academic experience of Haebeom Jung.", path="/experience/", body=exp_body))

        # ---------------- honors
        self.write("honors/index.html", self.subpage(
            current="honors/index.html", title="Honors &amp; Awards", lede="Scholarships, competition results, and recognitions.",
            desc="Honors, awards, and scholarships received by Haebeom Jung.", path="/honors/",
            body=f'        <ul class="honors">\n{self.honor_cards(honors)}\n        </ul>'))

        # ---------------- vitae
        self.write("vitae/index.html", self.subpage(
            current="vitae/index.html", title="Curriculum Vitae", lede="",
            desc="Curriculum vitae of Haebeom Jung: education, experience, publications, patents, service, and skills.", path="/vitae/",
            body=self.vitae_body()))

        # ---------------- sitemap
        urls = ["/", "/news/", "/publications/", "/experience/", "/honors/", "/vitae/"]
        import datetime as _dt
        today = _dt.date.today().isoformat()
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        sm += "".join(f"  <url><loc>{SITE_URL}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n"
        self.write("sitemap.xml", sm)

    # Cache busting: append a content hash to local asset URLs so browsers pick up
    # new CSS/JS/images immediately after a deploy.
    _VERSIONED = ("assets/css/style.css", "assets/js/main.js", "assets/img/profile.jpg")

    def _asset_hash(self, rel: str) -> str:
        p = ROOT / rel
        return hashlib.md5(p.read_bytes()).hexdigest()[:8] if p.exists() else "0"

    def bust(self, content: str) -> str:
        for rel in self._VERSIONED:
            v = self._asset_hash(rel)
            content = re.sub(rf'((?:\.\./)?{re.escape(rel)})(?=["\')])', rf"\1?v={v}", content)
        return content

    def write(self, rel: str, content: str) -> None:
        if rel.endswith(".html"):
            content = self.bust(content)
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content.rstrip() + "\n", encoding="utf-8")
        print(f"wrote {rel}")


def main(argv: list[str]) -> None:
    fetch = "--no-fetch" not in argv
    ensure_cv_source(fetch)
    if "--pdf" in argv:
        build_pdf()
    if "--pdf" in argv or "--ci" in argv:
        copy_pdf()
    Site(fetch).build()


if __name__ == "__main__":
    main(sys.argv[1:])
