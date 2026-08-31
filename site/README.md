# 具身学习实验室 · Astro 站点

这是当前主站项目。旧版 Vite 原型保留在 `../web/`，仅用于迁移对照。

## 本地开发

```powershell
cd D:\vla\site
npm install
npm run dev
```

默认访问：`http://localhost:4321`

第一课：`http://localhost:4321/courses/coordinate-frames/`

第二课：`http://localhost:4321/courses/rotation-representations/`

公网地址：`https://zianzhao68.github.io/embodied-learning-lab/`

## 验证与构建

```powershell
npm run check
npm run build
npm audit
npm run preview
```

静态产物输出到 `dist/`。

## 添加课程

1. 先读取 `../docs/course-standard.md`。
2. 复制 `templates/COURSE_TEMPLATE.mdx` 到 `src/content/courses/`。
3. 填写 frontmatter；`slug` 必须唯一，使用小写英文和连字符。
4. 若有测试，在 `src/data/quizzes.ts` 中使用课程 `slug` 注册。
5. 图片和 SVG 放入 `public/assets/`。
6. 完成桌面端、390px 手机端、构建和依赖审计检查。

## 架构

- Astro 静态生成
- Content Collections + schema
- Markdown/MDX + KaTeX
- Manim 技术动画；源代码和分镜位于 `../videos/`，站点只发布压缩后的 MP4 与海报
- 原生 TypeScript 交互，不引入整站前端框架
- 学习进度暂存 `localStorage`

公网使用 GitHub Pages，由 `.github/workflows/pages.yml` 在 `main` 更新后自动部署。Astro 的 `base` 由工作流传入，以适配 `/embodied-learning-lab/` 项目子路径。自定义域名为后续可选项。
