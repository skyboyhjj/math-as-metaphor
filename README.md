# 数学如隐喻 / Mathematics as Metaphor

> 俄罗斯数学家尤里·曼宁（Yuri Manin）说，数学是自然语言的一种专门的方言，因此是一种隐喻。他不认为这是在贬低严格性，反而强调：没有严格的规则持续约束，数学无法发展。只是他也看到另一面，用他自己的话说：「比喻帮助人类在这纯净空气中呼吸。」
>
> 这个合集沿着这条线读下去：数学如何用一套自造的语言转译世界，转译过程损耗了什么，又有哪些东西因此才能被说出口。

本仓库是微信公众号合集【数学如隐喻】的配套资料：每期正文、附录证明、可复算脚本、以及写作过程中核过的原始材料。

在线阅读：**<https://www.huiskill.org/>**

---

## 每期索引

| 期 | 标题 | 核心问题 | 正文 |
| :- | :- | :- | :- |
| 1 | 曼宁说「数学是隐喻」，他说的不是「数学像诗」 | 为什么表示必有损 | [issues/01](issues/01-manin-says-metaphor.md) |
| 2 | 阿罗不可能定理：为什么「公平投票」注定无解 | 公理是选的，结论是被逼出来的 | [issues/02](issues/02-arrow-impossibility.md) |
| 3 | 对象是关系的总和吗：从 Hahn-Banach 到 Yoneda | 对象由关系决定，那还剩下什么自由 | [issues/03](issues/03-object-as-relations.md) · [附录](appendices/03-yoneda-proof.md) |
| 4 | 当数学开始谈论自己：范畴论作为一种语言 | 一门语言如何自给自足 | [issues/04](issues/04-category-as-language.md) · [附录](appendices/04-category-verification.md) |
| 5 | 一个符号承担两件事：转译损耗的五种形态 | 翻译必有损，损在哪 | 待写 |
| 6 | 数学的本质恰恰在于其自由 | 那自由到底剩多少 | 待写 |

规划见 [notes/roadmap-freedom-as-thread.md](notes/roadmap-freedom-as-thread.md)。

---

## 三条原则

这套文字不打算只讲「数学很美」。它守三条：

**一、先算后说。** 能用数字裁决的，绝不靠直觉。每一期正文里的具体断言，背后都有一个可跑的脚本，放在 [`scripts/`](scripts/)。

**二、格式同型不等于等价。** 两处长得像，不等于同一件事。写类比必须同时标出边界——第 3 期专门用一节划清 Hahn-Banach 与 Yoneda 的强弱差别，就是为了不让「对象由关系决定」这句话被顺口说大。

**三、诚实边界是战斗力。** 指出自己上一步的错，比维护结论重要。第 3 期第四节写的就是一次自我纠正：曾经把一个不可表函子说成「不属于任何对象的关系」，后来算清楚了——它是两个可表函子的余积。

---

## 怎么跑这些脚本

全部纯标准库，不需要安装任何依赖。Python 3.9 以上即可。

```bash
python3 scripts/verify_yoneda.py      # Yoneda 引理的枚举验证（五组）
python3 scripts/verify_category.py    # 范畴论四组：等价≠同构、Cat 非小范畴等
python3 scripts/verify_arrow_g4.py    # 阿罗定理：穷举聚合规则，看独裁是否唯一幸存
python3 scripts/check_github_math.py  # 发布前检查：公式里有没有 GitHub 不认的宏
python3 scripts/make_site.py          # 由 issues/ 与 appendices/ 生成网站到 web/
```

每个脚本都会打印分组标题、验算过程与结论，不需要额外参数。`make_site.py` 除外，它产出文件。

### 关于 `make_site.py`

站点不是手写的，是从 Markdown 生成的。改完正文跑一遍：

```bash
python3 scripts/make_site.py          # 生成到 web/
python3 scripts/make_site.py --check  # 只统计不写盘
```

它做四件事：把 `issues/` 与 `appendices/` 渲染成带语义标签的 HTML；把公式从 `` $x$ `` 还原成 `$x$` 交给 MathJax；把 `.md` 链接改写成站内 `.html`；顺手生成首页索引与搜索数据。

站点样式在 `templates/style.css`，配色沿用公众号的朱砂（`#8b1e22`）与宣纸（`#faf8f0`）。

### 关于 `check_github_math.py`

GitHub 渲染 Markdown 里的 LaTeX 时，只用 MathJax 核心宏的一个子集。用了白名单外的宏，页面会显示红色报错：

```
The following macros are not allowed: operatorname
```

这个报错只对读者可见，本地编辑器里看不出来。所以每期写完、提交之前跑一遍：

```bash
python3 scripts/check_github_math.py              # 扫全仓，报出文件名 + 行号 + 建议改法
python3 scripts/check_github_math.py --all-macros # 附带列出用到的每个宏及次数
python3 scripts/check_github_math.py --self-test  # 验证脚本自身有效（内置夹具）
```

退出码 0 表示干净，1 表示有隐患。

它拦的是这一类：`\operatorname` `\bm` `\color` `\bbox` `\def` `\newcommand` `\tag` `\label` `\require` `\ce` 等——宏定义、样式注入、公式编号、扩展包加载，GitHub 一律拒绝。围栏代码块会被整段跳过，不会把 Python 的 `\n` 当成宏。

本仓库当前状态：11 个 Markdown、251 个公式片段，全部通过。

---

## 目录

```
issues/       每期正文（Markdown，唯一真源）
appendices/   附录：证明拆解与算据汇编
scripts/      算据脚本与站点生成脚本（纯标准库）
templates/    站点样式表
drafts/       公众号中间稿（AI 加工后、发布前）
dist/wechat/  公众号粘贴用 HTML
web/          网站（由 make_site.py 生成，不手改）
notes/        规划与方法笔记
sources/      核过的原始材料（如曼宁 1990 讲稿英文全本）
archive/      未采用的备选稿
```

### 关于 `web/`

`web/` 是**生成物**，不是手写页。里面是语义化的 HTML（`h1`/`h2`/`p`/`table`）、一份全站 CSS、首页索引与搜索数据。公式保留 LaTeX 原样，由页面加载的 MathJax CDN 渲染。

由 Cloudflare Pages 直接托管，`Build command` 留空、输出目录填 `web`。HTML 在本地生成好再 push，线上不依赖 Python 环境。

要改页面外观，改 `templates/style.css` 后重跑 `make_site.py`，不要直接编辑 `web/` 里的文件。

### 关于 `dist/wechat/`

公众号编辑器不支持 LaTeX，也不接受外部样式表——公式必须转成 Unicode，样式必须全部内联。`dist/wechat/` 里是转换后的粘贴版：浏览器打开 → 全选 → 复制 → 粘贴进编辑器。

它与 `web/` 是两套产物，不能互换：微信会剥离 `<style>`、忽略 class 选择器、移除 `<script>`，所以站点那套语义化 HTML 贴过去会散架。

### 关于 `sources/`

`sources/manin-1990-en.txt` 是曼宁 1990 年京都 ICM 讲稿《Mathematics as Metaphor》的英文全文，取自网络转载，正文中保留了 `Mathematics as Metaphor 1667/1669/1671` 三处页码标记，可据此核对原始出处（Proc. Int. Congr. Math. Kyoto 1990, Vol. II, pp. 1665–1671）。

**注意**：该讲稿由 Barry Mazur 代读（Proceedings 页脚 `Delivered by Barry Mazur`），曼宁本人未到场。

---

## 三个地方，各管一件事

| 位置 | 适合做的事 |
| :- | :- |
| 公众号 | 读。轻、顺、不打断，手机上能一口气看完。 |
| 网站 `huiskill.org` | 查与回看。目录清楚，公式可缩放，上下篇串得起来。 |
| 这个仓库 | 验。源码、脚本、原始材料，能自己跑一遍。 |

公众号只放「结果」：每期的正文与结论。推导、证明、可复算的代码放在仓库里，通过文末的「阅读原文」跳转过来。

这样分工的理由很简单：**公众号适合读，GitHub 适合查**。同一个结论，读者信不信，取决于能不能自己算一遍——那部分不该被排版吃掉。

站点由仓库里的 Markdown 生成，所以三处内容始终同源：改 `issues/` 里的源稿，跑一次 `make_site.py`，网站跟着变；公众号那边重走一次转换。

---

## 授权

- 正文与附录（Markdown / HTML）：[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh)
- 脚本（`scripts/` 下的 Python）：[MIT](LICENSE)

转载正文请注明出处与本仓库链接。
