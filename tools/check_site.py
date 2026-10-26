"""Check offline HTML, content contracts and Python syntax using only stdlib.

Run after build_site.py: python tools/check_site.py
This checks static evidence; browser interaction and live APIs need separate tests.
"""
from __future__ import annotations

import ast
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.references = []
        self.remote_loads = []
        self.lang = ""
        self.title = ""
        self.in_title = False
        self.has_toc = False
        self.has_course_nav = False
        self.has_completion = False
        self.has_progress = False
        self.highlighted_blocks = 0
        self.unexpanded_examples = 0
        self.invalid_urls = []
        self.in_resource_tag = False
        self.inline_resource_text = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.append(attributes["id"])
        if tag == "html":
            self.lang = attributes.get("lang", "")
        if tag == "title":
            self.in_title = True
        if tag in {"script", "style"}:
            self.in_resource_tag = True
        if attributes.get("style"):
            self.inline_resource_text.append(attributes["style"])
        if tag == "example":
            self.unexpanded_examples += 1
        classes = attributes.get("class", "").split()
        if tag == "nav":
            self.has_toc |= "page-toc" in classes or "本页" in attributes.get("aria-label", "")
            self.has_course_nav |= "course-nav" in classes or "全站" in attributes.get("aria-label", "")
        if tag == "input" and attributes.get("type") == "checkbox":
            self.has_completion |= attributes.get("id") == "page-complete"
        if tag == "progress":
            self.has_progress = True
        if tag == "code" and "highlight" in classes:
            self.highlighted_blocks += 1
        for name in ("href", "src", "poster", "data"):
            if not attributes.get(name):
                continue
            url = attributes[name]
            self.references.append((tag, name, url))
            parts = urlsplit(url)
            if parts.scheme.lower() in {"javascript", "vbscript"}:
                self.invalid_urls.append(url)
            if (parts.scheme in {"http", "https"} or parts.netloc) and tag != "a":
                self.remote_loads.append((tag, name, url))
            if tag == "base":
                self.invalid_urls.append("base href changes offline URL resolution")
        if attributes.get("srcset"):
            for candidate in attributes["srcset"].split(","):
                url = candidate.strip().split()[0] if candidate.strip() else ""
                if url:
                    self.references.append((tag, "srcset", url))
                    parts = urlsplit(url)
                    if parts.scheme in {"http", "https"} or parts.netloc:
                        self.remote_loads.append((tag, "srcset", url))
        if tag == "meta" and attributes.get("http-equiv", "").lower() == "refresh":
            self.invalid_urls.append("meta refresh is not allowed in offline tutorial pages")

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag in {"script", "style"}:
            self.in_resource_tag = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_resource_tag:
            self.inline_resource_text.append(data)


def check_site(root: Path = ROOT) -> dict:
    root = root.resolve()
    failures = []
    content = []
    for path in sorted((root / "content").glob("*.json")):
        try:
            page = json.loads(path.read_text(encoding="utf-8-sig"))
            required = {"slug", "title", "chapter", "level", "minutes", "summary",
                        "goals", "prerequisites", "sections", "sources"}
            missing = sorted(required - page.keys())
            if missing:
                raise ValueError(f"missing keys: {missing}")
            for field in ("slug", "title", "chapter", "level", "summary"):
                if not isinstance(page[field], str) or not page[field].strip():
                    raise ValueError(f"{field} must be a nonempty string")
            if page["level"] not in {"入门", "进阶", "高级"}:
                raise ValueError("level must be 入门 / 进阶 / 高级")
            if not isinstance(page["minutes"], (int, float)) or page["minutes"] <= 0:
                raise ValueError("minutes must be positive")
            if not re.fullmatch(r"[a-z0-9-]+", page["slug"]):
                raise ValueError("slug must use lowercase URL-safe characters")
            for field in ("goals", "prerequisites"):
                if not isinstance(page[field], list) or not page[field] or not all(
                    isinstance(value, str) and value.strip() for value in page[field]
                ):
                    raise ValueError(f"{field} must contain nonempty strings")
            if not isinstance(page["sections"], list) or not page["sections"]:
                raise ValueError("sections must be a nonempty list")
            for section in page["sections"]:
                if not all(isinstance(section.get(key), str) and section[key].strip()
                           for key in ("id", "title", "body")):
                    raise ValueError("section must provide id/title/body strings")
            section_ids = [section["id"] for section in page["sections"]]
            if len(section_ids) != len(set(section_ids)):
                raise ValueError("duplicate section id")
            if "sources" in section_ids or "main" in section_ids:
                raise ValueError("section id collides with generated page structure")
            if not isinstance(page["sources"], list):
                raise ValueError("sources must be a list")
            for source in page["sources"]:
                if not source.get("title") or urlsplit(source.get("url", "")).scheme not in {"http", "https"}:
                    raise ValueError("source needs a title and HTTP(S) URL")
            content.append(page)
        except (ValueError, TypeError, KeyError) as error:
            failures.append(f"{path.relative_to(root)}: {error}")
    if not content:
        failures.append("No valid content JSON pages found")
    duplicate_slugs = [slug for slug, count in Counter(p["slug"] for p in content).items() if count > 1]
    if duplicate_slugs:
        failures.append(f"Duplicate content slugs: {duplicate_slugs}")

    pages = {}
    for path in sorted(root.glob("*.html")):
        parser = PageParser()
        try:
            parser.feed(path.read_text(encoding="utf-8-sig"))
            parser.close()
        except (ValueError, UnicodeError) as error:
            failures.append(f"{path.name}: cannot parse HTML: {error}")
            continue
        pages[path.resolve()] = parser
    if not pages:
        failures.append("No generated root HTML pages found; run tools/build_site.py first")
    expected = {root / f"{page['slug']}.html" for page in content}
    for path in expected - pages.keys():
        failures.append(f"Missing generated HTML: {path.name}")
    for path in pages.keys() - expected:
        failures.append(f"Generated HTML has no matching content JSON: {path.name}")

    local_reference_count = 0
    for path, page in pages.items():
        name = path.name
        duplicate_ids = [identifier for identifier, count in Counter(page.ids).items() if count > 1]
        if duplicate_ids:
            failures.append(f"{name}: duplicate HTML IDs {duplicate_ids}")
        checks = {
            "nonempty title": bool(page.title.strip()),
            "Chinese html lang": page.lang.lower().startswith("zh"),
            "page table of contents": page.has_toc,
            "global course navigation": page.has_course_nav,
            "completion checkbox": page.has_completion,
            "progress element": page.has_progress,
            "syntax-highlighted code": page.highlighted_blocks > 0,
            "expanded example embeds": page.unexpanded_examples == 0,
        }
        for check, passed in checks.items():
            if not passed:
                failures.append(f"{name}: missing/invalid {check}")
        for tag, attribute, url in page.remote_loads:
            failures.append(f"{name}: remote automatic resource {tag}[{attribute}]={url}")
        for invalid in page.invalid_urls:
            failures.append(f"{name}: unsafe URL behavior: {invalid}")
        for text in page.inline_resource_text:
            if re.search(r"(?:https?:)?//[^\s'\"<>]+", text):
                failures.append(f"{name}: remote URL in inline script/style needs removal or review")
        for tag, attribute, url in page.references:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc:
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            local_reference_count += 1
            if not target.is_relative_to(root):
                failures.append(f"{name}: reference escapes tutorial directory: {url}")
                continue
            if not target.exists():
                failures.append(f"{name}: missing local {tag}[{attribute}] target: {url}")
                continue
            if parts.fragment and target.suffix.lower() == ".html":
                target_page = pages.get(target)
                if target_page is None:
                    failures.append(f"{name}: linked HTML outside root-page validation: {url}")
                elif unquote(parts.fragment) not in target_page.ids:
                    failures.append(f"{name}: missing fragment target: {url}")

    # CSS URLs are auto-loaded even though HTML only links the local stylesheet.
    for path in sorted((root / "assets").rglob("*.css")):
        text = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8-sig"), flags=re.S)
        urls = re.findall(r"url\(\s*['\"]?([^)'\"]+)", text)
        urls += re.findall(r"@import\s+['\"]([^'\"]+)", text)
        for url in urls:
            parts = urlsplit(url.strip())
            if parts.scheme in {"http", "https"} or parts.netloc:
                failures.append(f"{path.relative_to(root)}: remote CSS resource {url}")
            elif not parts.scheme and parts.path:
                target = (path.parent / unquote(parts.path)).resolve()
                if not target.is_relative_to(root) or not target.exists():
                    failures.append(f"{path.relative_to(root)}: missing/outside CSS resource {url}")

    # Reject remote string literals in local JS as a conservative CDN/network check.
    # This does not prove that obfuscated or dynamically built URLs cannot exist.
    for path in sorted((root / "assets").rglob("*.js")):
        script = path.read_text(encoding="utf-8-sig")
        if re.search(r"['\"`](?:https?:)?//[^'\"`\s]+", script):
            failures.append(f"{path.relative_to(root)}: remote URL literal in JavaScript")

    python_count = 0
    for directory in ("examples", "project", "tools"):
        for path in sorted((root / directory).rglob("*.py")):
            python_count += 1
            try:
                ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            except (SyntaxError, UnicodeError) as error:
                failures.append(f"{path.relative_to(root)}: invalid Python syntax: {error}")
    return {"status": "passed" if not failures else "failed", "html_pages": len(pages),
            "content_pages": len(content), "local_references_checked": local_reference_count,
            "python_files_parsed": python_count, "failures": failures,
            "limitations": ["Static HTML checks do not replace browser interaction tests.",
                            "External reference URLs and live model providers are not exercised."]}


if __name__ == "__main__":
    report = check_site()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["status"] == "passed" else 1)
