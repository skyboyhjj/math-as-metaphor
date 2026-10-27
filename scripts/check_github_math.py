#!/usr/bin/env python3
"""check_github_math.py — GitHub MathJax 宏白名单预检

GitHub 渲染 Markdown 里的 LaTeX 时，只用 MathJax 核心宏的一个子集。
用了白名单外的宏，页面会出现红色报错：

    The following macros are not allowed: operatorname

本脚本把这个问题的发现时间从「发布后被读者撞见」提前到「提交前」。

用法
----
    python3 scripts/check_github_math.py                # 扫仓库里所有 .md
    python3 scripts/check_github_math.py issues         # 只扫指定目录
    python3 scripts/check_github_math.py issues/03-object-as-relations.md
    python3 scripts/check_github_math.py --all-macros   # 附带列出用到的每个宏及次数
    python3 scripts/check_github_math.py --self-test    # 跑内置夹具，验证脚本自身有效

退出码
------
    0  干净
    1  发现白名单外的宏
    2  用法错误 / 未找到文件

依赖
----
    仅标准库。不需要装 MathJax，也不需要联网。
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# 禁用表：GitHub MathJax 不给用的宏 → 建议替代写法
#
# 分组只为输出好看。判定依据是 GitHub 的 MathJax safe 配置（宏 allowlist），
# 该配置拒绝定义类、样式/HTML 注入类、引用类、以及部分 amsmath 之外的扩展宏。
# ---------------------------------------------------------------------------

BANNED = {
    "自称运算符": {
        "operatorname": r"\mathrm{...}",
        "DeclareMathOperator": "（宏定义，GitHub 直接拒绝）改用 \\mathrm",
        "mathop": "改用 \\mathrm{...}",
    },
    "粗体向量": {
        "bm": r"\boldsymbol{...}",
        "pmb": r"\boldsymbol{...}",
    },
    "样式与 HTML 注入": {
        "color": "GitHub 不支持上色，删掉",
        "textcolor": "GitHub 不支持上色，删掉",
        "colorbox": "GitHub 不支持上色，删掉",
        "fcolorbox": "GitHub 不支持上色，删掉",
        "definecolor": "GitHub 不支持上色，删掉",
        "style": "删掉",
        "class": "删掉",
        "cssId": "删掉",
        "htmlId": "删掉",
        "htmlClass": "删掉",
        "htmlStyle": "删掉",
        "htmlData": "删掉",
        "bbox": "删掉（该宏用于给公式加框）",
        "unicode": "改用对应字符或 \\text{}",
        "mmlToken": "删掉",
        "char": "改用对应字符",
    },
    "宏定义与包加载": {
        "def": "GitHub 拒绝一切宏定义，把宏张开写",
        "gdef": "GitHub 拒绝一切宏定义，把宏张开写",
        "edef": "GitHub 拒绝一切宏定义，把宏张开写",
        "xdef": "GitHub 拒绝一切宏定义，把宏张开写",
        "let": "GitHub 拒绝一切宏定义，把宏张开写",
        "newcommand": "GitHub 拒绝一切宏定义，把宏张开写",
        "renewcommand": "GitHub 拒绝一切宏定义，把宏张开写",
        "providecommand": "GitHub 拒绝一切宏定义，把宏张开写",
        "require": "GitHub 不允许加载扩展包",
        "usepackage": "GitHub 不允许加载扩展包",
    },
    "交叉引用与编号": {
        "label": "GitHub 不支持公式编号，删掉",
        "ref": "GitHub 不支持公式编号，删掉",
        "eqref": "GitHub 不支持公式编号，删掉",
        "tag": "删掉；需要编号就写成 \\qquad(1)",
        "nonumber": "删掉",
        "notag": "删掉",
    },
    "删除线与圈注": {
        "cancel": r"\not 或改写",
        "bcancel": r"\not 或改写",
        "xcancel": r"\not 或改写",
        "sout": "删掉",
        "enclose": "删掉",
    },
    "化学与其他扩展": {
        "ce": "mhchem 未加载，改用普通公式写",
        "pu": "mhchem 未加载，改用普通公式写",
        "includegraphics": "GitHub 不支持插图进公式，改用图片链接",
        "verb": "删掉",
    },
}

# 反查：宏名 → (分组, 建议)
SUGGEST = {}
for _group, _items in BANNED.items():
    for _macro, _advice in _items.items():
        SUGGEST[_macro] = (_group, _advice)

# 统计用：任何反斜杠 + 字母序列，都算一个「宏」
MACRO_RE = re.compile(r"\\([A-Za-z]+)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def mask_non_math(text):
    """把非数学区域整段替换为等长空白（保留换行，行号不漂移）。

    要遮两类：
    1. 围栏代码块（``` / ~~~）——里面的 \\n \\t 是 Python 转义，不是 LaTeX。
    2. 行内代码（单反引号）——散文里提到某个宏名时，常写成 `\\operatorname`
       这样的代码片段，那是「在讲这个宏」，不是「在用这个宏」。

    但本仓库的公式恰好写作 `$公式$`（反引号被美元符夹住），必须保住。
    所以遮行内代码时用前后断言排除 `$...$` 包住的那种。
    """
    out = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append(re.sub(r"[^\n]", " ", line))
        elif in_fence:
            out.append(re.sub(r"[^\n]", " ", line))
        else:
            out.append(line)
    masked = "".join(out)
    # 行内代码：前后都不被 $ 夹住的才算代码（保住 $`...`$ 这种公式写法）
    masked = re.sub(
        r"(?<!\$)`[^`\n]*`(?!\$)",
        lambda m: re.sub(r"[^\n]", " ", m.group(0)),
        masked,
    )
    return masked


def scan_text(text):
    """返回 [(行号, 宏名, 分组, 建议)]，只含有问题的。"""
    masked = mask_non_math(text)
    hits = []
    for lineno, line in enumerate(masked.splitlines(), start=1):
        for m in MACRO_RE.finditer(line):
            macro = m.group(1)
            if macro in SUGGEST:
                group, advice = SUGGEST[macro]
                hits.append((lineno, macro, group, advice))
    return hits


def collect_macros(text):
    """统计文中出现的每个宏及次数（--all-macros 用）。"""
    masked = mask_non_math(text)
    counts = {}
    for m in MACRO_RE.finditer(masked):
        counts[m.group(1)] = counts.get(m.group(1), 0) + 1
    return counts


def iter_md_files(targets):
    for t in targets:
        if os.path.isfile(t):
            yield t
        else:
            for dp, dn, fn in os.walk(t):
                dn[:] = [d for d in dn if d not in (".git", "__pycache__", "node_modules")]
                for f in sorted(fn):
                    if f.lower().endswith(".md"):
                        yield os.path.join(dp, f)


def run(targets, show_all=False):
    files = sorted(iter_md_files(targets))
    if not files:
        print("没有找到任何 .md 文件。", file=sys.stderr)
        return 2

    total_hits = 0
    total_formulas = 0
    all_counts = {}

    for path in files:
        try:
            text = open(path, encoding="utf-8").read()
        except UnicodeDecodeError as e:
            print(f"  ✗ {path}  不是合法 UTF-8（{e}）")
            total_hits += 1
            continue

        total_formulas += len(re.findall(r"\$`[^`]+`\$|\$\$", text))
        hits = scan_text(text)
        if show_all:
            for k, v in collect_macros(text).items():
                all_counts[k] = all_counts.get(k, 0) + v

        if hits:
            print(f"\n✗ {path}")
            for lineno, macro, group, advice in hits:
                print(f"    第 {lineno} 行  \\{macro}   [{group}]")
                print(f"              建议：{advice}")
            total_hits += len(hits)

    print(f"\n扫描 {len(files)} 个 Markdown 文件，公式片段 {total_formulas} 个")

    if show_all and all_counts:
        print("\n用到的全部宏（按次数降序）：")
        for macro, n in sorted(all_counts.items(), key=lambda x: (-x[1], x[0])):
            flag = "  ✗ 白名单外" if macro in SUGGEST else ""
            print(f"  {n:>4}  \\{macro}{flag}")

    if total_hits == 0:
        print("✓ 没有发现 GitHub MathJax 白名单外的宏")
        return 0

    print(f"\n合计 {total_hits} 处隐患，修完再提交。")
    return 1


SELF_TEST_FIXTURE = r"""
正常公式，不应报错：

$`F \;\cong\; \mathrm{colim}\big(h^A \to F\big)`$

$`\int_0^1 f(x)\,dx \le \lVert f \rVert_\infty`$

$`A \xrightarrow{\sim} B \qquad \text{对一切 } n`$

以下三处必须被抓到：

$`F \cong \operatorname{colim} h^A`$

$$
\tag{1} x = y
$$

$`\bm{v} + \mathbf{w}`$

围栏代码块里的不算（应被遮罩）：

```python
print("\n\t\\alpha")
```

行内代码里提到宏名，是在讲解、不是在用（应被遮罩，这是本脚本的回归用例）：

散文里可以说 `\operatorname` 不能用，也可以说 `\tag` 不能用。

真正的公式仍然要查：

$`\operatorname{colim}`$
"""


def self_test():
    hits = scan_text(SELF_TEST_FIXTURE)
    found = [h[1] for h in hits]
    expect = {"operatorname": 2, "tag": 1, "bm": 1}
    got = {}
    for m in found:
        got[m] = got.get(m, 0) + 1

    print("自检夹具：")
    for _, macro, group, _ in hits:
        print(f"    抓 到  \\{macro}   [{group}]")

    ok = got == expect
    if ok:
        print("✓ 自检通过：3 处该抓的都抓到，代码块与行内代码零误报")
        return 0

    print(f"✗ 自检失败：期望 {expect}，实得 {got}")
    return 1


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}

    if "--help" in flags or "-h" in flags:
        print(__doc__)
        return 0
    if "--self-test" in flags:
        return self_test()
    if flags - {"--all-macros"}:
        print(f"未知参数：{sorted(flags - {'--all-macros'})}", file=sys.stderr)
        print("试 python3 scripts/check_github_math.py --help", file=sys.stderr)
        return 2

    if not args:
        here = os.path.dirname(os.path.abspath(__file__))
        args = [os.path.dirname(here)]

    return run(args, show_all="--all-macros" in flags)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
