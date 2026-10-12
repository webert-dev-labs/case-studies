"""Build the case studies website (docs/index.html) from cases.json.

Usage, from the repository root:
    python tools/build_site.py

The page is fully static: no external fonts, scripts, trackers or forms.
"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "cases.json"
OUT_FILE = ROOT / "docs" / "index.html"

# Static page: no scripts, nothing loaded from other hosts, same-origin images only.
CSP = (
    "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; "
    "base-uri 'none'; form-action 'none'"
)

REQUIRED_CASE_FIELDS = (
    "slug", "title", "scenario", "problem", "solution", "result",
    "highlights", "stack", "image", "image_alt", "path",
)


def load_data(path: Path = DATA_FILE) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate(data)
    return data


def validate(data: dict) -> None:
    """Fail early with a clear message when cases.json is incomplete."""
    for key in ("title", "tagline", "intro", "owner", "repo_url", "profile_url",
                "site_url", "social_image", "year"):
        if key not in data.get("site", {}):
            raise ValueError(f"site.{key} is missing in cases.json")
    slugs = set()
    for i, case in enumerate(data.get("cases", [])):
        missing = [f for f in REQUIRED_CASE_FIELDS if not case.get(f)]
        if missing:
            raise ValueError(f"case #{i + 1} is missing: {', '.join(missing)}")
        if case["slug"] in slugs:
            raise ValueError(f"duplicate case slug: {case['slug']}")
        slugs.add(case["slug"])


def _highlights(case: dict) -> str:
    items = "".join(
        f'<li><span class="hl-value">{escape(h["value"])}</span>'
        f'<span class="hl-label">{escape(h["label"])}</span></li>'
        for h in case["highlights"]
    )
    return f'<ul class="highlights">{items}</ul>'


def _case(case: dict, index: int, repo_url: str) -> str:
    code_url = f"{repo_url}/tree/main/{case['path']}"
    demo = (
        f'<a class="btn btn-primary" href="{escape(case["demo"])}">Open live report</a>'
        if case.get("demo")
        else ""
    )
    stack = "".join(f"<li>{escape(s)}</li>" for s in case["stack"])
    return f"""
    <article class="case" id="{escape(case['slug'])}">
      <a class="case-media" href="{escape(case.get('demo') or code_url)}">
        <img src="{escape(case['image'])}" alt="{escape(case['image_alt'])}" loading="lazy">
      </a>
      <div class="case-body">
        <p class="case-index">Case {index:02d}</p>
        <h3>{escape(case['title'])}</h3>
        <p class="scenario">{escape(case['scenario'])}</p>
        <dl class="psr">
          <div><dt>Problem</dt><dd>{escape(case['problem'])}</dd></div>
          <div><dt>Solution</dt><dd>{escape(case['solution'])}</dd></div>
          <div><dt>Result</dt><dd>{escape(case['result'])}</dd></div>
        </dl>
        {_highlights(case)}
        <ul class="stack" aria-label="Technologies">{stack}</ul>
        <div class="actions">
          {demo}
          <a class="btn btn-secondary" href="{escape(code_url)}">View code</a>
        </div>
      </div>
    </article>"""


STYLE = """
:root {
  --bg: #f7f7f5; --surface: #ffffff; --text: #111111; --muted: #55534e;
  --line: #e4e3df; --accent: #2a78d6; --accent-text: #ffffff; --chip: #eef3fb;
  --chip-text: #1d5aa3; --shadow: 0 1px 2px rgba(0,0,0,.04), 0 8px 24px rgba(0,0,0,.06);
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #121212; --surface: #1c1c1b; --text: #f0efec; --muted: #b5b3ab;
    --line: #2e2e2c; --accent: #3987e5; --accent-text: #ffffff; --chip: #1f2a3a;
    --chip-text: #9cc3f5; --shadow: none;
  }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--text); line-height: 1.6;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; }
a { color: inherit; }
a:focus-visible, .btn:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
.wrap { max-width: 1080px; margin: 0 auto; padding: 0 20px; }
header.top { border-bottom: 1px solid var(--line); }
header.top .wrap { display: flex; align-items: center; justify-content: space-between; height: 60px; }
.brand { font-weight: 700; text-decoration: none; letter-spacing: -.01em; }
.top nav a { color: var(--muted); text-decoration: none; margin-left: 20px; font-size: .95rem; }
.top nav a:hover { color: var(--text); }
.hero { padding: 72px 0 48px; }
.eyebrow { color: var(--accent); font-weight: 600; font-size: .85rem; letter-spacing: .08em;
  text-transform: uppercase; margin: 0 0 12px; }
.hero h1 { font-size: clamp(2rem, 5vw, 3.2rem); line-height: 1.1; letter-spacing: -.02em; margin: 0 0 16px; }
.hero p.lead { font-size: 1.15rem; color: var(--muted); max-width: 640px; margin: 0; }
section { padding: 32px 0; }
h2 { font-size: 1.4rem; letter-spacing: -.01em; margin: 0 0 24px; }
.case { display: grid; grid-template-columns: 1.05fr 1fr; gap: 0; background: var(--surface);
  border: 1px solid var(--line); border-radius: 16px; overflow: hidden; box-shadow: var(--shadow);
  margin-bottom: 28px; }
.case-media { display: block; position: relative; background: #fcfcfb; border-right: 1px solid var(--line);
  min-height: 360px; overflow: hidden; }
.case-media img { position: absolute; inset: 0; width: 100%; height: 100%;
  object-fit: cover; object-position: top center; transition: transform .3s ease; }
.case-media:hover img { transform: scale(1.02); }
.case-body { padding: 28px 28px 24px; }
.case-index { color: var(--muted); font-size: .8rem; font-weight: 600; letter-spacing: .08em;
  text-transform: uppercase; margin: 0 0 4px; }
.case h3 { font-size: 1.5rem; margin: 0 0 4px; letter-spacing: -.01em; }
.scenario { color: var(--muted); margin: 0 0 18px; font-size: .95rem; }
.psr { margin: 0 0 20px; display: grid; gap: 10px; }
.psr div { display: grid; grid-template-columns: 84px 1fr; gap: 12px; }
.psr dt { font-weight: 600; font-size: .9rem; }
.psr dd { margin: 0; color: var(--muted); font-size: .95rem; }
.highlights { list-style: none; padding: 16px 0; margin: 0 0 16px; display: grid;
  grid-template-columns: repeat(4, 1fr); gap: 8px; border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line); }
.highlights li { display: flex; flex-direction: column; }
.hl-value { font-size: 1.25rem; font-weight: 700; font-variant-numeric: tabular-nums; }
.hl-label { font-size: .78rem; color: var(--muted); line-height: 1.3; }
.stack { list-style: none; padding: 0; margin: 0 0 20px; display: flex; flex-wrap: wrap; gap: 6px; }
.stack li { background: var(--chip); color: var(--chip-text); font-size: .8rem; font-weight: 600;
  padding: 3px 10px; border-radius: 999px; }
.actions { display: flex; flex-wrap: wrap; gap: 10px; }
.btn { display: inline-block; padding: 10px 18px; border-radius: 10px; font-weight: 600;
  font-size: .95rem; text-decoration: none; border: 1px solid transparent; }
.btn-primary { background: var(--accent); color: var(--accent-text); }
.btn-primary:hover { filter: brightness(1.08); }
.btn-secondary { border-color: var(--line); background: var(--surface); }
.btn-secondary:hover { border-color: var(--muted); }
.pillars { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.pillar { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 18px; }
.pillar h3 { font-size: 1rem; margin: 0 0 6px; }
.pillar p { margin: 0; color: var(--muted); font-size: .92rem; }
.privacy { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 20px 24px; }
.privacy ul { margin: 0; padding-left: 20px; color: var(--muted); }
footer { border-top: 1px solid var(--line); margin-top: 40px; padding: 28px 0 40px;
  color: var(--muted); font-size: .88rem; }
footer .wrap { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px; }
@media (max-width: 860px) {
  .case { grid-template-columns: 1fr; }
  .case-media { border-right: 0; border-bottom: 1px solid var(--line); min-height: 0;
    aspect-ratio: 10 / 7; }
  .pillars { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 520px) {
  .wrap { padding: 0 16px; }
  .hero { padding: 48px 0 32px; }
  .case-body { padding: 20px 18px; }
  .highlights { grid-template-columns: repeat(2, 1fr); row-gap: 14px; }
  .psr div { grid-template-columns: 1fr; gap: 0; }
  .pillars { grid-template-columns: 1fr; }
  .top nav a:first-child { display: none; }
}
"""

PILLARS = [
    ("Business framing", "Problem, solution and measurable result, in plain language."),
    ("Working code", "Runs locally in a few commands, with pinned dependencies."),
    ("Automated tests", "Core logic covered by tests that run before every change."),
    ("Sample output", "Reports and screenshots you can explore without installing anything."),
]


def render(data: dict) -> str:
    site = data["site"]
    cases = data["cases"]
    case_html = "".join(_case(c, i + 1, site["repo_url"]) for i, c in enumerate(cases))
    pillars = "".join(
        f'<div class="pillar"><h3>{escape(t)}</h3><p>{escape(d)}</p></div>' for t, d in PILLARS
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="no-referrer">
<title>{escape(site['title'])} · {escape(site['owner'])}</title>
<meta name="description" content="{escape(site['tagline'])} {escape(site['intro'])}">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="{escape(site['site_url'])}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(site['title'])} · {escape(site['owner'])}">
<meta property="og:description" content="{escape(site['tagline'])}">
<meta property="og:url" content="{escape(site['site_url'])}">
<meta property="og:image" content="{escape(site['site_url'] + site['social_image'])}">
<meta property="og:image:width" content="1280">
<meta property="og:image:height" content="640">
<meta name="twitter:card" content="summary_large_image">
<style>{STYLE}</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="brand" href="#">{escape(site['owner'])}</a>
    <nav>
      <a href="#cases">Case studies</a>
      <a href="{escape(site['profile_url'])}">GitHub</a>
    </nav>
  </div>
</header>
<main>
  <div class="wrap">
    <section class="hero">
      <p class="eyebrow">{escape(site['title'])}</p>
      <h1>{escape(site['tagline'])}</h1>
      <p class="lead">{escape(site['intro'])}</p>
    </section>

    <section id="cases" aria-label="Case studies">
      {case_html}
    </section>

    <section aria-labelledby="pillars-title">
      <h2 id="pillars-title">What every case study includes</h2>
      <div class="pillars">{pillars}</div>
    </section>

    <section aria-labelledby="privacy-title">
      <div class="privacy">
        <h2 id="privacy-title">Data and privacy</h2>
        <ul>
          <li>All companies, people, products and figures are fictitious and generated by code with a fixed random seed.</li>
          <li>The code and this site do not call external services, use trackers or collect any data.</li>
        </ul>
      </div>
    </section>
  </div>
</main>
<footer>
  <div class="wrap">
    <span>© {escape(str(site['year']))} {escape(site['owner'])}. All rights reserved.</span>
    <span>Shared for demonstration purposes only.</span>
  </div>
</footer>
</body>
</html>
"""


def main() -> None:
    data = load_data()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(render(data), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(ROOT)} with {len(data['cases'])} case(s)")


if __name__ == "__main__":
    main()
