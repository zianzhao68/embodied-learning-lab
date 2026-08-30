export interface QuizQuestion {
  question: string
  options: string[]
  answer: number[]
  explain: string
  multiple?: boolean
}

export const quizzes: Record<string, QuizQuestion[]> = {
  'coordinate-frames': [
    {
      question: '从“列的加权组合”理解，$\\mathbf{A}\\mathbf{x}$ 表示什么？',
      options: ['把 A 的每一行分别乘同一个常数', '用 x 的各分量给 A 的对应列加权，再把结果相加', '只对 A 和 x 的对应元素相乘', '把 A 的所有元素与 x 的所有元素相加'],
      answer: [1],
      explain: '若 A=[a₁ a₂ …]，则 Ax=x₁a₁+x₂a₂+…；输入分量就是各列向量的权重。'
    },
    {
      question: '若 $\\mathbf{A}=\\begin{bmatrix}1&2\\\\3&0\\end{bmatrix}$，$\\mathbf{x}=\\begin{bmatrix}2\\\\4\\end{bmatrix}$，则 $\\mathbf{A}\\mathbf{x}$ 为？',
      options: ['$\\begin{bmatrix}4\\\\12\\end{bmatrix}$', '$\\begin{bmatrix}10\\\\6\\end{bmatrix}$', '$\\begin{bmatrix}8\\\\3\\end{bmatrix}$', '$\\begin{bmatrix}6\\\\12\\end{bmatrix}$'],
      answer: [1],
      explain: '按列组合：2·(1,3)ᵀ+4·(2,0)ᵀ=(10,6)ᵀ；按行点乘也得到相同结果。'
    },
    {
      question: '${}^{\\mathrm{A}}\\mathbf{R}_{\\mathrm{B}}$ 的三列分别表示什么？',
      options: ['A 坐标系的三个轴在 B 系中的表达', 'B 坐标系的三个轴在 A 系中的表达', 'B 坐标系原点在 A 系中的位置', '点 P 在三个方向上的坐标'],
      answer: [1],
      explain: '旋转矩阵的三列是 B 系 x、y、z 轴分别在 A 系中的坐标。'
    },
    {
      question: '右手拇指指向 $+z$，从 $+z$ 端看向原点时，正旋转方向是什么？',
      options: ['顺时针，且 +x 转向 −y', '逆时针，且 +x 转向 +y', '顺时针，且 +x 转向 +z', '方向与观察位置无关，任何视角都必须看成逆时针'],
      answer: [1],
      explain: '拇指指向 +z，四指弯曲给出 +θ。从 +z 端看向原点时表现为逆时针，+x 转向 +y。换到 −z 端观察会看成顺时针。'
    },
    {
      question: '按照右手定则，绕 $+x$ 轴旋转 $+90^{\\circ}$ 时，哪个方向关系正确？',
      options: ['$+y\\rightarrow+z$', '$+y\\rightarrow-z$', '$+z\\rightarrow+y$', '$+x\\rightarrow+y$'],
      answer: [0],
      explain: '右手拇指指向 +x，四指从 +y 弯向 +z，因此绕 +x 的 +90° 将 +y 转向 +z。'
    },
    {
      question: 'B 系相对 A 系绕 $+z$ 旋转 90° 时，${}^{\\mathrm{A}}\\mathbf{R}_{\\mathrm{B}}$ 第二列中的 $-1$ 表示什么？',
      options: ['B 的正 x 轴在 A 中指向负 y', 'B 的正 y 轴在 A 中指向负 x', 'B 的正 z 轴长度变成了负数', '旋转时必须人为加入一个负号'],
      answer: [1],
      explain: '第二列描述 B 的正 y 轴。旋转 +90° 后，它在 A 坐标系中指向负 x，所以坐标为 (−1,0,0)ᵀ。'
    },
    {
      question: '已知 ${}^{\\mathrm{A}}\\mathbf{T}_{\\mathrm{B}}$ 和 ${}^{\\mathrm{B}}\\mathbf{T}_{\\mathrm{C}}$，正确的复合顺序是？',
      options: ['${}^{\\mathrm{A}}\\mathbf{T}_{\\mathrm{C}}={}^{\\mathrm{B}}\\mathbf{T}_{\\mathrm{C}}{}^{\\mathrm{A}}\\mathbf{T}_{\\mathrm{B}}$', '${}^{\\mathrm{A}}\\mathbf{T}_{\\mathrm{C}}={}^{\\mathrm{A}}\\mathbf{T}_{\\mathrm{B}}{}^{\\mathrm{B}}\\mathbf{T}_{\\mathrm{C}}$', '${}^{\\mathrm{A}}\\mathbf{T}_{\\mathrm{C}}={}^{\\mathrm{B}}\\mathbf{T}_{\\mathrm{A}}{}^{\\mathrm{B}}\\mathbf{T}_{\\mathrm{C}}$'],
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
      options: ['因为矩阵求逆规定所有元素都取负', '因为 t 原来在 A 系表达，取反后还要用 Rᵀ 转换到 B 系', '为了让齐次矩阵的行列式等于 0', '只是一种记号约定，没有几何意义'],
      answer: [1],
      explain: '逆向平移需要在目标坐标系 B 中表达，所以除了反向，还必须旋转表达坐标系。'
    },
    {
      question: '机器人移动后抓取点整体偏移，哪些应优先检查？（多选）',
      options: ['TF 方向或乘法顺序是否写反', '是否把本应动态更新的变换当成固定外参', '把分割模型训练轮数直接翻倍', '是否混用了米和毫米'],
      answer: [0, 1, 3],
      explain: '优先排查变换方向、动态 TF 与单位；识别稳定时盲目增加训练轮数通常无效。',
      multiple: true
    }
  ],
  'rotation-representations': [
    {
      question: '一个矩阵属于 $\\mathrm{SO}(3)$ 必须同时满足什么条件？',
      options: ['$\\mathbf{R}^{\\mathsf T}\\mathbf{R}=\\mathbf{I}_3$ 且 $\\det(\\mathbf{R})=1$', '矩阵所有元素都大于 0', '$\\det(\\mathbf{R})=-1$', '矩阵必须是对称矩阵'],
      answer: [0],
      explain: '正交性保证轴单位且互相垂直，行列式为 1 保证右手性并排除镜像反射。'
    },
    {
      question: '若 $\\mathbf{R}^{\\mathsf T}\\mathbf{R}=\\mathbf{I}_3$，但 $\\det(\\mathbf{R})=-1$，它表示什么？',
      options: ['合法三维旋转', '反射或旋转与反射的组合', '零旋转', '四元数未归一化'],
      answer: [1],
      explain: '行列式为 −1 的正交矩阵改变手性，属于 O(3) 但不属于 SO(3)。'
    },
    {
      question: '列向量和 ZYX 约定下，$\\mathbf{R}=\\mathbf{R}_z(\\psi)\\mathbf{R}_y(\\theta)\\mathbf{R}_x(\\phi)$ 对向量的实际作用顺序是什么？',
      options: ['先 yaw，再 pitch，最后 roll', '先 roll，再 pitch，最后 yaw', '三次同时发生，顺序无关', '只执行 pitch'],
      answer: [1],
      explain: '矩阵从右向左作用，因此最右侧 Rx(roll) 最先作用，然后是 Ry(pitch) 和 Rz(yaw)。'
    },
    {
      question: 'ZYX 欧拉角在 pitch 为 $\\pm90^{\\circ}$ 附近出现万向节锁，其本质是什么？',
      options: ['机器人少了一个物理关节', '旋转矩阵不再正交', '欧拉角参数化奇异，roll 与 yaw 发生耦合', '四元数范数变成 0'],
      answer: [2],
      explain: '物理姿态仍有 3 个自由度，但该欧拉角坐标在奇异位置失去唯一性。'
    },
    {
      question: '轴角 Rodrigues 旋转中，单位旋转轴 $\\mathbf{u}$ 满足哪个关系？',
      options: ['$\\mathbf{R}\\mathbf{u}=\\mathbf{0}$', '$\\mathbf{R}\\mathbf{u}=\\mathbf{u}$', '$\\mathbf{R}\\mathbf{u}=-\\mathbf{u}$', '$\\lVert\\mathbf{u}\\rVert_2=0$'],
      answer: [1],
      explain: '绕轴旋转不会改变轴自身方向，因此旋转轴是特征值为 1 的方向。'
    },
    {
      question: '绕 $+z$ 轴旋转 $90^{\\circ}$，按 $(w,x,y,z)$ 顺序的单位四元数是哪一个？',
      options: ['$(0,0,0,1)$', '$(\\sqrt2/2,0,0,\\sqrt2/2)$', '$(1,0,0,1)$', '$(\\sqrt2/2,\\sqrt2/2,0,0)$'],
      answer: [1],
      explain: '轴为 (0,0,1)，半角为 45°，所以 q=(cos45°,0,0,sin45°)。'
    },
    {
      question: '单位四元数 $\\mathbf{q}$ 与 $-\\mathbf{q}$ 的关系是什么？',
      options: ['表示相反旋转', '表示同一个三维旋转', '只有 q 合法', '两者旋转轴相同但角度相差 90°'],
      answer: [1],
      explain: '四元数对 SO(3) 是双覆盖；q 与 −q 作用到向量时两个负号抵消。'
    },
    {
      question: '若先执行四元数旋转 $\\mathbf{q}_1$，再执行 $\\mathbf{q}_2$，总旋转应写成什么？',
      options: ['$\\mathbf{q}_1\\otimes\\mathbf{q}_2$', '$\\mathbf{q}_2\\otimes\\mathbf{q}_1$', '$\\mathbf{q}_1+\\mathbf{q}_2$', '$\\mathbf{q}_1-\\mathbf{q}_2$'],
      answer: [1],
      explain: '与列向量旋转矩阵一致，右侧旋转先作用，因此总旋转为 q₂⊗q₁。'
    },
    {
      question: 'SLERP 前发现 $\\mathbf{q}_0^{\\mathsf T}\\mathbf{q}_1<0$，通常应如何处理？',
      options: ['把 q₁ 取负后再插值', '把两个四元数都设为 0', '直接交换 w 与 x', '改成欧拉角逐元素相加'],
      answer: [0],
      explain: 'q₁ 与 −q₁ 表示同一旋转；取负可以选择四维单位球面上的较短插值路径。'
    },
    {
      question: '机器人姿态接口对接时，哪些项目必须显式检查？（多选）',
      options: ['四元数字段是 wxyz 还是 xyzw', '角度使用 degree 还是 radian', '主动/被动旋转与坐标系方向', '只要数组长度为 4 就无需检查'],
      answer: [0, 1, 2],
      explain: '字段顺序、角度单位、旋转方向和坐标系语义都会造成姿态错误；数组长度不能说明约定。',
      multiple: true
    }
  ]
}
