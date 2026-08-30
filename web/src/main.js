import './styles.css'
import 'katex/dist/katex.min.css'
import katex from 'katex'
import MarkdownIt from 'markdown-it'
import texmath from 'markdown-it-texmath'
import { courses } from './courses/catalog.js'

const md = new MarkdownIt({ html: true, linkify: true, typographer: true })
  .use(texmath, { engine: katex, delimiters: 'dollars' })
const app = document.querySelector('#app')

const icon = {
  arrow: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10h11m-4-4 4 4-4 4"/></svg>',
  back: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="m12 5-5 5 5 5"/></svg>'
}

function shell(content) {
  return `
    <header class="topbar">
      <a class="brand" href="#/">
        <span class="brand-mark">E</span>
        <span><strong>Embodied Lab</strong><small>具身学习实验室</small></span>
      </a>
      <nav><a href="#/">课程</a><a href="#/roadmap">学习路径</a></nav>
    </header>
    ${content}
    <footer><span>Embodied Learning Lab</span><span>理解 · 实现 · 验证 · 复盘</span></footer>`
}

function renderHome() {
  const completed = courses.filter(c => localStorage.getItem(`course:${c.slug}:done`) === '1').length
  app.innerHTML = shell(`
    <main>
      <section class="hero">
        <div class="eyebrow">EMBODIED INTELLIGENCE · SYSTEMATIC COURSE</div>
        <h1>从空间直觉出发，<br><em>构建完整的具身能力链。</em></h1>
        <p>面向具身算法工程师的项目制课程。每一课都包含清晰公式、原理图解、工程映射与即时测试。</p>
        <div class="hero-actions">
          <a class="button primary" href="#/course/${courses[0].slug}">开始第一课 ${icon.arrow}</a>
          <a class="button ghost" href="#/roadmap">查看学习路径</a>
        </div>
        <div class="stats"><div><strong>${courses.length}</strong><span>已发布课程</span></div><div><strong>${completed}</strong><span>已完成</span></div><div><strong>9 个月</strong><span>成长路线</span></div></div>
      </section>
      <section class="course-section">
        <div class="section-heading"><div><span>CURRICULUM</span><h2>课程目录</h2></div><p>先建立机器人基础，再进入模仿学习与 VLA。</p></div>
        <div class="course-grid">${courses.map(courseCard).join('')}</div>
      </section>
    </main>`)
}

function courseCard(course) {
  const done = localStorage.getItem(`course:${course.slug}:done`) === '1'
  return `<a class="course-card" href="#/course/${course.slug}">
    <div class="card-top"><span class="course-no">0${course.order}</span><span class="status ${done ? 'done' : ''}">${done ? '已完成' : course.level}</span></div>
    <span class="phase">${course.phase}</span><h3>${course.title}</h3><p>${course.description}</p>
    <div class="tags">${course.tags.map(t => `<span>${t}</span>`).join('')}</div>
    <div class="card-bottom"><span>${course.duration}</span><span class="read">进入课程 ${icon.arrow}</span></div>
  </a>`
}

function renderCourse(course) {
  const content = md.render(course.content)
  app.innerHTML = shell(`
    <div class="course-layout">
      <aside class="course-sidebar">
        <a class="back-link" href="#/">${icon.back} 返回课程</a>
        <div class="sidebar-meta"><span>课程 0${course.order}</span><strong>${course.title}</strong><small>${course.duration}</small></div>
        <nav id="toc" class="toc" aria-label="本课目录"></nav>
      </aside>
      <main class="lesson-wrap">
        <article class="lesson">
          <div class="lesson-kicker"><span>${course.phase}</span><span>${course.level}</span><span>${course.duration}</span></div>
          ${content}
          ${quizTemplate(course)}
        </article>
      </main>
    </div>`)

  buildToc()
  bindQuiz(course)
  observeHeadings()
}

function quizTemplate(course) {
  return `<section class="quiz" id="课程测试">
    <div class="quiz-heading"><span>KNOWLEDGE CHECK</span><h2>本课测试</h2><p>不要回看正文。提交后会即时给出结果与解释，成绩仅保存在本机。</p></div>
    <form id="quiz-form">
      ${course.quiz.map((q, i) => `<fieldset class="question" data-index="${i}">
        <legend><span>${String(i + 1).padStart(2, '0')}</span>${md.renderInline(q.question)}${q.multiple ? '<small>多选</small>' : ''}</legend>
        <div class="options">${q.options.map((o, j) => `<label><input type="${q.multiple ? 'checkbox' : 'radio'}" name="q${i}" value="${j}"><span class="option-mark"></span><span>${md.renderInline(o)}</span></label>`).join('')}</div>
        <div class="feedback" aria-live="polite"></div>
      </fieldset>`).join('')}
      <button class="button primary submit-quiz" type="submit">提交答案 ${icon.arrow}</button>
      <div id="quiz-result" class="quiz-result" aria-live="polite"></div>
    </form>
  </section>`
}

function bindQuiz(course) {
  const form = document.querySelector('#quiz-form')
  form.addEventListener('submit', event => {
    event.preventDefault()
    let score = 0
    course.quiz.forEach((q, i) => {
      const field = form.querySelector(`[data-index="${i}"]`)
      const selected = [...field.querySelectorAll('input:checked')].map(el => Number(el.value)).sort()
      const answer = [...q.answer].sort()
      const correct = selected.length === answer.length && selected.every((v, n) => v === answer[n])
      if (correct) score += 1
      field.classList.toggle('correct', correct)
      field.classList.toggle('wrong', !correct)
      field.querySelector('.feedback').innerHTML = `<strong>${correct ? '回答正确' : '需要复习'}</strong><span>${q.explain}</span>`
    })
    const percent = Math.round(score / course.quiz.length * 100)
    const passed = percent >= 80
    if (passed) localStorage.setItem(`course:${course.slug}:done`, '1')
    localStorage.setItem(`course:${course.slug}:score`, String(percent))
    document.querySelector('#quiz-result').innerHTML = `<strong>${score} / ${course.quiz.length}</strong><span>${passed ? '已达到本课通过标准。建议在第 1、3、7、14 天主动回忆。' : '建议重读错误对应章节，稍后再次测试。通过标准为 80%。'}</span>`
    document.querySelector('#quiz-result').scrollIntoView({ behavior: 'smooth', block: 'center' })
  })
}

function buildToc() {
  const headings = [...document.querySelectorAll('.lesson > h2')]
  const toc = document.querySelector('#toc')
  headings.forEach((heading, i) => {
    const id = heading.textContent.trim().replace(/[\s·]+/g, '-').replace(/[^\w\u4e00-\u9fa5-]/g, '')
    heading.id = id || `section-${i}`
  })
  toc.innerHTML = headings.map((h, i) => `<a href="#${h.id}" data-target="${h.id}"><span>${String(i + 1).padStart(2, '0')}</span>${h.textContent}</a>`).join('')
}

function observeHeadings() {
  const links = [...document.querySelectorAll('.toc a')]
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        links.forEach(a => a.classList.toggle('active', a.dataset.target === entry.target.id))
      }
    })
  }, { rootMargin: '-15% 0px -70% 0px' })
  document.querySelectorAll('.lesson > h2').forEach(h => observer.observe(h))
}

function renderRoadmap() {
  const stages = [
    ['01', '机器人与 3D 基础', '第 1–8 周', '空间表示、运动学、视觉几何、控制与 ROS2'],
    ['02', '模仿学习与操作策略', '第 9–16 周', 'BC、ACT、Diffusion Policy、数据与评测'],
    ['03', 'VLA', '第 17–28 周', '视觉语言动作模型、微调、部署与泛化'],
    ['04', '前沿专项与作品集', '第 29–36 周', '选择专项问题，完成对照实验和工程交付']
  ]
  app.innerHTML = shell(`<main class="roadmap-page"><div class="eyebrow">LEARNING PATH</div><h1>九个月成长路径</h1><p class="roadmap-intro">以 VLA 操作为主线，以 3D 感知和运动控制为两翼。不是补完全部基础后再实践，而是在项目中反复建立能力。</p><div class="timeline">${stages.map(s => `<section><span>${s[0]}</span><div><small>${s[2]}</small><h2>${s[1]}</h2><p>${s[3]}</p></div></section>`).join('')}</div></main>`)
}

function route() {
  window.scrollTo(0, 0)
  const hash = location.hash || '#/'
  if (hash === '#/roadmap') return renderRoadmap()
  const match = hash.match(/^#\/course\/([^/]+)/)
  if (match) {
    const course = courses.find(c => c.slug === match[1])
    if (course) return renderCourse(course)
  }
  renderHome()
}

window.addEventListener('hashchange', route)
route()
