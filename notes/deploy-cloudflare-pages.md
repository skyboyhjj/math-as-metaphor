# 部署：把 web/ 发到 huiskill.org

> 版本 v1.0 ｜ 2026-10-27
> 目标：`main` 分支的 `web/` 目录，由 Cloudflare Pages 托管到 `www.huiskill.org`

---

## 一、当前状态

| 项 | 状态 |
| :- | :- |
| GitHub 仓库 | `skyboyhjj/math-as-metaphor`，18 个文件已上线 |
| 站点源码 | `web/` 已生成 7 个页面 + 3 个资源文件 |
| 域名 `huiskill.org` | 已托管在 Cloudflare |
| 域名解析 | **`www.huiskill.org` 当前解析失败**，需要补记录 |

最后一项要在绑 Pages 时一并处理，见第四节。

---

## 二、站点是什么样的

```
web/
  index.html              目录页：六期卡片 + 关于 + 搜索
  issues/01.html          第 1 期
  issues/02.html          第 2 期
  issues/03.html          第 3 期
  issues/04.html          第 4 期
  appendices/03.html      第 3 期附录
  appendices/04.html      第 4 期附录
  assets/style.css        全站样式，一份
  assets/favicon.svg      站标
  assets/search-data.js   搜索索引（2.8 KB）
  assets/search.js        搜索逻辑（700 B）
```

纯静态。没有构建步骤，没有 Node 依赖，没有服务端。公式用 MathJax CDN，搜索是前端过滤。

---

## 三、Cloudflare Pages 接入

### 3.1 创建项目

1. 登录 Cloudflare Dashboard，左侧选 **Workers & Pages**
2. **Create** → **Pages** → **Connect to Git**
3. 授权 GitHub，选仓库 `skyboyhjj/math-as-metaphor`
4. 配置如下：

| 配置项 | 填什么 |
| :- | :- |
| Project name | `math-as-metaphor` |
| Production branch | `main` |
| Framework preset | **None** |
| Build command | **留空** |
| Build output directory | `web` |
| Root directory | 留空 |

5. **Save and Deploy**

构建命令留空是有意的：HTML 在本地由 `make_site.py` 生成、随 commit 一起推上来，Cloudflare 只做静态托管。这样线上不依赖 Python 环境，也不会因为平台构建镜像升级而突然失败。

### 3.2 首次部署后的地址

`https://math-as-metaphor.pages.dev`

先在这个地址验证，再绑自有域名。

### 3.3 部署记录

每次 push 到 `main` 自动触发。Cloudflare 会保留每次部署的独立预览地址，回滚只需在 Deployments 里点旧版本的 **Rollback**。

---

## 四、绑定 huiskill.org（含 DNS 修正）

### 4.1 为什么现在解析失败

`www.huiskill.org` 返回 `Could not resolve host`，说明 DNS 里没有对应记录。三种可能：

1. 域名还没添加到这个 Cloudflare 账号
2. 已添加但没有 `www` 的 CNAME 记录
3. 域名注册商的 Nameserver 还没切到 Cloudflare

先确认第 3 项：在 Cloudflare 的 **Websites** 列表里能看到 `huiskill.org` 且状态为 **Active**，就说明 Nameserver 已生效。若是 **Pending Nameserver Update**，要等注册商那边生效（通常几分钟到 24 小时）。

### 4.2 在 Pages 里加自定义域名

1. 打开 Pages 项目 → **Custom domains** → **Set up a custom domain**
2. 先加 `www.huiskill.org`，按提示确认
3. 再加 `huiskill.org`（根域）

因为域名就在同一个 Cloudflare 账号下，Pages 会自动创建所需 DNS 记录，不必手填。

### 4.3 若需要手动补记录

在 **DNS** → **Records** 里：

| Type | Name | Content | Proxy |
| :- | :- | :- | :- |
| CNAME | `www` | `math-as-metaphor.pages.dev` | Proxied |
| CNAME | `@` | `math-as-metaphor.pages.dev` | Proxied |

根域的 CNAME 由 Cloudflare 的 CNAME flattening 自动处理，不需要 A 记录。

### 4.4 跳转规则

建议让根域跳 `www`，或反之，只留一个主域。在 **Rules** → **Redirect Rules** 里加一条：

- 请求 `huiskill.org/*`
- 目标 `https://www.huiskill.org/$1`
- 状态码 301

这样搜索引擎不会把两个地址当成两份内容。

### 4.5 HTTPS

绑完域名后 Cloudflare 自动签发证书，通常几分钟内生效。`SSL/TLS` 模式设为 **Full** 即可（Pages 本身已支持 HTTPS）。

---

## 五、日常流程

### 改了正文

```bash
python3 scripts/make_site.py          # 重新生成 web/
python3 scripts/check_github_math.py  # 公式宏合规
git add -A && git commit -m "site: 第 5 期上线"
git push
```

push 后 Cloudflare 自动部署，约 30 秒生效。

### 只改样式

改 `templates/style.css`，重跑 `make_site.py`，push。样式表会被复制到 `web/assets/style.css`，HTML 不用动。

### 加了新一期

1. 写 `issues/05-xxx.md`
2. 在 `scripts/make_site.py` 顶部的 `ISSUES` 列表里加一条（含 `question` 与 `appendix`）
3. 从 `PLANNED` 里删掉对应的占位项
4. 重跑脚本，push

首页卡片、上一篇下一篇、导航栏都会自动接上，不需要手改任何 HTML。

---

## 六、本地预览

```bash
cd web && python3 -m http.server 8000
```

浏览器打开 `http://localhost:8000`。用 `file://` 直接双击打开会看不到样式，因为页面里用的是 `/assets/` 绝对路径。

---

## 七、检查清单

上线前跑一遍：

- [ ] `python3 scripts/make_site.py` 无报错，7 个页面全部生成
- [ ] `python3 scripts/check_github_math.py` 退出码 0
- [ ] 本地 `http.server` 打开首页，六张卡片能点
- [ ] 任意一期正文，公式正常渲染（不是 `$...$` 原文）
- [ ] 附录页底部的「返回正文」能跳回
- [ ] 首页搜索框输入「Yoneda」，能搜到第 3 期
- [ ] 手机宽度（375px）下无横向滚动条
