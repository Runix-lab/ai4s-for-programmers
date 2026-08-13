# -*- coding: utf-8 -*-
"""Page registry and site-wide SEO metadata.

Every page is one dict. `file` names the fragment in content/, `slug` is the URL
path, and everything else feeds the <head> and the structured-data graph.

Titles are written to survive SERP truncation (CJK counts double — see the width
check in build.py), and descriptions are written to be read by a human deciding
whether to click, not stuffed with keywords.
"""

ORIGIN = "https://ai4s.runixcloud.io"
SITE_NAME = "AI4S for Programmers"
ORG = "Runix"
ORG_URL = "https://runixcloud.io"
REPO = "https://github.com/Runix-lab/ai4s-for-programmers"
PUBLISHED = "2026-08-13"
UPDATED = "2026-08-13"

COURSE_NAME = "抗体数据 × AI for Science · 程序员两天速成营"
TEACHES = [
    "蛋白质序列与抗体结构的数据表示",
    "抗原、表位、互补位与亲和力 KD 的读法",
    "IMGT / Kabat / Chothia 三套抗体编号体系的差异",
    "生物数据的实体归一与交叉源验证",
    "AI for Science 中数据质量的证伪方法",
]

NAV = [
    ("study", "速成营"),
    ("study/syllabus", "大纲"),
    ("study/labs", "实验"),
    ("study/quiz", "检验"),
    ("study/glossary", "术语表"),
    ("study/resources", "资源"),
    ("en", "EN"),
]


def _lesson(slug, file, crumb, h1, title, desc, keywords, duration, teaches,
            eyebrow, dek, prev, nxt, og="lesson", og_headline=None, faq=None):
    return dict(
        slug=f"study/{slug}", file=file, crumb=crumb, h1=h1, title=title, desc=desc,
        keywords=keywords, duration=duration, teaches=teaches, eyebrow=eyebrow, dek=dek,
        parent=1, prev=prev, next=nxt, schema="Lesson", priority=0.85, quiz=True,
        og=og, og_headline=og_headline or crumb, og_kicker="AI4S for Programmers",
        faq=faq,
    )


PAGES = [
    # ---------------------------------------------------------------- 0 home
    dict(
        slug="study", file="home", crumb="两天速成营",
        h1="程序员两天学会看懂<br>AI for Science 的数据",
        title="AI4S for Programmers · 程序员的 AI for Science 入门",
        desc="零生物背景的程序员两天入门 AI for Science：所有生物概念映射到你已经懂的编程概念，配 6 个可运行实验和 35 道检验题。免费开源。",
        keywords=["AI for Science 入门", "AI4S", "程序员 转 AI 制药", "抗体 数据",
                  "生物信息学 入门", "AI4S 教程"],
        eyebrow="免费 · 开源 · 无需生物背景",
        dek="不讲生物学，讲<b>数据</b>。抗体是 4 条字符串组成的对象，靶点归一化是外键解析，"
            "数据质检是写断言——这个领域的每个问题，你都在软件工程里见过。",
        badges=["<b>2 天 · 8 节</b>", "<b>6 个</b>可运行实验", "<b>35 道</b>检验题",
                "前置：<b>会写 Python</b>", "生物基础：<b>零</b>"],
        parent=None, prev=None, next=1, schema="Course", priority=1.0,
        changefreq="weekly", og="default", og_type="website",
        og_headline="程序员两天学会看懂 AI for Science 的数据",
        og_kicker="免费 · 开源 · 无需生物背景",
        lang_alt=14,
        faq=[
            ("什么是 AI for Science（AI4S）？",
             "AI for Science 指用机器学习方法解决自然科学问题，例如从蛋白质序列预测三维结构、"
             "预测分子间结合强度、或从头设计蛋白质。它和通用 AI 最大的区别是数据来自真实实验，"
             "获取成本极高、总量极小，所以数据质量往往比模型选择更决定成败。"),
            ("没有生物学基础的程序员能学吗？",
             "可以。这门课的设计前提就是零生物背景。所有生物概念都先映射到一个你已经熟悉的编程概念"
             "——蛋白质序列是字符串、UniProt 登录号是主键、抗体编号体系是并存的 schema 版本"
             "——再讲它在生物上的含义。只要会写 Python 就能跟完。"),
            ("学完能做什么？",
             "能读懂一份抗原-抗体数据集的每一列、能判断一份数据是否可信、"
             "能在 5 分钟内对这类项目做出初步判断并问出关键问题。"
             "它的目标是判断力，不是让你自己去建模。"),
            ("课程要花多少钱？",
             "免费。全部内容和 6 个实验的源码都在 GitHub 上以 CC BY-SA 4.0 / MIT 开放。"),
        ],
    ),

    # ---------------------------------------------------------------- 1 course
    dict(
        slug="study/syllabus", file="course", crumb="课程总览",
        h1="课程总览：两天 8 节课",
        title="课程总览 · 抗体数据与 AI4S 两天速成营",
        desc="两天 8 节课的完整大纲：Day 1 从零到看懂数据，Day 2 从数据到判断力。含每节的时长、目标、配套实验与检验题，以及时间不够时的精简路径。",
        keywords=["AI4S 课程", "抗体数据 教程", "AI for Science 学习路径"],
        eyebrow="COURSE",
        dek="Day 1 建立概念骨架，Day 2 建立判断力。<b>时间不够就只做 S7 和 S8</b>——"
            "那两节是判断力的来源，前面的概念可以随时回头查。",
        parent=None, prev=None, next=2, schema="Course", priority=0.9,
        og="default", og_headline="两天 8 节课 · 完整大纲",
        og_kicker="AI4S for Programmers",
    ),

    # ---------------------------------------------------------------- 2..9 lessons
    _lesson(
        "protein-as-string", "s1", "S1 · 分子的数据类型",
        "分子的「数据类型」：蛋白质就是字符串",
        "蛋白质就是字符串 · 抗体的数据结构入门",
        "把抗体当数据结构理解：蛋白质是 20 个字母的字符串，抗体是 4 条链组成的复合对象，可变区是实例字段，CDR 是决定行为的关键子串。",
        ["蛋白质 序列", "抗体 结构 VH VL", "CDR 是什么", "纳米抗体 VHH", "氨基酸 单字母"],
        "PT90M",
        ["蛋白质序列的一维表示", "抗体的重链轻链组成", "可变区与恒定区的区别", "CDR 与 CDRH3 的作用"],
        "DAY 1 · S1 · 上午 90 分钟",
        "把抗体当成一个<b>数据结构</b>来理解，而不是当成生物。",
        prev=1, nxt=3,
        faq=[
            ("CDR 是什么？",
             "CDR（互补决定区）是抗体可变区里真正伸出去接触目标的 6 个环：重链 3 个、轻链 3 个。"
             "它们只占序列很小一部分，却决定这个抗体能抓住谁。其中 CDRH3 最长、变化最大，"
             "是特异性的主要来源，因此去重和聚类通常以它为轴。"),
            ("可变区和恒定区有什么区别？",
             "可变区（VH/VL）位于 Y 形抗体的两个尖端，每个抗体都不同，携带全部区分信息；"
             "恒定区（CH/CL）是下半部分，同类抗体几乎完全一样。做数据时通常切掉恒定区只留可变区，"
             "因为恒定区对区分实例没有信息量。"),
            ("什么是纳米抗体（VHH）？",
             "VHH / 纳米抗体是一类只有重链、没有轻链的天然抗体，来自骆驼科动物（羊驼、骆驼、美洲驼）。"
             "鲨鱼也有单域抗体，但那一类叫 VNAR、来自 IgNAR，与 VHH 是独立演化出来的两套东西，"
             "「VHH 来自羊驼和鲨鱼」是常见的错误说法。写代码判断「有没有轻链」时必须考虑这一整类。"),
        ],
    ),
    _lesson(
        "binding-and-affinity", "s2", "S2 · 结合与亲和力",
        "「结合」就是两个对象的匹配",
        "抗原、表位、互补位与 KD 亲和力怎么读",
        "抗原 ≠ 表位：抗原是整个分子，表位是真正被抓住的那几个残基，互补位是抗体这侧。附 KD 数量级速查与 SPR/BLI/ELISA 可信度对比。",
        ["表位 互补位 区别", "抗原 表位 区别", "KD 解离常数", "亲和力 nM pM",
         "线性表位 构象表位", "SPR BLI ELISA"],
        "PT60M",
        ["抗原、表位、互补位的区别", "线性表位与构象表位", "KD 的数量级读法", "三种亲和力测量方法的可信度"],
        "DAY 1 · S2 · 上午 60 分钟",
        "这一节讲清「抓住」这件事怎么发生、怎么<b>量化</b>。",
        prev=2, nxt=4,
        faq=[
            ("抗原和表位有什么区别？",
             "抗原是被抓住的整个分子（例如「PD-1 蛋白」），表位是这个抗原上真正被抗体接触到的那几个残基。"
             "用编程类比：抗原是整个对象，表位是这个对象实际暴露出来的那个接口。"
             "互补位则是抗体一侧发生接触的残基，位于 CDR 上。"),
            ("KD 越大还是越小代表结合越强？",
             "越小越强。KD 是解离常数，单位是摩尔（M）。10⁻⁶（μM）算弱，治疗性抗体大致落在低 nM（10⁻⁹）"
             "到 pM（10⁻¹²）这个区间。读它的方式和读延迟指标一样：只看数量级，越小越好。"
             "关系式是 KD = koff / kon。看到具体数字要先确认它是用什么方法测的——"
             "ELISA 给的 EC50/IC50 是表观值，不能和 SPR 的 KD 放进同一列。"),
            ("线性表位和构象表位有什么区别？",
             "线性表位是连续的一段氨基酸，可以直接当字符串比对；构象表位由序列上相距很远、"
             "折叠后才凑到一起的残基组成，只能从三维结构算出来，而且占大多数。"
             "所以「从一维序列预测表位」这句话对构象表位并不成立。"),
        ],
    ),
    _lesson(
        "formats-and-ids", "s3", "S3 · 格式与标识符",
        "数据格式与标识符：你的主场",
        "IMGT / Kabat / Chothia 区别与 UniProt 登录号",
        "FASTA、PDB、UniProt 登录号，以及三套抗体编号体系为什么会切出不同的 CDR 边界。附一条真实序列在三套体系下的对照，以及别名冲突的翻车案例。",
        ["IMGT Kabat Chothia 区别", "抗体编号 体系", "UniProt 登录号", "FASTA 格式",
         "PDB 结构", "基因 别名 冲突"],
        "PT90M",
        ["FASTA 与 PDB 格式", "IMGT/Kabat/Chothia 三套编号体系的差异", "UniProt 登录号作为主键", "蛋白别名冲突的风险"],
        "DAY 1 · S3 · 下午 90 分钟",
        "这一节全是你的主场——<b>格式、schema、主键、别名冲突</b>。",
        prev=3, nxt=5,
        og="imgt", og_headline="IMGT / Kabat / Chothia 到底差在哪",
        faq=[
            ("IMGT、Kabat、Chothia 有什么区别？",
             "它们是三套并存的抗体残基编号体系，作用都是让不同长度的抗体可变区能按「结构位置」对齐比较。"
             "区别在于 CDR 边界的划法不同：Kabat（1970 年代起）按序列变异度划，Chothia（1987）按结构环划，"
             "IMGT（1997）用统一的结构域编号、是目前最主流的一套。"
             "但要注意两点：一是常用的编号体系不止三套，还有 Martin、AbM、Contact、AHo、North 等；"
             "二是 Kabat 与 Chothia 对 CDR-H3 的定义其实是相同的，它们的差别体现在 CDR-H1 和 CDR-L1 上。"
             "一份数据集只给一套编号却不说明是哪套，等同于给了日期字段却不说时区。"),
            ("为什么靶点必须归一到 UniProt 登录号？",
             "因为蛋白名字极不稳定：PD-1 又叫 PDCD1、CD279、programmed cell death protein 1，"
             "而且不同基因之间的别名会互相撞车。UniProt 登录号（如人 PD-1 是 Q15116）全球唯一且稳定，"
             "是这个领域唯一可靠的主键。"),
        ],
    ),
    _lesson(
        "hands-on-day1", "s4", "S4 · 动手（Day 1）",
        "动手：把今天学的跑一遍",
        "动手实验：打开一条真实抗体记录并做数据体检",
        "Day 1 的两个实验：打开一条真实抗体记录逐字段对照概念，然后用 SELECT COUNT(*) GROUP BY 的思路给整份数据做一次体检。",
        ["抗体 数据集 字段", "生物数据 体检", "数据质量 检查"],
        "PT60M",
        ["读取真实抗体数据记录", "数据集的基数与填充率体检"],
        "DAY 1 · S4 · 下午 60 分钟",
        "所有实验都在<b>真实数据</b>上跑，不是玩具样例。",
        prev=4, nxt=6,
    ),
    _lesson(
        "what-ai-does", "s5", "S5 · AI 在做什么",
        "AI for Science 在这里做什么",
        "AlphaFold 解决了什么、没解决什么",
        "AlphaFold2 解决单体折叠，AlphaFold-Multimer 和 AlphaFold 3 扩展到复合物，但抗体-抗原仍是最弱的一类。用函数签名理解 AI4S 的三类任务，以及为什么瓶颈是数据不是模型。",
        ["AlphaFold 原理", "AlphaFold 局限", "蛋白质结构预测", "抗体 设计 AI",
         "AI 制药 数据 瓶颈"],
        "PT60M",
        ["AlphaFold 的贡献与边界", "结构预测/亲和力预测/从头设计三类任务", "为什么数据是瓶颈"],
        "DAY 2 · S5 · 上午 60 分钟",
        "不讲模型细节，只讲<b>有哪几类任务、各自的输入输出和现状</b>。",
        prev=5, nxt=7,
        og="alphafold", og_headline="AlphaFold 解决了什么，没解决什么",
        faq=[
            ("AlphaFold 解决了什么问题？",
             "AlphaFold 让「从氨基酸序列预测单体蛋白的三维结构」在大多数情况下达到接近实验的精度，"
             "把原本需要数月到数年的实验测定压缩到分钟级。这是结构生物学的分水岭事件。"),
            ("为什么抗体设计还是很难？",
             "抗体-抗原结合属于蛋白-蛋白相互作用，比单体折叠难得多；而且 CDRH3 由基因重组随机拼接产生，"
             "缺乏可借鉴的进化同源信息。同时可用于训练的真实配对数据极少——结构复合物只有数千个，"
             "定量亲和力数据只有数百条量级。所以这个方向至今高度依赖真实实验数据。"),
        ],
    ),
    _lesson(
        "data-engineering", "s6", "S6 · 数据工程",
        "数据工程的真实形态",
        "生物数据工程的四层能力与五个真实的坑",
        "要建的不是爬虫，是四层能力：多源接入、实体归一、证据判定、信息抽取。附五个真实踩过的坑，每个都有你熟悉的软件工程对应物。",
        ["生物 数据工程", "实体归一 entity resolution", "数据血缘", "ETL 生物数据",
         "数据 证据分级"],
        "PT60M",
        ["多源接入与实体归一", "证据分级与数据血缘", "关键词共现噪声与别名假阳性"],
        "DAY 2 · S6 · 上午 60 分钟",
        "这一节全部用<b>软件工程的语言</b>讲。",
        prev=6, nxt=8,
    ),
    _lesson(
        "falsification", "s7", "S7 · 质量与证伪",
        "质量与证伪：亲手复现那些坑",
        "交叉源验证：为什么自证等于循环论证",
        "全课最核心的一节。四个实验让你亲手把 bug 跑出来：词边界假阳性、别名劫持、从三维结构实算表位、断言式质检，以及验证方法本身也要被验证。",
        ["交叉源验证", "数据 证伪", "断言式 质检", "表位 计算", "假阳性 词边界",
         "数据质量 验证"],
        "PT90M",
        ["交叉源验证方法", "子串匹配假阳性的成因", "从三维结构计算表位", "断言式数据质检"],
        "DAY 2 · S7 · 下午 90 分钟",
        "这一节是全课的核心。四个实验，<b>每个都让你亲手把 bug 跑出来</b>。",
        prev=7, nxt=9,
        og="falsify", og_headline="用产出结果的源去检查结果 = 循环论证",
        faq=[
            ("什么是交叉源验证？",
             "用一个独立的权威数据源去复核另一个源产出的结果，两边一致才算通过。"
             "关键在于「独立」：如果用产出结果的同一个源去检查结果，那是循环论证，"
             "等同于写测试时用被测代码自己的逻辑去断言。"),
            ("为什么数据全部通过质检反而可疑？",
             "真实数据一定有已知瑕疵——测序模糊码、部分序列、来源缺失。"
             "一份 QC 标记全是 OK 的数据集，更可能说明质检做得不够细，而不是数据完美。"
             "拿不出缺陷清单的供应商值得警惕。"),
        ],
    ),
    _lesson(
        "judgment", "s8", "S8 · 判定与商业",
        "判定与商业：可以直接用的清单",
        "怎么判断一份科学数据集值不值得买",
        "三维验收标准、十个必问问题、五分钟自助抽查法和红旗清单，可以直接抄进合同或尽调清单。附一条纯靠算术就能证伪的红旗：表位数量不可能超过公开复合物结构总数。",
        ["数据集 验收", "科学数据 采购", "数据 尽调", "供应商 评估", "数据 可溯源"],
        "PT60M",
        ["数量/可溯源率/配对准确率三维验收", "采购时的十个必问问题", "五分钟自助抽查法"],
        "DAY 2 · S8 · 下午 60 分钟",
        "可以直接拿去用的清单。<b>抄走就行。</b>",
        prev=8, nxt=10,
        og="judge", og_headline="判断一份科学数据集的十个必问问题",
        faq=[
            ("怎么判断一份抗体数据集的质量？",
             "看三个维度而不是只看条数：① 带结合上下文的配对条数；"
             "② 可溯源率——随机抽 100 条，链接必须能打开且内容确实佐证靶点关系，要求 100%；"
             "③ 配对准确率——随机抽 200 条由领域专家盲评。只按条数验收，"
             "供应商用没有抗原配对信息的序列库就能轻松凑数。"),
        ],
    ),

    # ---------------------------------------------------------------- 10 labs
    dict(
        slug="study/labs", file="labs", crumb="动手实验",
        h1="6 个动手实验",
        title="6 个可运行实验 · 亲手复现真实数据 bug",
        desc="六个 Python 实验：读一条真实抗体记录、数据体检、复现子串匹配假阳性、交叉源验证、从三维结构算表位、断言式质检。附完整源码。",
        keywords=["生物数据 Python 实验", "抗体 数据 分析 代码", "gemmi 表位 计算",
                  "HGNC UniProt API", "数据质检 断言"],
        eyebrow="LABS",
        dek="每个实验都是一个可以直接跑的 Python 脚本，<b>不是伪代码</b>。"
            "四个离线可跑，两个需要联网（真的去请求 HGNC / UniProt）。",
        parent=None, prev=9, next=11, schema="Article", priority=0.9,
        og="labs", og_headline="6 个可运行实验 · 亲手复现真实 bug",
    ),

    # ---------------------------------------------------------------- 11 quiz
    dict(
        slug="study/quiz", file="quiz", crumb="在线检验",
        h1="35 道检验题",
        title="35 道在线检验题 · 抗体数据与 AI4S",
        desc="Day 1 检验 15 题 + 结业考试 20 题，全部选择题、即时判分、每题都附解析说明为什么。用来确认你真的掌握了，而不只是读过了——做错的题回对应小节重看一遍。",
        keywords=["AI4S 测验", "抗体 知识 测试", "生物信息学 题目"],
        eyebrow="EXAM",
        dek="做题比读文更重要。<b>做错的题回对应小节重看一遍</b>，这是这套材料唯一要求你做的事。",
        parent=None, prev=10, next=None, schema="Article", priority=0.7, quiz=True,
        og="quiz", og_headline="35 道题 · 检验你是真懂还是读过",
    ),

    # ---------------------------------------------------------------- 12 glossary
    dict(
        slug="study/glossary", file="glossary", crumb="术语表",
        h1="术语表：生物词 → 编程词",
        title="生物术语对照表 · 给程序员的速查",
        desc="45 个高频术语的双向速查：每个生物概念配一句人话解释和一个编程类比。抗体、表位、KD、CDR、IMGT、UniProt、FASTA、PDB 全覆盖。",
        keywords=["生物 术语 对照", "抗体 名词解释", "生物信息学 术语表",
                  "表位 是什么", "互补位 是什么", "CDRH3"],
        eyebrow="GLOSSARY",
        dek="遇到不认识的词直接 <kbd>Ctrl</kbd>+<kbd>F</kbd>。"
            "每一条都给<b>一句人话</b>和<b>一个编程类比</b>。",
        parent=None, prev=None, next=None, schema="Article", priority=0.8,
        changefreq="monthly", og="glossary",
        og_headline="45 个术语 · 生物词直译成编程词",
    ),

    # ---------------------------------------------------------------- 13 resources
    dict(
        slug="study/resources", file="resources", crumb="视频与资源",
        h1="视频与资源清单",
        title="AI4S 入门视频与资料清单 · 逐条实测",
        desc="精选视频教程与 UniProt / HGNC / RCSB PDB / SAbDab 等权威数据库入口，中英文都有，标题时长逐条核对。按「只看一条该看哪条」排序，不贪多、不堆量。",
        keywords=["AlphaFold 视频", "抗体 科普 视频", "AI4S 学习资料",
                  "SAbDab", "UniProt", "PDB 数据库"],
        eyebrow="RESOURCES",
        dek="按<b>投入产出比</b>排序，不是按数量堆。如果只看一条，看 Veritasium 那条 AlphaFold。",
        parent=None, prev=None, next=None, schema="Article", priority=0.7,
        og="resources", og_headline="24 条视频与数据库 · 逐条实测存活",
    ),

    # ---------------------------------------------------------------- 14 english
    dict(
        slug="en", file="en", crumb="English", lang="en",
        h1="AI for Science, explained for programmers",
        title="AI for Science for Programmers · Free Course",
        desc="A free two-day course that teaches AI for Science to programmers with zero biology background, by mapping every biological concept onto one you already know.",
        keywords=["AI for Science course", "AI4S for programmers",
                  "antibody data engineering", "IMGT vs Kabat vs Chothia",
                  "epitope vs paratope", "protein data for software engineers"],
        eyebrow="FREE · OPEN SOURCE · NO BIOLOGY REQUIRED",
        dek="Not a biology course. A <b>data</b> course that happens to be about molecules — "
            "an antibody is four strings, target normalisation is foreign-key resolution, "
            "and QC is just writing assertions.",
        parent=None, prev=None, next=None, schema="Course", priority=0.8,
        og="en", og_type="website", og_locale="en_US", lang_alt=0,
        og_headline="AI for Science, explained for programmers",
        og_kicker="Free · Open source · No biology required",
        faq=[
            ("What is AI for Science (AI4S)?",
             "AI for Science means applying machine learning to natural-science problems — "
             "predicting a protein's 3D structure from its sequence, predicting binding strength "
             "between molecules, or designing proteins from scratch. Unlike general-purpose AI, "
             "the data comes from real experiments: expensive to produce and tiny in volume, "
             "which is why data quality usually matters more than model choice."),
            ("Do I need a biology background?",
             "No. The course assumes zero biology. Every concept is introduced through a "
             "programming analogy you already understand — protein sequences are strings, "
             "UniProt accessions are primary keys, antibody numbering schemes are competing "
             "schema versions — before any biology is explained. Python literacy is the only "
             "prerequisite."),
        ],
    ),
    # ------------------------------------------------- 15 site root (AI4S line)
    dict(
        slug="", file="ai4s", crumb="首页",
        h1="AI for Science，<br>讲给程序员听",
        title="AI4S · AI for Science 给程序员的入门",
        desc="AI for Science 里最难的部分不是科学，是数据工程——而那正是程序员已经会的事。免费开源的两天速成营，零生物背景可学，配 6 个可运行实验。",
        keywords=["AI for Science", "AI4S", "AI4S 是什么", "AI for Science 入门",
                  "程序员 AI 制药", "科学数据 工程", "AI4S 教程"],
        eyebrow="RUNIX · AI FOR SCIENCE",
        dek="这个领域最稀缺的不是模型能力，是<b>判断一份科学数据是真是假的能力</b>。"
            "而做这件事需要的技能，你在软件工程里已经练了很多年。",
        badges=["<b>免费</b> · 开源", "无需生物背景", "<b>6 个</b>可运行实验",
                "内容 <b>CC BY-SA</b> · 代码 <b>MIT</b>"],
        parent=None, prev=None, next=0, schema="Course", priority=1.0,
        changefreq="weekly", og="default", og_type="website",
        og_headline="AI for Science，讲给程序员听",
        og_kicker="Runix · 免费开源",
        faq=[
            ("AI4S 和普通的机器学习有什么区别？",
             "方法上没有本质区别，数据条件上有天壤之别。通用 AI 的数据近乎无限、标注便宜；"
             "AI4S 的每条数据都来自真实实验，成本极高、总量极小，而且经常带有不容易发现的"
             "系统性错误。所以在 AI4S 里，数据的收集、归一和验证通常比模型架构更决定成败。"),
            ("没有科学背景能进入 AI for Science 领域吗？",
             "能。这个领域最缺的岗位之一是数据工程——把多个来源的科学数据接进来、归一到稳定主键、"
             "给每条记录标明证据强度、写质检断言。这些工作的核心技能是软件工程，不是实验科学。"),
            ("从哪里开始学 AI for Science？",
             "从判断力开始，而不是从建模开始。先能读懂一份科学数据集的每一列、"
             "能判断它是否可信，再谈模型。本站的两天速成营就是按这个前提设计的，"
             "全部免费开源，零生物背景可学。"),
        ],
    ),
]

NOT_FOUND = dict(
    slug="404", file="404", crumb="页面不存在", h1="这个页面不存在",
    title="页面不存在 · AI4S for Programmers",
    desc="你访问的页面不存在或已经移动。可以从课程总览重新开始，或者用术语表直接查一个词。",
    parent=None, prev=None, next=None, noindex=True, og="default",
    dek="链接可能过期了。从<a href=\"/study/\">两天速成营</a>重新开始，"
        "或者直接去<a href=\"/study/glossary/\">术语表</a>查词。",
)
