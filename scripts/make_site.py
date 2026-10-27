#!/usr/bin/env python3
"""make_site.py — 从 issues/ 与 appendices/ 生成静态站点到 web/

设计要点
--------
1. 纯标准库，不装任何依赖。Cloudflare Pages 只做静态托管，构建在本地完成。
2. 公式保留 LaTeX 原样，输出成 $...$，由页面里的 MathJax CDN 运行时渲染。
   源文件里写作 `$x$`（美元符夹反引号），生成时剥掉反引号——MathJax 把
   反引号当字面字符，会渲染成 `x`，多两个反引号。
3. 源文件里的 .md 链接改写成 .html，路径按 issues/ appendices/ 同构映射。
4. 每个文件取首个 h1 作页面标题，其余 h1 降为 h2（附录里有多个 h1）。

用法
----
    python3 scripts/make_site.py            # 生成到 web/
    python3 scripts/make_site.py --check    # 只校验不写盘
"""

import os
import re
import json
import html
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "web")

SITE = {
    "title": "数学如隐喻",
    "subtitle": "Mathematics as Metaphor",
    "tagline": "数学是自然语言的一种专门的方言，因此是一种隐喻。",
    "base": "",
    "repo": "https://github.com/skyboyhjj/math-as-metaphor",
}

# 期次元数据：标题从源文件读，这里只放本站特有的信息
ISSUES = [
    {"no": 1, "src": "issues/01-manin-says-metaphor.md", "out": "issues/01.html",
     "question": "为什么表示必有损",
     "appendix": None, "script": "scripts/verify_arrow_g4.py"},
    {"no": 2, "src": "issues/02-arrow-impossibility.md", "out": "issues/02.html",
     "question": "公理是选的，结论是被逼出来的",
     "appendix": None, "script": None},
    {"no": 3, "src": "issues/03-object-as-relations.md", "out": "issues/03.html",
     "question": "对象由关系决定，那还剩下什么自由",
     "appendix": ("appendices/03-yoneda-proof.md", "appendices/03.html"),
     "script": "scripts/verify_yoneda.py"},
    {"no": 4, "src": "issues/04-category-as-language.md", "out": "issues/04.html",
     "question": "一门语言如何自给自足",
     "appendix": ("appendices/04-category-verification.md", "appendices/04.html"),
     "script": "scripts/verify_category.py"},
]

PLANNED = [
    {"no": 5, "title": "一个符号承担两件事：转译损耗的五种形态", "question": "翻译必有损，损在哪"},
    {"no": 6, "title": "数学的本质恰恰在于其自由", "question": "那自由到底剩多少"},
]

# ---------------------------------------------------------------------------
# 行内
# ---------------------------------------------------------------------------

PLACEHOLDER = "\x00{}\x00"


def _stash(store, value):
    store.append(value)
    return PLACEHOLDER.format(len(store) - 1)


def _restore(text, store):
    def sub(m):
        return store[int(m.group(1))]
    return re.sub(r"\x00(\d+)\x00", sub, text)


def inline(text):
    """行内转换。顺序要紧：先捞出公式与行内代码，再做粗体和链接。"""
    store = []

    # 1. $`...`$  →  $...$   （剥掉反引号，留给 MathJax）
    def math_sub(m):
        body = m.group(1)
        return _stash(store, '<span class="math">$' + body + '$</span>')

    text = re.sub(r"\$`([^`]+)`\$", math_sub, text)

    # 2. 行内代码 `...` → <code>
    text = re.sub(
        r"(?<!\$)`([^`]+)`(?!\$)",
        lambda m: _stash(store, "<code>" + html.escape(m.group(1)) + "</code>"),
        text,
    )

    # 3. 转义 + 粗体
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)

    # 4. 链接 [text](url)，按目标类型改写
    def link_sub(m):
        label, url = m.group(1), m.group(2)
        if url.startswith(("http://", "https://", "#")):
            return f'<a href="{url}">{label}</a>'
        # 脚本不在站点里，指回 GitHub
        sm = re.search(r"(?:\.\./)?scripts/(.+)$", url)
        if sm:
            gh = f"{SITE['repo']}/blob/main/scripts/{sm.group(1)}"
            return f'<a href="{gh}">{label}</a>'
        # 附录与正文：绝对路径，去掉序号后缀
        url = re.sub(r"\.md$", ".html", url)
        url = re.sub(r"/[0-9]{2}-[a-z0-9-]+\.html$", lambda mm: "/" + mm.group(0).split("/")[-1][:2] + ".html", url)
        url = re.sub(r"^(?:\.\./)?", "/", url)
        return f'<a href="{url}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_sub, text)

    return _restore(text, store)


# ---------------------------------------------------------------------------
# 块级
# ---------------------------------------------------------------------------

def split_header(lines):
    """取出首个 h1 与紧随其后的元信息引用块。"""
    title = None
    meta = []
    body = list(lines)

    for i, line in enumerate(body):
        if re.match(r"^#\s+\S", line):
            title = line.lstrip("# ").strip()
            body = body[i + 1:]
            break

    # 跳过空行，收集连续的 > 行；遇到「版本记录」即停（那是给作者看的历史，不上站）
    j = 0
    while j < len(body) and not body[j].strip():
        j += 1
    while j < len(body) and body[j].startswith(">"):
        text = body[j].lstrip("> ").strip()
        if "版本记录" in text:
            break
        if text:
            meta.append(text)
        j += 1

    if meta:
        # 引用块剩余部分（版本记录等）不是正文，整段跳过
        while j < len(body) and (body[j].startswith(">") or not body[j].strip()):
            j += 1
        body = body[j:]

    return title, meta, body


def render_blocks(lines):
    # 剥掉开头的空行与第一条分隔线：元信息行下面已经有分隔，不必叠两条
    k = 0
    while k < len(lines) and not lines[k].strip():
        k += 1
    if k < len(lines) and re.match(r"^-{3,}$", lines[k].strip()):
        k += 1
    lines = lines[k:]

    # 标题层级归一化：有的期用 ##，有的期用 ###，统一映射到 h2
    levels = [len(mm.group(1)) for mm in re.finditer(r"^(#{2,6})\s+", "\n".join(lines), re.M)]
    base = min(levels) if levels else 2

    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        s = line.strip()

        if not s:
            i += 1
            continue

        # 分隔线
        if re.match(r"^-{3,}$", s) or re.match(r"^\*{3,}$", s):
            out.append('<hr class="section-rule">')
            i += 1
            continue

        # 围栏代码块
        if s.startswith("```"):
            lang = s[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            code = html.escape("\n".join(buf))
            cls = f' class="language-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>{code}</code></pre>")
            continue

        # 引用块
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            inner = "".join(f"<p>{inline(x)}</p>" for x in buf if x)
            out.append(f"<blockquote>{inner}</blockquote>")
            continue

        # 表格
        if s.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            header = [c.strip() for c in s.strip("|").split("|")]
            aligns = []
            for c in lines[i + 1].strip().strip("|").split("|"):
                c = c.strip()
                if c.startswith(":") and c.endswith(":"):
                    aligns.append("center")
                elif c.endswith(":"):
                    aligns.append("right")
                else:
                    aligns.append("left")
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1

            th = "".join(f'<th style="text-align:{aligns[k] if k < len(aligns) else "left"}">{inline(c)}</th>'
                         for k, c in enumerate(header))
            trs = []
            for r in rows:
                tds = "".join(
                    f'<td style="text-align:{aligns[k] if k < len(aligns) else "left"}">{inline(c)}</td>'
                    for k, c in enumerate(r))
                trs.append(f"<tr>{tds}</tr>")
            out.append('<div class="table-wrap"><table>'
                       f"<thead><tr>{th}</tr></thead><tbody>{''.join(trs)}</tbody>"
                       "</table></div>")
            continue

        # 有序列表
        if re.match(r"^\d+\.\s", s):
            buf = []
            while i < n and re.match(r"^\d+\.\s", lines[i].strip()):
                buf.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            items = "".join(f"<li>{inline(x)}</li>" for x in buf)
            out.append(f"<ol>{items}</ol>")
            continue

        # 无序列表
        if re.match(r"^[-*]\s", s):
            buf = []
            while i < n and re.match(r"^[-*]\s", lines[i].strip()):
                buf.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            items = "".join(f"<li>{inline(x)}</li>" for x in buf)
            out.append(f"<ul>{items}</ul>")
            continue

        # 标题
        m = re.match(r"^(#{1,6})\s+(.+)$", s)
        if m:
            level = len(m.group(1))
            if level == 1:
                level = 2          # 正文里再出现的 h1 一律降为 h2
            else:
                level = level - base + 2
            level = max(2, min(level, 4))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # 段落
        buf = []
        while i < n:
            s2 = lines[i].strip()
            if not s2 or s2.startswith((">", "|", "```", "#")) or re.match(r"^-{3,}$", s2) \
               or re.match(r"^[-*]\s", s2) or re.match(r"^\d+\.\s", s2):
                break
            buf.append(s2)
            i += 1
        if buf:
            out.append(f"<p>{inline(''.join(buf) if len(buf) == 1 else ''.join(buf))}</p>")

    return "\n".join(out)


# ---------------------------------------------------------------------------
# 页面外壳
# ---------------------------------------------------------------------------

def page(title, body, *, nav="", extra_head="", desc=""):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} · {SITE['title']}</title>
<meta name="description" content="{html.escape(desc or SITE['tagline'])}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:site_name" content="{SITE['title']}">
<meta property="og:description" content="{html.escape(desc or SITE['tagline'])}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css">
{extra_head}
</head>
<body>
<div class="paper">
{nav}
<main>
{body}
</main>
<footer class="site-footer">
  <p><strong>数学如隐喻</strong> · Mathematics as Metaphor</p>
  <p>源稿与算据：<a href="{SITE['repo']}">github.com/skyboyhjj/math-as-metaphor</a></p>
  <p class="license">正文与附录采用 <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh">CC BY-NC-SA 4.0</a>，脚本采用 MIT。</p>
</footer>
</div>
<script>
window.MathJax = {{
  tex: {{
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
  }},
  options: {{ skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'] }}
}};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</body>
</html>
"""


def top_nav(current_no=None):
    links = ['<a href="/">目录</a>']
    for it in ISSUES:
        cls = ' class="on"' if current_no == it["no"] else ""
        links.append(f'<a href="/{it["out"]}"{cls}>第 {it["no"]} 期</a>')
    return '<nav class="top-nav">' + "".join(links) + "</nav>"


def pager(no):
    parts = []
    prev = next((x for x in ISSUES if x["no"] == no - 1), None)
    nxt = next((x for x in ISSUES if x["no"] == no + 1), None)
    if prev:
        parts.append(f'<a class="pg prev" href="/{prev["out"]}"><span>上一期</span>第 {prev["no"]} 期</a>')
    if nxt:
        parts.append(f'<a class="pg next" href="/{nxt["out"]}"><span>下一期</span>第 {nxt["no"]} 期</a>')
    if not parts:
        return ""
    return '<div class="pager">' + "".join(parts) + "</div>"


# ---------------------------------------------------------------------------
# 构建
# ---------------------------------------------------------------------------

def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def build_issue(it, search_docs):
    raw = read(it["src"])
    lines = raw.splitlines()
    title, meta, body = split_header(lines)

    meta_html = ""
    if meta:
        items = [inline(x) for x in meta]
        meta_html = '<p class="issue-meta">' + " ｜ ".join(items) + "</p>"

    content = f'<article class="issue">\n<h1>{inline(title)}</h1>\n{meta_html}\n{render_blocks(body)}\n</article>'

    if it["appendix"]:
        content += (f'\n<p class="appendix-link">完整证明与算据：'
                    f'<a href="/{it["appendix"][1]}">附录 · 第 {it["no"]} 期</a></p>')

    content += pager(it["no"])

    search_docs.append({"t": f"第 {it['no']} 期 · {title}", "u": "/" + it["out"],
                        "k": body_text(body)[:220]})
    return title, page(f"第 {it['no']} 期 · {title}", content,
                       nav=top_nav(it["no"]), desc=title)


def build_appendix(it):
    src, out = it["appendix"]
    raw = read(src)
    lines = raw.splitlines()
    title, meta, body = split_header(lines)

    meta_html = ""
    if meta:
        meta_html = '<p class="issue-meta">' + " ｜ ".join(inline(x) for x in meta) + "</p>"

    content = f'<article class="issue appendix">\n<h1>{inline(title or "附录")}</h1>\n{meta_html}\n{render_blocks(body)}\n</article>'
    content += (f'<p class="appendix-link">返回正文：'
                f'<a href="/{it["out"]}">第 {it["no"]} 期</a></p>')
    return page(f"附录 · 第 {it['no']} 期", content, nav=top_nav(it["no"]), desc=title or "")


def body_text(lines):
    t = " ".join(l.strip() for l in lines if l.strip())
    t = re.sub(r"\$`[^`]+`\$", "", t)
    t = re.sub(r"[#>*`|-]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def build_index():
    cards = []
    for it in ISSUES:
        raw = read(it["src"])
        title, meta, body = split_header(raw.splitlines())
        link = f'<a class="card" href="/{it["out"]}">'
        sub = f'<span class="card-sub">{html.escape(it["question"])}</span>'
        ap = (f'<span class="card-ap">附录</span>' if it["appendix"] else "")
        cards.append(
            f'{link}<span class="card-no">{it["no"]:02d}</span>'
            f'<span class="card-body"><strong>{html.escape(title)}</strong>{sub}</span>{ap}</a>'
        )

    for p in PLANNED:
        cards.append(
            f'<div class="card planned"><span class="card-no">{p["no"]:02d}</span>'
            f'<span class="card-body"><strong>{html.escape(p["title"])}</strong>'
            f'<span class="card-sub">{html.escape(p["question"])}</span></span>'
            f'<span class="card-ap">待写</span></div>'
        )

    body = f"""
<header class="hero">
  <h1 class="hero-title">{SITE['title']}</h1>
  <p class="hero-sub">{SITE['subtitle']}</p>
  <p class="hero-quote">「{SITE['tagline']}」</p>
  <p class="hero-note">这个合集沿着这条线读下去：数学如何用一套自造的语言转译世界，转译过程损耗了什么，又有哪些东西因此才能被说出口。</p>
</header>

<section class="card-list">
{chr(10).join(cards)}
</section>

<section class="about">
  <h2>关于这个站</h2>
  <p>每期正文与附录在 <a href="{SITE['repo']}">GitHub 仓库</a>公开，包含可复算的验证脚本——正文里的具体断言，背后都有一段能跑的代码。</p>
  <p>公众号只放结果，推导与算据放在仓库里，文末的「阅读原文」跳转过去。</p>
</section>

<section class="search-box">
  <input id="q" type="search" placeholder="搜索标题与正文关键词" autocomplete="off">
  <div id="results" class="search-results"></div>
</section>
"""
    return page("目录", body, nav=top_nav(), desc=SITE["tagline"],
                extra_head='<script src="/assets/search-data.js"></script>\n'
                           '<script defer src="/assets/search.js"></script>')


STYLE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "templates", "style.css"), encoding="utf-8").read() \
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "templates", "style.css")) else ""

SEARCH_JS = """(function () {
  var docs = window.__SEARCH__ || [];
  var q = document.getElementById('q');
  var box = document.getElementById('results');
  if (!q || !box) return;
  function run() {
    var kw = q.value.trim().toLowerCase();
    box.innerHTML = '';
    if (!kw) return;
    var hits = docs.filter(function (d) {
      return (d.t + ' ' + d.k).toLowerCase().indexOf(kw) >= 0;
    }).slice(0, 20);
    if (!hits.length) { box.innerHTML = '<p class="no-hit">没有匹配的内容</p>'; return; }
    box.innerHTML = hits.map(function (d) {
      return '<a class="hit" href="' + d.u + '"><strong>' + d.t + '</strong><span>' + d.k.slice(0, 80) + '…</span></a>';
    }).join('');
  }
  q.addEventListener('input', run);
})();
"""


def main(argv):
    check_only = "--check" in argv
    os.makedirs(os.path.join(OUT, "issues"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "appendices"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)

    written = []
    search_docs = []

    for it in ISSUES:
        title, html_text = build_issue(it, search_docs)
        written.append((it["out"], html_text, len(title)))

    for it in ISSUES:
        if it["appendix"]:
            written.append((it["appendix"][1], build_appendix(it), 0))

    index_html = build_index()
    written.append(("index.html", index_html, 0))

    if not check_only:
        for rel, content, _ in written:
            p = os.path.join(OUT, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)

        # 样式
        css_path = os.path.join(ROOT, "templates", "style.css")
        if os.path.exists(css_path):
            with open(css_path, encoding="utf-8") as f:
                css = f.read()
            with open(os.path.join(OUT, "assets", "style.css"), "w", encoding="utf-8") as f:
                f.write(css)

        # 搜索索引
        with open(os.path.join(OUT, "assets", "search-data.js"), "w", encoding="utf-8") as f:
            f.write("window.__SEARCH__ = " + json.dumps(search_docs, ensure_ascii=False) + ";\n")

        with open(os.path.join(OUT, "assets", "search.js"), "w", encoding="utf-8") as f:
            f.write(SEARCH_JS)

        # 站标：朱砂圆 + 一道弧与一点（两语相转的意象）
        favicon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<circle cx="32" cy="32" r="30" fill="#8b1e22"/>
<path d="M17 41 Q32 13 47 41" stroke="#faf8f0" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="32" cy="43" r="3.4" fill="#d4c9a8"/>
</svg>
"""
        with open(os.path.join(OUT, "assets", "favicon.svg"), "w", encoding="utf-8") as f:
            f.write(favicon)

    print(f"生成 {len(written)} 个页面:")
    for rel, content, _ in written:
        print(f"  {len(content):>7,}B  {rel}")
    if not check_only:
        print(f"\n输出目录: {os.path.relpath(OUT, ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
