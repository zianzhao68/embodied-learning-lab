import coordinateFrames from './01-coordinate-frames.md?raw'

export const courses = [
  {
    slug: 'coordinate-frames',
    order: 1,
    phase: '机器人基础',
    title: '坐标系与刚体变换',
    description: '从矩阵的列组合直觉出发，掌握旋转、平移、齐次变换及机器人变换链。',
    duration: '90–120 分钟',
    level: '基础',
    tags: ['矩阵直觉', 'SE(3)', '坐标变换'],
    content: coordinateFrames,
    quiz: [
      {
        question: '从“列的加权组合”理解，$\\mathbf{A}\\mathbf{x}$ 表示什么？',
        options: [
          '把 A 的每一行分别乘同一个常数',
          '用 x 的各分量给 A 的对应列加权，再把结果相加',
          '只对 A 和 x 的对应元素相乘',
          '把 A 的所有元素与 x 的所有元素相加'
        ],
        answer: [1],
        explain: '若 A=[a₁ a₂ …]，则 Ax=x₁a₁+x₂a₂+…；输入分量就是各列向量的权重。'
      },
      {
        question: '若 $\\mathbf{A}=\\begin{bmatrix}1&2\\\\3&0\\end{bmatrix}$，$\\mathbf{x}=\\begin{bmatrix}2\\\\4\\end{bmatrix}$，则 $\\mathbf{A}\\mathbf{x}$ 为？',
        options: [
          '$\\begin{bmatrix}4\\\\12\\end{bmatrix}$',
          '$\\begin{bmatrix}10\\\\6\\end{bmatrix}$',
          '$\\begin{bmatrix}8\\\\3\\end{bmatrix}$',
          '$\\begin{bmatrix}6\\\\12\\end{bmatrix}$'
        ],
        answer: [1],
        explain: '按列组合：2·(1,3)ᵀ+4·(2,0)ᵀ=(10,6)ᵀ；按行点乘也得到相同结果。'
      },
      {
        question: '${}^{\\mathrm{A}}\\mathbf{R}_{\\mathrm{B}}$ 的三列分别表示什么？',
        options: [
          'A 坐标系的三个轴在 B 系中的表达',
          'B 坐标系的三个轴在 A 系中的表达',
          'B 坐标系原点在 A 系中的位置',
          '点 P 在三个方向上的坐标'
        ],
        answer: [1],
        explain: '旋转矩阵的三列是 B 系 x、y、z 轴分别在 A 系中的坐标。'
      },
      {
        question: '右手拇指指向 $+z$，从 $+z$ 端看向原点时，正旋转方向是什么？',
        options: [
          '顺时针，且 +x 转向 −y',
          '逆时针，且 +x 转向 +y',
          '顺时针，且 +x 转向 +z',
          '方向与观察位置无关，任何视角都必须看成逆时针'
        ],
        answer: [1],
        explain: '拇指指向 +z，四指弯曲给出 +θ。从 +z 端看向原点时表现为逆时针，+x 转向 +y。换到 −z 端观察会看成顺时针。'
      },
      {
        question: '按照右手定则，绕 $+x$ 轴旋转 $+90^{\\circ}$ 时，哪个方向关系正确？',
        options: [
          '$+y\\rightarrow+z$',
          '$+y\\rightarrow-z$',
          '$+z\\rightarrow+y$',
          '$+x\\rightarrow+y$'
        ],
        answer: [0],
        explain: '右手拇指指向 +x，四指从 +y 弯向 +z，因此绕 +x 的 +90° 将 +y 转向 +z。'
      },
      {
        question: 'B 系相对 A 系绕 $+z$ 旋转 90° 时，${}^{\\mathrm{A}}\\mathbf{R}_{\\mathrm{B}}$ 第二列中的 $-1$ 表示什么？',
        options: [
          'B 的正 x 轴在 A 中指向负 y',
          'B 的正 y 轴在 A 中指向负 x',
          'B 的正 z 轴长度变成了负数',
          '旋转时必须人为加入一个负号'
        ],
        answer: [1],
        explain: '第二列描述 B 的正 y 轴。旋转 +90° 后，它在 A 坐标系中指向负 x，所以坐标为 (−1,0,0)ᵀ。'
      },
      {
        question: '已知 ${}^{\\mathrm{A}}\\mathbf{T}_{\\mathrm{B}}$ 和 ${}^{\\mathrm{B}}\\mathbf{T}_{\\mathrm{C}}$，正确的复合顺序是？',
        options: [
          '${}^{\\mathrm{A}}\\mathbf{T}_{\\mathrm{C}}={}^{\\mathrm{B}}\\mathbf{T}_{\\mathrm{C}}{}^{\\mathrm{A}}\\mathbf{T}_{\\mathrm{B}}$',
          '${}^{\\mathrm{A}}\\mathbf{T}_{\\mathrm{C}}={}^{\\mathrm{A}}\\mathbf{T}_{\\mathrm{B}}{}^{\\mathrm{B}}\\mathbf{T}_{\\mathrm{C}}$',
          '${}^{\\mathrm{A}}\\mathbf{T}_{\\mathrm{C}}={}^{\\mathrm{B}}\\mathbf{T}_{\\mathrm{A}}{}^{\\mathrm{B}}\\mathbf{T}_{\\mathrm{C}}$'
        ],
        answer: [1],
        explain: '从右向左先 C→B，再 B→A；相邻的 B 上下标可以消去。'
      },
      {
        question: 'B 系相对 A 系绕 z 轴旋转 90°，B 原点在 A 系为 (1,2,0)。若 ${}^{\\mathrm{B}}\\mathbf{p}=(0,1,0)$，则 ${}^{\\mathrm{A}}\\mathbf{p}$ 为？',
        options: ['(0,2,0)', '(1,3,0)', '(2,2,0)', '(1,1,0)'],
        answer: [0],
        explain: 'B 的正 y 轴在 A 中指向负 x，因此 (1,2,0)+(-1,0,0)=(0,2,0)。'
      },
      {
        question: '为什么逆变换的平移是 $-\\mathbf{R}^{\\mathsf T}\\mathbf{t}$？',
        options: [
          '因为矩阵求逆规定所有元素都取负',
          '因为 t 原来在 A 系表达，取反后还要用 Rᵀ 转换到 B 系',
          '为了让齐次矩阵的行列式等于 0',
          '只是一种记号约定，没有几何意义'
        ],
        answer: [1],
        explain: '逆向平移需要在目标坐标系 B 中表达，所以除了反向，还必须旋转表达坐标系。'
      },
      {
        question: '机器人移动后抓取点整体偏移，哪些应优先检查？（多选）',
        options: [
          'TF 方向或乘法顺序是否写反',
          '是否把本应动态更新的变换当成固定外参',
          '把分割模型训练轮数直接翻倍',
          '是否混用了米和毫米'
        ],
        answer: [0, 1, 3],
        explain: '优先排查变换方向、动态 TF 与单位；识别稳定时盲目增加训练轮数通常无效。',
        multiple: true
      }
    ]
  }
]
