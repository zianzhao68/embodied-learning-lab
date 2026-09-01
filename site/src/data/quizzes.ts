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
      explain: '物理姿态仍有 3 个自由度；中间的 pitch 把 yaw 轴与 roll 轴转到同一直线，使两个参数只剩一个有效组合。'
    },
    {
      question: '在固定 ZYX 约定下，roll 为 $90^{\\circ}$、pitch 为 $0^{\\circ}$，是否发生万向节锁？',
      options: ['会，因为任意一个角到 90° 都会锁', '不会，ZYX 的奇异由中间角 pitch 到 ±90° 触发', '会，因为旋转矩阵行列式变成 −1', '无法判断，因为还缺少平移'],
      answer: [1],
      explain: '三个不同轴的欧拉角顺序中，奇异位置由中间旋转决定。ZYX 的中间角是 pitch；单独让 roll 或 yaw 到 90° 不会触发。'
    },
    {
      question: '叉乘矩阵 $[\\mathbf{u}]_{\\times}$ 的含义是什么？',
      options: ['把 u 的每个分量平方', '把“与 u 做叉乘”写成线性矩阵运算，使 $[\\mathbf{u}]_{\\times}\\mathbf{p}=\\mathbf{u}\\times\\mathbf{p}$', '计算 u 的长度', '把任意向量投影到 u 上'],
      answer: [1],
      explain: '逐分量展开 u×p，并收集 pₓ、pᵧ、p_z 的系数，就得到这个反对称矩阵；它不是额外规定。'
    },
    {
      question: '关于 $\\mathbf{p}_{\\parallel}$、$\\mathbf{p}_{\\perp}$ 和 $\\mathbf{p}_{\\mathrm{tan}}$，哪项理解正确？',
      options: ['$\\mathbf{p}$ 被拆成三个分量并直接相加', '$\\mathbf{p}=\\mathbf{p}_{\\parallel}+\\mathbf{p}_{\\perp}$；$\\mathbf{p}_{\\mathrm{tan}}$ 是描述圆平面旋转的辅助方向', '$\\mathbf{p}_{\\parallel}$ 是旋转半径', '$\\mathbf{p}_{\\mathrm{tan}}$ 始终等于旋转轴'],
      answer: [1],
      explain: '真实分解只有平行分量和垂直半径。切向量由叉乘构造，用作圆平面内与半径垂直的第二个坐标方向。'
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
  ],
  'se3-transform-chains': [
    {
      question: '刚体变换对同一刚体上的任意两点保持什么性质？',
      options: ['每个点到世界原点的距离不变', '两点之间的距离不变', '每个点的三个坐标数字不变', '平移向量始终为零'],
      answer: [1],
      explain: '两点做差时共同平移抵消，旋转矩阵保持向量长度，因此刚体内部点间距离不变；点到世界原点的距离可以改变。'
    },
    {
      question: '普通单位四元数与完整机器人位姿的关系是什么？',
      options: ['四元数同时编码旋转和平移', '四元数只编码旋转，完整位姿还需要平移向量', '四元数只编码平移', '四元数的 xyz 分量就是三轴平移'],
      answer: [1],
      explain: '单位四元数表示 SO(3) 旋转。常见机器人位姿使用 (t,q)，再构造成 SE(3) 齐次矩阵。'
    },
    {
      question: '齐次坐标中，为什么点使用 $w=1$、方向使用 $w=0$？',
      options: ['w 表示时间', 'w 控制平移项：点受到平移，方向不应因原点移动而改变', '方向只能在二维中使用', '这样能让旋转矩阵行列式变成 0'],
      answer: [1],
      explain: '矩阵乘法的右上平移块会乘 w。w=1 时得到 Rp+t；w=0 时只得到 Rv。'
    },
    {
      question: '一个 $4\times4$ 矩阵属于 $\mathrm{SE}(3)$，哪些条件必须满足？（多选）',
      options: ['左上角属于 SO(3)', '右上角是三维平移', '最后一行为 $(0,0,0,1)$', '所有 16 个元素都必须非零'],
      answer: [0, 1, 2],
      explain: 'SE(3) 的标准分块形式为 [R t; 0 1]，其中 R∈SO(3)、t∈R³；元素是否为零不是合法性条件。',
      multiple: true
    },
    {
      question: '已知 ${}^{\mathrm A}\mathbf T_{\mathrm B}$ 与 ${}^{\mathrm B}\mathbf T_{\mathrm C}$，正确复合是哪一个？',
      options: ['${}^{\mathrm A}\mathbf T_{\mathrm C}={}^{\mathrm A}\mathbf T_{\mathrm B}{}^{\mathrm B}\mathbf T_{\mathrm C}$', '${}^{\mathrm A}\mathbf T_{\mathrm C}={}^{\mathrm B}\mathbf T_{\mathrm C}{}^{\mathrm A}\mathbf T_{\mathrm B}$', '${}^{\mathrm C}\mathbf T_{\mathrm A}={}^{\mathrm A}\mathbf T_{\mathrm B}+{}^{\mathrm B}\mathbf T_{\mathrm C}$', '顺序任意'],
      answer: [0],
      explain: '从右向左先 C→B，再 B→A；相邻 B 上下标消去，得到 A←C。'
    },
    {
      question: '若 $\mathbf R_1=\mathbf R_z(90^\circ)$、$\mathbf t_1=(1,2,0)$，第二段 $\mathbf t_2=(2,0,0)$ 在中间坐标系表达，则复合平移是多少？',
      options: ['(3,2,0)', '(1,4,0)', '(-1,2,0)', '(1,0,0)'],
      answer: [1],
      explain: '先计算 R₁t₂=(0,2,0)，再加 t₁=(1,2,0)，得到 (1,4,0)。不能直接相加不同坐标系表达的平移。'
    },
    {
      question: '$\mathbf T=[\mathbf R\ \mathbf t;\mathbf0^{\mathsf T}\ 1]$ 的逆变换平移为什么是 $-\mathbf R^{\mathsf T}\mathbf t$？',
      options: ['只需把所有矩阵元素取负', '返回时既要反向平移，也要把该平移改写到逆变换的输出坐标系', '为了使最后一行变成零', '因为 R 的行列式是 −1'],
      answer: [1],
      explain: '从 p_A=Rp_B+t 解出 p_B=Rᵀp_A−Rᵀt；−t 仍在原输出系表达，必须再乘 Rᵀ。'
    },
    {
      question: '已知 ${}^{\mathrm W}\mathbf T_{\mathrm A}$ 和 ${}^{\mathrm W}\mathbf T_{\mathrm B}$，B 相对 A 的位姿是什么？',
      options: ['$({}^{\mathrm W}\mathbf T_{\mathrm A})^{-1}{}^{\mathrm W}\mathbf T_{\mathrm B}$', '${}^{\mathrm W}\mathbf T_{\mathrm A}+{}^{\mathrm W}\mathbf T_{\mathrm B}$', '${}^{\mathrm W}\mathbf T_{\mathrm A}({}^{\mathrm W}\mathbf T_{\mathrm B})^{-1}$', '${}^{\mathrm W}\mathbf T_{\mathrm B}-{}^{\mathrm W}\mathbf T_{\mathrm A}$'],
      answer: [0],
      explain: '先由 A 返回 W，再由 W 进入 B：A←W · W←B = A←B。'
    },
    {
      question: '主动刚体运动与被动坐标转换的主要区别是什么？',
      options: ['主动运动中物体实际移动；被动转换中空间点不动，只改变坐标表达', '被动转换一定包含缩放', '主动运动不能使用矩阵', '两者永远使用不同数值矩阵'],
      answer: [0],
      explain: '两者可能出现相同矩阵形式，但回答的物理问题不同；必须结合输入/输出 frame 和语义判断。'
    },
    {
      question: '眼在手上系统中，从抓取模板到 base 的正确链路是哪一个？',
      options: ['T_base_ee · T_ee_camera · T_camera_object · T_object_grasp', 'T_object_grasp · T_camera_object · T_ee_camera · T_base_ee', 'T_base_camera · T_ee_object', '四段变换直接相加'],
      answer: [0],
      explain: '从右向左依次 grasp→object→camera→ee→base，相邻 frame 名配对。'
    },
    {
      question: '眼在手上链路中，哪些通常是动态项？（多选）',
      options: ['由当前关节状态得到的 T_base_ee', '每帧视觉得到的 T_camera_object', '离线手眼标定 T_ee_camera', '固定抓取模板 T_object_grasp'],
      answer: [0, 1],
      explain: '末端相对 base 的位姿随关节运动更新，物体观测随视觉帧更新；手眼外参与抓取模板通常固定但需版本化。',
      multiple: true
    },
    {
      question: '抓取点出现稳定偏差或随运动漂移时，应优先检查哪些项目？（多选）',
      options: ['frame 方向与乘法顺序', '机器人状态和图像时间戳', '米/毫米单位', '静态与动态变换是否混淆', '直接增加视觉模型训练轮数'],
      answer: [0, 1, 2, 3],
      explain: '稳定偏差和运动相关漂移首先指向坐标链、时序、单位或外参使用问题；盲目增加训练轮数不能修复几何链路错误。',
      multiple: true
    }
  ],
  'forward-kinematics': [
    {
      question: '转动关节和移动关节的关节变量分别通常是什么？',
      options: ['角度与沿轴距离', '沿轴距离与角度', '两者都是末端 xyz', '两者都是四元数'],
      answer: [0],
      explain: '转动关节变量是绕关节轴的角度，移动关节变量是沿关节轴的位移；它们描述相邻连杆的相对运动。'
    },
    {
      question: '机械臂的自由度（DOF）最准确的含义是什么？',
      options: ['连杆的总数量', '描述构型所需的独立关节变量数量', '末端矩阵中的 16 个数字', '所有传感器数量'],
      answer: [1],
      explain: 'DOF 是系统独立构型变量的数量，不等于连杆数，也不等于位姿表示使用的参数个数。'
    },
    {
      question: '正运动学 $f(\mathbf q)$ 的输入和输出分别是什么？',
      options: ['末端位姿到关节变量', '关节变量到末端位姿', '图像到点云', '速度到力矩'],
      answer: [1],
      explain: 'FK 已知关节构型 q，计算末端相对 base 的位姿；反方向的问题属于逆运动学。'
    },
    {
      question: '平面 2R 中，$q_2$ 是第二连杆相对第一连杆的角度。第二连杆相对 base 的绝对方向是多少？',
      options: ['$q_2$', '$q_1+q_2$', '$q_1-q_2$', '$q_1q_2$'],
      answer: [1],
      explain: '第一关节先带动整条下游链旋转 q₁，第二关节再相对第一连杆旋转 q₂，所以绝对方向为 q₁+q₂。'
    },
    {
      question: '2R 机械臂中 $l_1=0.4$ m、$l_2=0.3$ m、$q_1=30^\circ$、$q_2=60^\circ$，末端 y 坐标是多少？',
      options: ['0.2 m', '0.3 m', '0.5 m', '0.7 m'],
      answer: [2],
      explain: 'y=0.4sin30°+0.3sin(30°+60°)=0.2+0.3=0.5 m。'
    },
    {
      question: '串联机械臂的正确正运动学链是哪一种？',
      options: ['按 base 到末端的相邻变换有序相乘', '所有局部变换逐元素相加', '相邻变换可以任意交换', '只保留最后一个关节变换'],
      answer: [0],
      explain: '末端位姿是 base←1、1←2、… 的有序矩阵乘积；相邻 frame 配对且矩阵通常不可交换。'
    },
    {
      question: '为什么改变肩部关节会同时改变肘部、腕部和末端位姿？',
      options: ['因为所有关节角必须相等', '肩部变换位于链的上游，会左乘所有下游局部变换', '因为连杆长度同时改变', '因为末端坐标与关节无关'],
      answer: [1],
      explain: '上游关节改变其后的整棵子链；下游关节不会反过来改变上游 frame。'
    },
    {
      question: '本课采用的标准 DH 单节变换顺序是什么？',
      options: ['$R_z(\theta)T_z(d)T_x(a)R_x(\alpha)$', '$T_x(a)R_x(\alpha)R_z(\theta)T_z(d)$', '$R_x(\theta)T_y(d)R_z(a)$', '顺序不影响结果'],
      answer: [0],
      explain: '标准 DH 约定依次写为绕旧 z 转、沿旧 z 移、沿新 x 移、绕新 x 转；不能擅自交换。'
    },
    {
      question: '标准 DH 中，转动关节和移动关节通常分别让哪个参数成为变量？',
      options: ['$\theta_i$ 与 $d_i$', '$a_i$ 与 $\alpha_i$', '$d_i$ 与 $\theta_i$', '两者都只改变 $a_i$'],
      answer: [0],
      explain: '转动关节变量进入 θᵢ，移动关节变量进入 dᵢ；aᵢ、αᵢ通常由连杆几何决定。'
    },
    {
      question: '关于标准 DH 与改进 DH，哪项正确？',
      options: ['两者参数表可不经检查直接混用', '两者 frame 附着和乘法顺序可能不同，参数表必须与实现配套', '改进 DH 不支持转动关节', '标准 DH 只能用于二维机械臂'],
      answer: [1],
      explain: '两种约定都可建模三维机械臂，但参数含义依赖各自 frame 规则；混用会产生系统性错误。'
    },
    {
      question: 'POE 公式中的 $\mathbf M$ 表示什么？',
      options: ['所有关节速度之和', '所有关节变量为零时的末端位姿', '机器人质量矩阵', '相机内参'],
      answer: [1],
      explain: 'POE 用关节螺旋轴的指数变换乘以零位末端构型 M；M 是 home configuration。'
    },
    {
      question: 'FK 与仿真或 TF 不一致时，哪些是合理的优先检查项？（多选）',
      options: ['关节轴与正方向', '弧度/角度和米/毫米', 'base、flange、TCP 固定变换', '标准/改进 DH 是否混用', '直接开始调 IK 参数'],
      answer: [0, 1, 2, 3],
      explain: '应先验证模型、约定、单位和固定外参。FK 错误时继续调 IK 只会掩盖根因。',
      multiple: true
    }
  ],
  'inverse-kinematics-jacobian': [
    {
      question: '平面 2R 的目标距离 $r$ 满足什么条件时位置几何可达？',
      options: ['$|l_1-l_2|\le r\le l_1+l_2$', '$r>l_1+l_2$', '$r<|l_1-l_2|$', '只要 x 和 y 都为正'],
      answer: [0],
      explain: '两根连杆必须能与目标距离组成三角形，因此目标位于以 |l₁−l₂| 和 l₁+l₂ 为内外半径的圆环内。'
    },
    {
      question: '$l_1=0.4$ m、$l_2=0.3$ m 时，距离 base 0.05 m 的目标为什么不可达？',
      options: ['目标太远', '目标太近，小于内半径 0.1 m', '因为 q₂ 必须为 0', '因为 Jacobian 永远为零'],
      answer: [1],
      explain: '最小可达半径为 |0.4−0.3|=0.1 m；长连杆完全折回时末端仍距离 base 0.1 m。'
    },
    {
      question: '平面 2R 普通可达目标为什么通常有两组 IK 解？',
      options: ['四元数双覆盖', '余弦定理给定 cos q₂ 后，sin q₂ 可以取正负，对应两种肘部构型', '因为连杆长度可以改变', '因为平移有正负号'],
      answer: [1],
      explain: '同一三角形可以在目标连线两侧放置肘部；q₂ 的正负分支经 q₁ 公式产生两组关节角。'
    },
    {
      question: '检验一组 IK 关节角是否正确，最可靠的基本方法是什么？',
      options: ['只与某个参考关节角逐元素比较', '将关节角送回 FK，检查末端任务误差', '检查 q₁+q₂ 是否为 0', '检查两个角是否都为正'],
      answer: [1],
      explain: 'IK 可能多解且角度有周期；应验证 f(q) 是否重建目标，并再检查限位和碰撞。'
    },
    {
      question: '$\dot{\mathbf p}=\mathbf J(\mathbf q)\dot{\mathbf q}$ 表达什么？',
      options: ['关节速度到末端瞬时速度的局部线性映射', '末端位置到关节位置的全局唯一映射', '图像到深度的映射', '质量到力矩的映射'],
      answer: [0],
      explain: 'Jacobian 是当前位置附近的速度映射；它依赖 q，步长较大时需要重新线性化。'
    },
    {
      question: '位置 Jacobian 的第 i 列最直观的含义是什么？',
      options: ['所有关节同时以 1 rad/s 运动的速度', '只让第 i 个关节以单位速度运动时的末端速度', '第 i 根连杆长度', '第 i 个关节的绝对位置'],
      answer: [1],
      explain: '将其他关节速度设为 0、q̇ᵢ=1，对应末端速度就是 J 的第 i 列。'
    },
    {
      question: '平面 2R 的位置 Jacobian 在什么条件下奇异？',
      options: ['$q_1=90^\circ$', '$q_2=0$ 或 $\pi$（模 $2\pi$）', '$q_1=q_2$ 时始终奇异', '只要末端 y=0'],
      answer: [1],
      explain: 'det J=l₁l₂sin q₂；两根连杆完全伸直或折叠时 sin q₂=0，Jacobian 秩下降。'
    },
    {
      question: '2R 完全伸直时，奇异的几何机制是什么？',
      options: ['两个关节消失', 'Jacobian 两列共线，只能生成一维切向瞬时速度，不能生成径向速度', '所有末端速度都必须为零', '旋转矩阵行列式变成 −1'],
      answer: [1],
      explain: '两个关节造成的速度都垂直于同一共线半径，所以列空间从二维降为一维；机械臂仍可沿切向运动。'
    },
    {
      question: '$q_1=0,q_2=90^\circ$ 是否触发本课 2R 奇异？',
      options: ['触发，因为任意角到 90° 都奇异', '不触发，此时 det J=l₁l₂≠0', '触发，因为 q₁=0', '无法判断，因为还缺少平移'],
      answer: [1],
      explain: '奇异由 q₂=0 或 π 触发。q₂=90° 时两列不共线，是明确的不触发反例。'
    },
    {
      question: '阻尼最小二乘中的 $\lambda$ 主要解决什么问题？',
      options: ['让不可达目标自动变得可达', '抑制奇异附近小奇异值求逆导致的巨大关节更新', '自动完成碰撞检测', '把角度单位从 degree 变为 radian'],
      answer: [1],
      explain: 'λ²I 使线性系统在奇异附近保持可逆和有限，但会引入偏差，也不能替代可达性与约束检查。'
    },
    {
      question: '关于关节限位与多解，哪项正确？',
      options: ['有数学 IK 解就一定能执行', '应生成候选、过滤限位/碰撞，并优先选择与上一构型连续的解', '每帧随机选择肘上或肘下', '简单 clamp 后总能收敛到目标'],
      answer: [1],
      explain: '数学解还必须满足物理约束；连续选解可避免控制循环在分支间跳变，简单 clamp 可能使迭代停在边界。'
    },
    {
      question: 'IK 失败时应优先记录和检查哪些信息？（多选）',
      options: ['FK 与所有中间 frame', '目标 frame、TCP 和单位', '可达性、关节限位与碰撞', '最小奇异值、初值和最终误差', '只返回一个没有原因的 False'],
      answer: [0, 1, 2, 3],
      explain: 'IK 失败需要区分模型、frame、不可达、约束、奇异、初值和数值问题；单一布尔值不足以诊断。',
      multiple: true
    }
  ],
  'pinhole-camera-projection': [
    {
      question: '在一张 640×480 图像中，像素坐标通常怎样定义？',
      options: ['左上角为 (0,0)，u 向右、v 向下', '左下角为 (0,0)，u 向上、v 向右', '图像中心永远为 (0,0)', 'u、v 的单位都是米'],
      answer: [0],
      explain: '常见图像存储以左上角为原点，列方向是 u，行方向是 v，单位是像素。'
    },
    {
      question: '本课 OpenCV 光学坐标系中的 Z 表示什么？',
      options: ['点到光心的任意欧氏距离', '沿相机光轴向前的深度', '像素的列编号', '相机焦距'],
      answer: [1],
      explain: 'Z 是沿光轴向前的 z-depth。它一般不等于 √(X²+Y²+Z²) 形式的射线距离。'
    },
    {
      question: '为什么投影公式中会出现 $X/Z$？',
      options: ['来自相似三角形，表示横向偏移相对前向深度的比例', '为了把像素换成颜色', '因为 X 与 Z 必须相加', '只是人为规定，没有几何原因'],
      answer: [0],
      explain: '光心、物点和成像平面形成相似三角形，因此 x′/f=X/Z；物体越远，同样 X 对应的图像偏移越小。'
    },
    {
      question: '$f_x=f_y=500$ px、$(c_x,c_y)=(320,240)$ px，点 $(X,Y,Z)=(0.10,0.05,1.00)$ m 投影到哪里？',
      options: ['(50,25)', '(370,265)', '(420,290)', '(320,240)'],
      answer: [1],
      explain: 'X/Z=0.10、Y/Z=0.05；像素偏移为 (50,25)，再加主点得到 (370,265)。'
    },
    {
      question: '保持 X、Y 和内参不变，只把正深度 Z 加倍，会发生什么？',
      options: ['相对主点的像素偏移加倍', '相对主点的像素偏移减半', '像素完全不变', '主点坐标加倍'],
      answer: [1],
      explain: '偏移分别为 fₓX/Z 和 fᵧY/Z，所以 Z 加倍时偏移减半，投影更靠近主点。'
    },
    {
      question: '四个内参的作用分别是什么？',
      options: ['$f_x,f_y$ 控制归一化坐标到像素的尺度，$c_x,c_y$ 给出主点', '它们共同描述相机在世界中的位置', '$c_x,c_y$ 是相机平移的米制坐标', '$f_x,f_y$ 是图像宽和高'],
      answer: [0],
      explain: '内参描述相机内部像素映射；相机在世界中的位姿属于外参。'
    },
    {
      question: '为什么单个像素通常不能确定唯一三维点？',
      options: ['因为像素没有颜色', '同一条穿过光心的射线上，不同共同尺度的点具有相同 X/Z、Y/Z', '因为所有相机都没有焦距', '因为内参矩阵不可逆'],
      answer: [1],
      explain: '投影除以 Z 后丢失共同尺度；一个像素对应一条射线，还需要深度或其他几何约束。'
    },
    {
      question: '已知像素 (370,265)、Z=2 m、$f_x=f_y=500$ px、主点 (320,240)，反投影点是多少？',
      options: ['(0.10,0.05,1.00) m', '(0.20,0.10,2.00) m', '(50,25,2) m', '(370,265,2) m'],
      answer: [1],
      explain: 'X=(370−320)×2/500=0.20 m，Y=(265−240)×2/500=0.10 m，Z=2 m。'
    },
    {
      question: '世界点投影到像素的正确顺序是什么？',
      options: ['先内参，再随意应用外参', '先用 world→camera 外参得到相机坐标，再透视除法并应用内参', '直接把世界坐标 X、Y 当成 u、v', '先删除 Z，再求外参'],
      answer: [1],
      explain: '针孔公式只接受相机坐标；外参先改写坐标表达，内参再把射线方向映射为像素。'
    },
    {
      question: '若相机坐标轴与世界轴平行，相机位于世界 x=1 m，world→camera 的平移为何是 −1 m？',
      options: ['因为焦距为负', '要把世界坐标减去相机光心位置，得到相对相机的位置', '因为图像 v 向下', '这是畸变造成的'],
      answer: [1],
      explain: '对齐坐标轴时，相机中的点等于世界点减去相机在世界中的位置，因此平移是 (−1,0,0)。'
    },
    {
      question: '关于 $Z\le0$ 的点，工程实现应怎样处理？',
      options: ['继续当作正常可见像素', '显式标记无效，例如返回 NaN 像素和 valid=False', '把 Z 自动改成绝对值', '把点放到主点'],
      answer: [1],
      explain: '相机后方或光心平面上的点不是正常可见点；自动取绝对值会掩盖坐标系方向错误。'
    },
    {
      question: 'RGB-D 反投影出现米级错误时，应检查哪些项目？（多选）',
      options: ['内参与当前图像分辨率是否匹配', 'u/v 是否与 row/column 写反', '深度是 m 还是 mm、是 Z 还是 range', '像素畸变状态和 RGB/depth 对齐', 'world↔camera 变换方向', '只增大神经网络规模'],
      answer: [0, 1, 2, 3, 4],
      explain: '几何错误常来自分辨率、坐标顺序、深度定义、畸变/对齐和外参方向；模型规模不能修复错误约定。',
      multiple: true
    }
  ],
  'depth-image-point-cloud': [
    {
      question: '几何像素写作 $(u,v)$ 时，NumPy 深度数组通常怎样索引？',
      options: ['depth[u,v]', 'depth[v,u]', 'depth[X,Z]', 'depth[Z,u]'],
      answer: [1],
      explain: 'u 是列、v 是行；数组通常先行后列，所以写 depth[v,u]。'
    },
    {
      question: '深度原始值 1250 的单位是毫米，换成米是多少？',
      options: ['1250 m', '12.5 m', '1.25 m', '0.125 m'],
      answer: [2],
      explain: '毫米转米乘 0.001：1250×0.001=1.25 m。'
    },
    {
      question: '$f_x=f_y=2$ px、主点 $(1,1)$，像素 $(2,1)$ 的 z-depth 为 1 m，对应相机点是什么？',
      options: ['(0.5,0,1) m', '(2,1,1) m', '(1,0.5,1) m', '(0,0,1) m'],
      answer: [0],
      explain: 'X=(2−1)×1/2=0.5，Y=(1−1)×1/2=0，Z=1。'
    },
    {
      question: '有组织点云 $H\times W\times3$ 的主要优点是什么？',
      options: ['每个三维点仍能追溯到原像素位置', '永远没有无效点', '自动包含三角网格', '不需要相机内参'],
      answer: [0],
      explain: 'P[v,u] 与 depth[v,u]、RGB[v,u] 保持对应，便于 mask 和检测框映射；无效位置仍需 mask。'
    },
    {
      question: '深度值 0 或 NaN 通常应怎样处理？',
      options: ['当作光心处的真实表面', '通过 valid mask 标记无效，不参与几何算法', '统一改成 1 m', '取绝对值'],
      answer: [1],
      explain: '0/NaN 通常表示缺测；伪造深度会在光心或固定平面产生错误点。'
    },
    {
      question: 'z-depth 与 range 的区别是什么？',
      options: ['二者在所有像素都完全相同', 'z-depth 是沿光轴分量，range 是沿斜射线的欧氏距离', 'z-depth 单位是像素', 'range 只表示颜色'],
      answer: [1],
      explain: '中心射线两者相同；离中心后 range 是斜边，通常大于同一点的 Z。'
    },
    {
      question: '射线方向 $(0.5,0,1)$，若给定 z-depth $Z=2$ m，三维点与 range 分别是什么？',
      options: ['点 (1,0,2) m，range 约 2.236 m', '点 (0.5,0,1) m，range 2 m', '点 (1,0,2) m，range 2 m', '点 (2,0,2) m，range 4 m'],
      answer: [0],
      explain: '点为 Z(0.5,0,1)=(1,0,2)，欧氏距离 √(1²+2²)=√5≈2.236 m。'
    },
    {
      question: 'RGB[v,u] 与 depth[v,u] 什么时候可以直接组合颜色和三维点？',
      options: ['只要数组宽高相同', '只有它们已被标定并对齐到同一相机/像素射线', '只要都显示为彩色', '不需要任何条件'],
      answer: [1],
      explain: '不同 RGB/depth 光心存在外参和遮挡差异；相同数组索引不自动代表同一空间射线。'
    },
    {
      question: '图像宽高都缩小为原来一半，简单像素缩放约定下内参怎样更新？',
      options: ['$f_x,f_y,c_x,c_y$ 都乘 0.5', '只有焦距乘 2', '内参完全不变', '主点变成 0'],
      answer: [0],
      explain: '像素坐标整体缩放时，两方向焦距和主点坐标都按对应比例缩放。'
    },
    {
      question: '从左边裁掉 100 列、顶部裁掉 40 行时，主点怎样更新？',
      options: ['$c_x\leftarrow c_x-100, c_y\leftarrow c_y-40$', '$c_x,c_y$ 都加裁剪量', '焦距减裁剪量', '主点不变'],
      answer: [0],
      explain: '新图坐标原点向右下移动，所以同一主点在新图中的编号分别减 left 和 top。'
    },
    {
      question: '相机点云供机械臂抓取前，还需要什么？',
      options: ['直接把 camera 坐标当关节角', '用 $T_{base\leftarrow camera}$ 转换到机器人 base，并检查标定方向', '删除所有 Z', '只把单位改成像素'],
      answer: [1],
      explain: '反投影输出 camera 表达；机器人规划通常要求 base 表达，必须使用正确手眼/TF 变换。'
    },
    {
      question: '点云出现整体尺度或倾斜错误时，应检查哪些项目？（多选）',
      options: ['深度单位与 depth scale', 'z-depth/range 定义', '图像缩放/裁剪后 K 是否更新', 'u/v 与行列顺序', 'camera↔base 变换方向', '只调大体素尺寸'],
      answer: [0, 1, 2, 3, 4],
      explain: '尺度、深度定义、内参、索引和外参都会造成系统性几何错误；体素尺寸只能改变采样密度。',
      multiple: true
    }
  ]
}
