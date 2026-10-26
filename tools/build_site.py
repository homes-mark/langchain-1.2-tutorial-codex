"""Build standalone HTML. Run from any cwd: python tools/build_site.py."""
import html
import json
import re
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename

ROOT = Path(__file__).resolve().parents[1]
FORMATTER = HtmlFormatter(nowrap=True, style="monokai")
PAGES = [json.loads(p.read_text(encoding="utf-8-sig"))
         for p in sorted((ROOT / "content").glob("*.json"))]
PAGES.sort(key=lambda p: (p["slug"] != "index", p["slug"]))
assert PAGES and PAGES[0]["slug"] == "index", "Missing index content"
assert len({p["slug"] for p in PAGES}) == len(PAGES)


def code_block(code, language="python", path=None):
    lexer = get_lexer_by_name(language)
    source = f'<a href="{html.escape(path)}" download>下载源文件 ↗</a>' if path else ""
    return (f'<div class="codebox"><div class="codebar"><span>{html.escape(path or language)}</span>'
            f'{source}<button type="button" class="copy-code">复制代码</button></div>'
            f'<pre tabindex="0"><code class="highlight language-{language}">'
            + highlight(code, lexer, FORMATTER) + '</code></pre></div>')


def render_body(body):
    def embed(match):
        attrs = dict(re.findall(r'(\w+)="([^"]+)"', match.group(1)))
        path = attrs["path"]
        file = (ROOT / path).resolve()
        assert file.is_relative_to(ROOT), path
        code = file.read_text(encoding="utf-8-sig")
        if "region" in attrs:
            found = re.search(r'^\s*# region ' + re.escape(attrs["region"]) +
                              r'\s*\n(.*?)^\s*# endregion[^\n]*', code, re.M | re.S)
            assert found, f'Missing region {attrs["region"]} in {path}'
            code = found.group(1)
        language = get_lexer_for_filename(file.name).aliases[0]
        return code_block(code, language, path)
    body = re.sub(r'<example\s+([^>]+)>\s*</example>', embed, body)
    def inline(match):
        return code_block(html.unescape(match.group(2)), match.group(1))
    return re.sub(r'<pre><code class="language-([\w+-]+)">(.*?)</code></pre>', inline, body, flags=re.S)


def nav(current):
    chunks = []
    previous = None
    for p in PAGES:
        if p["chapter"] != previous:
            chunks.append(f'<div class="nav-group">{html.escape(p["chapter"])}</div>')
            previous = p["chapter"]
        active = ' aria-current="page"' if p["slug"] == current else ''
        chunks.append(f'<a href="{p["slug"]}.html" data-page="{p["slug"]}"{active}>'
                      f'<span class="status-dot" aria-hidden="true"></span>{html.escape(p["title"])}</a>')
    return ''.join(chunks)


for i, p in enumerate(PAGES):
    slug = p["slug"]
    sections = p["sections"]
    assert len({s["id"] for s in sections}) == len(sections), slug
    toc = ''.join(f'<a href="#{s["id"]}">{html.escape(s["title"])}</a>' for s in sections)
    body = ''.join(f'<section id="{s["id"]}"><h2><a href="#{s["id"]}" aria-label="链接到本节">'
                   f'<span class="section-no">{j+1:02d}</span>{html.escape(s["title"])}</a></h2>'
                   f'{render_body(s["body"])}</section>' for j, s in enumerate(sections))
    goals = ''.join(f'<li>{html.escape(g)}</li>' for g in p["goals"])
    prerequisites = ' · '.join(html.escape(x) for x in p["prerequisites"])
    sources = ''.join(f'<li><a href="{html.escape(s["url"])}" rel="noreferrer">{html.escape(s["title"])}</a></li>'
                      for s in p.get("sources", []))
    adjacent = []
    for pos, label in ((i-1, "← 上一页"), (i+1, "下一页 →")):
        if 0 <= pos < len(PAGES):
            other = PAGES[pos]
            adjacent.append(f'<a href="{other["slug"]}.html"><small>{label}</small>{html.escape(other["title"])}</a>')
    index_class = " home" if slug == "index" else ""
    output = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(p['summary'])}"><title>{html.escape(p['title'])} · LangChain 1.2 中文教程</title>
<link rel="stylesheet" href="assets/site.css"><link rel="stylesheet" href="assets/syntax.css">
<script src="assets/site.js" defer></script></head>
<body data-slug="{slug}"><a class="skip" href="#main">跳到正文</a>
<header class="mobile-header"><a href="index.html">LC / 1.2 学习手册</a><button id="menu-toggle" aria-controls="sidebar" aria-expanded="false">课程目录</button></header>
<aside class="sidebar" id="sidebar"><a class="brand" href="index.html"><span class="brand-icon">LC</span><span>LangChain <b>1.2</b><small>从概念到企业智能体</small></span></a>
<div class="edition">PYTHON EDITION · 离线学习版</div><label class="search-label" for="nav-search">查找章节</label><input id="nav-search" type="search" placeholder="搜索：RAG、工具、记忆…">
<nav class="course-nav" aria-label="全站学习目录">{nav(slug)}</nav>
<div class="sidebar-bottom"><span class="offline-dot"></span>全部内容与资源均可离线阅读<a href="HANDOFF.md">维护与交接 ↗</a></div></aside>
<div class="workspace"><div class="topline"><span>学习手册 / {html.escape(p['chapter'])}</span><span>版本基线 1.2.0</span></div>
<div class="reading-layout"><main id="main" class="article{index_class}">
<div class="eyebrow">{html.escape(p['chapter'])} <span>·</span> {html.escape(p['level'])}</div>
<h1>{html.escape(p['title'])}</h1><p class="lead">{html.escape(p['summary'])}</p>
<div class="meta"><span class="pill">{html.escape(p['level'])}</span><span>建议 {p['minutes']} 分钟</span><span>顺序 {i+1:02d} / {len(PAGES):02d}</span></div>
<div class="learning-card"><div><h3>本章学习目标</h3><ul>{goals}</ul></div><div><h3>前置知识</h3><p>{prerequisites}</p><p class="small">推荐按左侧目录顺序学习；熟悉基础后可从实战阶段一开始。</p></div></div>
<details class="inline-toc"><summary>本页目录 · {len(sections)} 节</summary><nav aria-label="本页目录">{toc}</nav></details>
{body}<section id="sources"><h2>资料与版本依据</h2><p class="small">核对日期：2026-10-26。官方网页可能随新版本更新；本教程 API 以锁定依赖和本地验证为准。以下外部参考链接需联网，正文与代码阅读无需联网。</p><ul class="sources">{sources}</ul></section>
<div class="completion"><label><input type="checkbox" id="page-complete"> 我已完成本页阅读与练习</label><a href="#main">回到顶部 ↑</a></div>
<nav class="page-nav" aria-label="前后章节">{''.join(adjacent)}</nav>
<footer>LangChain 1.2 中文学习手册 · 原创教学示例 · <a href="21-reference.html">版本、术语与交付清单</a></footer>
</main><aside class="rightbar"><div class="progress-card"><div class="eyebrow">我的学习进度</div><strong id="progress-text">0 / {len(PAGES)}</strong><progress id="course-progress" max="{len(PAGES)}" value="0" aria-label="课程完成进度"></progress><p id="progress-note">进度仅保存在本地浏览器。</p><div class="progress-actions"><button id="export-progress">导出</button><label class="button" for="import-progress">导入</label><input type="file" id="import-progress" accept="application/json,.json" hidden></div><p id="progress-message" role="status" aria-live="polite"></p></div><nav class="page-toc" aria-label="本页快捷导航"><h3>ON THIS PAGE</h3>{toc}<a href="#sources">资料与版本依据</a></nav></aside></div></div>
<noscript><div class="noscript">JavaScript 未开启：正文、目录和高亮可正常阅读；完成标记与进度导入导出需开启 JavaScript。</div></noscript>
</body></html>'''
    (ROOT / f'{slug}.html').write_text(output, encoding="utf-8")
(ROOT / "assets/syntax.css").write_text(FORMATTER.get_style_defs('.highlight'), encoding="utf-8")
(ROOT / "assets/catalog.json").write_text(json.dumps([{k:p[k] for k in ('slug','title','chapter','level','minutes')} for p in PAGES], ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Built {len(PAGES)} self-contained pages (shared local CSS/JS).")
