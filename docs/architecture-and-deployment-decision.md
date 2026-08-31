# ADR-001：课程网站架构与公网发布方案

- 状态：架构与 GitHub Pages 公网部署均已实施
- 日期：2026-08-30
- 背景：课程需要手机端自动适配、公式/图例/测试清晰、频繁迭代，并允许非局域网访问。

## 1. 架构选择

### 结论

使用 **Astro 静态站点生成（SSG）+ TypeScript + Content Collections/MDX + KaTeX**。

首期不建设传统后端：

- 课程正文、公式和 SVG 在构建期生成静态 HTML。
- 测试题作为按需加载的客户端 island。
- Three.js 图例仅在进入可视区域时加载。
- 学习进度先保存在 `localStorage`。
- 需要账号和跨设备同步时，再增加 EdgeOne Functions + KV，不提前引入服务端复杂度。

### 选择理由

1. Astro Content Collections 适合结构化管理课程 Markdown/MDX，可用 schema 校验标题、章节、时长、标签和测试信息，并生成 TypeScript 类型。
2. Astro 默认输出静态 HTML，只给测试和 3D 图等交互组件发送 JavaScript；比当前所有内容打入一个 Vite 客户端包更适合长课程和手机网络。
3. 可继续复用现有 Markdown、KaTeX、SVG、CSS 和测试数据，迁移成本可控。
4. 支持按课程生成稳定 URL、SEO 元信息、站点地图及后续 PWA。
5. Astro 有 EdgeOne 官方部署支持，也可无锁定地部署到 GitHub Pages、Cloudflare Pages、Vercel 等静态平台。

### 不选择的方案

- Next.js：当前没有必须的服务端渲染和复杂业务后台，运行模型偏重。
- Docusaurus/VitePress：文档能力强，但定制课程交互、视觉和 Three.js 时约束更多。
- 继续使用纯 Vite SPA：短期可用，但课程增长后缺少内容 schema、按页静态生成和默认的最小 JavaScript 输出。

## 2. 手机适配标准

框架本身不会自动保证适配，实施时采用移动优先：

- 基准宽度：360、390、430、768、1024、1440 px。
- 正文、公式、表格和 SVG 不允许造成页面横向滚动；长公式仅在自己的容器内滚动。
- 触控目标至少约 44×44 px。
- 手机端目录改为抽屉或折叠面板。
- SVG 使用 `viewBox`，位图使用 Astro 响应式图片。
- Three.js 提供静态图降级，并限制手机像素比与资源大小。
- 每课发布前完成 390 px 与 1440 px 截图、真实手机和 Lighthouse 检查。

## 3. 公网发布选择

### 零成本起步：GitHub Pages（当前采用）

GitHub Pages 作为当前公开课程的零成本发布入口：

- GitHub Free 的公开仓库可免费使用 Pages。
- 默认提供公开 `github.io` 地址，无需处于同一局域网，也不必先购买域名。
- Git push 后由 GitHub Actions 自动构建 Astro 并发布。
- 官方限制包含站点 1 GB、软带宽 100 GB/月、软构建限制 10 次/小时；对当前课程迭代足够。
- 公开仓库的标准 GitHub Actions runner 免费。

局限：没有 EdgeOne/Cloudflare 那样完善的每分支预览；中国大陆不同运营商访问速度和稳定性没有平台承诺，发布后必须用移动/联通/电信实际测试。

### 面向国内学习者的长期方案：EdgeOne Makers + 自定义域名

若 GitHub Pages 在手机网络测试不稳定，则从同一 Git 仓库部署到腾讯 EdgeOne Makers：

- 当前免费版：500 次构建/月、1 个并发构建、单次 20 分钟、40 个项目、免费 SSL、自定义域名和 1 GB KV。
- 支持 Git 主分支推送自动部署，也支持部署钩子。
- 可在后续用 Functions/KV 实现跨设备学习进度。

重要限制：官方文档说明，在中国大陆网络环境直接使用平台项目/部署域名时需要 3 小时有效的预览链接。长期稳定访问应绑定自定义域名：

- 使用中国大陆节点或含中国大陆的全球节点：域名必须完成 ICP 备案。
- 全球（不含中国大陆）区域：自定义域名无需 ICP，但没有中国大陆节点加速。
- 因此“大陆长期稳定 + 完全零成本 + 无域名/无备案”无法承诺同时成立。

### 备用平台：Cloudflare Pages

Cloudflare Pages 免费版同样提供 500 次构建/月、1 个并发、20 分钟构建超时、无限预览部署、100 个自定义域名。适合作为海外访问或临时镜像，但 `pages.dev` 在中国大陆的实际可达性需要真实网络测试，因此不作为唯一国内入口。

## 4. 推荐发布流程

1. 本地分支开发并运行检查，不为每个微小保存触发公网构建。
2. 功能完成后提交公开 GitHub 仓库；合并 `main` 后由 Actions 自动发布 Pages。
3. 从默认 Pages 地址进行手机 4G/5G 测试。
4. 域名准备完成后绑定自定义域名；如需国内节点，再评估 EdgeOne Makers 与备案。
5. 记录中国移动、联通、电信至少两个网络的首屏时间和可达性。
6. Cloudflare Pages 保留为全球区域备用镜像。

## 5. 已实施结构

旧版 Vite 原型保留在 `web/`；Astro 主站位于：

```text
site/
├─ astro.config.mjs
├─ src/
│  ├─ content.config.ts
│  ├─ content/courses/*.mdx
│  ├─ components/
│  │  ├─ CourseCard.astro
│  │  ├─ CourseNav.astro
│  │  └─ Quiz.astro
│  ├─ data/quizzes.ts
│  ├─ layouts/BaseLayout.astro
│  ├─ pages/
│  ├─ styles/global.css
│  └─ utils/url.ts
└─ public/
   ├─ assets/
   └─ videos/

videos/
├─ requirements.txt
├─ manim_style.py
└─ <topic>/
   ├─ storyboard.md
   └─ *.py

rotation-lib/
├─ src/embodied_spatial/
│  ├─ numpy.py / torch.py
│  └─ se3_numpy.py / se3_torch.py
├─ tests/
├─ examples/
└─ artifacts/
```

## 6. 实施与待确认项

- 仓库已调整为公开：`https://github.com/zianzhao68/embodied-learning-lab`。
- Astro 静态主站已在 `site/` 实施，旧版 `web/` 未覆盖。
- GitHub Pages Actions 工作流已配置并成功部署：`https://zianzhao68.github.io/embodied-learning-lab/`。
- 待使用真实手机网络验证中国大陆访问体验；自定义域名和 ICP 备案为后续可选项。
- 暂不需要登录和跨手机/电脑同步进度，因此不引入后端。

## 7. 调研来源

- Astro Content Collections：https://docs.astro.build/en/guides/content-collections/
- Astro Islands：https://docs.astro.build/en/concepts/islands/
- Astro MDX：https://docs.astro.build/en/guides/integrations-guide/mdx/
- EdgeOne Astro：https://pages.edgeone.ai/document/framework-astro
- EdgeOne 免费配额：https://pages.edgeone.ai/zh/document/limits-and-quotas
- EdgeOne Git 部署：https://pages.edgeone.ai/zh/document/create-deploys
- EdgeOne 域名与大陆访问：https://pages.edgeone.ai/zh/document/domain-overview
- EdgeOne 自定义域名：https://pages.edgeone.ai/zh/document/custom-domain
- Cloudflare Pages 限制：https://developers.cloudflare.com/pages/platform/limits/
- GitHub Pages 限制：https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- GitHub Actions 计费：https://docs.github.com/en/billing/concepts/product-billing/github-actions
