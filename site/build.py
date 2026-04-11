#!/usr/bin/env -S uv run --quiet --with pyyaml --with jinja2 --with markdown python3
"""Build the Southern Cross Financial bespoke site.

Reads ensayo-generated content from ../content/ and ../jobs.json,
combines with hand-crafted templates and styles, and renders the
static site to ../dist/.

Usage:
    ./site/build.py              # build to ../dist/
    ./site/build.py serve        # build then serve on :8004 for local preview

Requires `uv` to be installed (https://docs.astral.sh/uv/) — pyyaml,
jinja2, and markdown are pulled in via the shebang.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import markdown as md
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

# --- Paths ---
SITE_DIR = Path(__file__).parent
ROOT = SITE_DIR.parent
CONTENT_DIR = ROOT / "content"
JOBS_FILE = ROOT / "jobs.json"
BRIEF_FILE = ROOT / "brief.yaml"
DIST_DIR = ROOT / "dist"

TEMPLATES_DIR = SITE_DIR / "templates"
STYLES_DIR = SITE_DIR / "styles"
SCRIPTS_DIR = SITE_DIR / "scripts"
ASSETS_DIR = SITE_DIR / "assets"


# --- Frontmatter loader ---
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file.

    Handles three variants the upstream generator sometimes emits:
      1. Plain `---\\nyaml\\n---\\nbody`
      2. Code-fenced wrapper around the whole thing: ```yaml\\n---\\nyaml\\n---\\nbody```
      3. Code-fenced YAML block followed by markdown body, with no inner `---`:
         ```yaml\\nyaml\\n```\\nbody
    """
    text = text.strip()

    # Variant 3: ```yaml ... ``` then body, no inner `---`
    if text.startswith("```"):
        # Find the closing fence (first ``` after the opening line)
        opening_nl = text.find("\n")
        if opening_nl != -1:
            rest = text[opening_nl + 1:]
            close_idx = rest.find("\n```")
            if close_idx != -1:
                yaml_block = rest[:close_idx]
                body = rest[close_idx + len("\n```"):].strip()
                # If the yaml block contains a `---` it's actually variant 2 — fall through
                if "---" not in yaml_block:
                    try:
                        meta = yaml.safe_load(yaml_block) or {}
                    except yaml.YAMLError:
                        meta = {}
                    return meta, body
        # Otherwise strip the wrapping fence and fall through to variant 1/2 parsing
        first_nl = text.find("\n")
        if first_nl != -1:
            text = text[first_nl + 1:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, m.group(2).strip()


def load_employees() -> list[dict]:
    """Load all employees from content/employees/*.md."""
    emp_dir = CONTENT_DIR / "employees"
    if not emp_dir.is_dir():
        return []
    employees = []
    for md_file in sorted(emp_dir.glob("*.md")):
        if md_file.stem.endswith("-prompt"):
            continue  # skip the prompt files
        meta, body = parse_frontmatter(md_file.read_text(encoding="utf-8"))
        meta["body"] = body
        meta["slug"] = md_file.stem
        # Initials for placeholder headshots
        name = meta.get("name", md_file.stem.replace("-", " ").title())
        parts = name.replace("Dr.", "").strip().split()
        meta["initials"] = "".join(p[0].upper() for p in parts[:2] if p)
        employees.append(meta)
    return employees


def load_documents() -> dict:
    """Load support and policy documents from content/docs/."""
    docs = {"support": [], "policy": []}
    for category in ("support", "policy"):
        cat_dir = CONTENT_DIR / "docs" / category
        if not cat_dir.is_dir():
            continue
        for md_file in sorted(cat_dir.glob("*.md")):
            meta, body = parse_frontmatter(md_file.read_text(encoding="utf-8"))
            meta["body"] = body
            meta["slug"] = md_file.stem
            meta["category"] = category
            docs[category].append(meta)
    return docs


def load_brief() -> dict:
    """Load brief.yaml — the company profile and scenario."""
    if not BRIEF_FILE.is_file():
        return {}
    return yaml.safe_load(BRIEF_FILE.read_text(encoding="utf-8")) or {}


def load_jobs() -> dict:
    """Load jobs.json — the job listings (and company business hours, etc.)."""
    if not JOBS_FILE.is_file():
        return {}
    return json.loads(JOBS_FILE.read_text(encoding="utf-8"))


# --- Build ---


def render_markdown(text: str) -> Markup:
    """Render markdown to HTML, safe for inclusion in templates."""
    if not text:
        return Markup("")
    html = md.markdown(
        text,
        extensions=["extra", "sane_lists", "smarty"],
    )
    return Markup(html)


def setup_jinja() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["markdown"] = render_markdown
    return env


def render_page(env: Environment, template_name: str, output_path: Path, **context):
    template = env.get_template(template_name)
    html = template.render(**context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"  ✓ {output_path.relative_to(ROOT)}")


def copy_static_assets():
    """Copy CSS, JS, and assets into dist/."""
    # Styles
    target_styles = DIST_DIR / "styles"
    if STYLES_DIR.is_dir():
        if target_styles.exists():
            shutil.rmtree(target_styles)
        shutil.copytree(STYLES_DIR, target_styles)

    # Scripts
    target_scripts = DIST_DIR / "scripts"
    if SCRIPTS_DIR.is_dir():
        if target_scripts.exists():
            shutil.rmtree(target_scripts)
        shutil.copytree(SCRIPTS_DIR, target_scripts)

    # Assets (images, headshots, icons)
    target_assets = DIST_DIR / "assets"
    if ASSETS_DIR.is_dir():
        if target_assets.exists():
            shutil.rmtree(target_assets)
        shutil.copytree(ASSETS_DIR, target_assets)


def build():
    print(f"Building Southern Cross Financial → {DIST_DIR}")
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # Clean dist/ but keep .git, CNAME, .nojekyll if present
    for item in DIST_DIR.iterdir():
        if item.name in (".git", "CNAME", ".nojekyll"):
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # Load data
    brief = load_brief()
    employees = load_employees()
    docs = load_documents()
    jobs_data = load_jobs()

    # Common context
    company = brief.get("company", {})
    profile = company.get("profile", {})
    scenario = company.get("scenario", {})
    branding = brief.get("branding", {}).get("colors", {})

    ctx = {
        "company": company,
        "profile": profile,
        "scenario": scenario,
        "branding": branding,
        "employees": employees,
        "docs": docs,
        "jobs": jobs_data.get("jobs", []),
        "company_url": jobs_data.get("company_url", ""),
        "year": 2026,
    }

    env = setup_jinja()

    # --- Public pages ---
    pages = [
        ("index.html.j2", "index.html"),
        ("about.html.j2", "about.html"),
        ("services.html.j2", "services.html"),
        ("careers.html.j2", "careers.html"),
        ("contact.html.j2", "contact.html"),
    ]
    for template, output in pages:
        render_page(env, template, DIST_DIR / output, page=output.replace(".html", ""), **ctx)

    # --- Job detail pages ---
    careers_dir = DIST_DIR / "careers"
    careers_dir.mkdir(exist_ok=True)
    for job in ctx["jobs"]:
        slug = job["slug"]
        render_page(
            env,
            "job-detail.html.j2",
            careers_dir / f"{slug}.html",
            job=job,
            page="careers",
            **ctx,
        )

    # --- Staff section (gated by client-side auth, content via API) ---
    staff_dir = DIST_DIR / "staff"
    staff_dir.mkdir(exist_ok=True)
    render_page(env, "staff/login.html.j2", staff_dir / "login.html", page="staff", **ctx)
    render_page(env, "staff/index.html.j2", staff_dir / "index.html", page="staff", **ctx)
    render_page(env, "staff/directory.html.j2", staff_dir / "directory.html", page="staff", **ctx)
    render_page(env, "staff/documents.html.j2", staff_dir / "documents.html", page="staff", **ctx)

    # --- Static assets ---
    copy_static_assets()
    print(f"  ✓ assets copied")

    # CNAME for GitHub Pages custom domain
    cname_file = DIST_DIR / "CNAME"
    if not cname_file.exists():
        cname_file.write_text("southerncrossfinancial.eduserver.au\n", encoding="utf-8")
        print("  ✓ CNAME")

    # Disable Jekyll processing
    nojekyll = DIST_DIR / ".nojekyll"
    if not nojekyll.exists():
        nojekyll.touch()

    print("\nDone.")


def serve():
    """Build then serve the dist directory on :8004 for local preview."""
    import http.server
    import socketserver
    import os

    build()
    os.chdir(DIST_DIR)
    PORT = 8004
    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        print(f"\nServing Southern Cross at http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve()
    else:
        build()
