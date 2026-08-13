/* 35-question bank + renderer.
 *
 * Each question carries a `sec` tag naming the lesson it belongs to, so the same
 * bank drives both the full exam at /quiz/ and the short self-test at the end of
 * each lesson. Mount points look like:
 *
 *   <div class="quiz" data-bank="d1" data-sec="s1">   -> just S1's questions
 *   <div class="quiz" data-bank="d1">                 -> the whole Day 1 exam
 */
(function () {
  'use strict';

  var BANK = {
    d1: [
      { sec: 's1', q: '蛋白质序列本质上是什么数据类型？', o: ['浮点数数组', '20 个字母组成的字符串', '三维坐标矩阵'], a: 1,
        e: '20 种氨基酸各用一个大写字母表示。三维坐标是「结构」，是序列折叠之后的产物。' },
      { sec: 's1', q: '最常见的 IgG 抗体由几条链组成？', o: ['1 条', '2 重链 + 2 轻链', '4 条等长链'], a: 1,
        e: '重链长、轻链短，拼成 Y 形。注意「2+2」说的是 IgG 单体——分泌型 IgM 是五聚体、分泌型 IgA 常是二聚体。另一个特例是单域抗体（VHH/VNAR），只有重链没有轻链。' },
      { sec: 's1', q: '做数据时为什么要切掉恒定区？', o: ['恒定区太长占空间', '恒定区对同类抗体几乎相同，无区分信息', '恒定区数据质量差'], a: 1,
        e: '类比：它相当于类的公共部分，对区分实例毫无信息量，留着是噪声。' },
      { sec: 's1', q: 'CDR 一共几个？哪个最关键？', o: ['4 个，CDRL1 最关键', '6 个，CDRH3 最关键', '8 个，都一样重要'], a: 1,
        e: '重链 3 个 + 轻链 3 个。CDRH3 最长、变化最大，由基因重组随机拼接产生，是特异性主要来源。' },
      { sec: 's1', q: 'VHH（纳米抗体）的特点是？', o: ['比普通抗体大', '只有重链没有轻链', '不能结合抗原'], a: 1,
        e: '个头小好改造，是热门方向。来源要说准：VHH 来自骆驼科动物（羊驼、骆驼、美洲驼）；鲨鱼的单域抗体叫 VNAR、来自 IgNAR，是独立演化的另一套，不叫 VHH。写代码判断「有无轻链」时要考虑这一整类。' },

      { sec: 's2', q: '抗原和表位的关系是？', o: ['同一个东西', '表位是抗原上真正被抓住的那一小块', '抗原是表位的一部分'], a: 1,
        e: '抗原是整个分子，表位是其上真正被抓的几个残基。抗体那一侧对应的叫互补位。' },
      { sec: 's2', q: '构象表位为什么难处理？', o: ['序列上不连续，只有折叠后才凑到一起', '太长了', '只在低温下存在'], a: 0,
        e: '所以必须有三维结构才能算，不能用字符串匹配找。而且构象表位占大多数。' },
      { sec: 's2', q: 'KD = 1×10⁻¹² M 和 KD = 1×10⁻⁷ M，哪个结合更强？', o: ['10⁻⁷', '10⁻¹²', '一样'], a: 1,
        e: 'KD 越小越强。10⁻¹² 是皮摩尔级，比 10⁻⁷ 强 5 个数量级。' },
      { sec: 's2', q: '亲和力场景下，ELISA 给出的是什么？', o: ['真正的 KD 与结合动力学', 'EC50/IC50 这类表观值', '三维结构'], a: 1,
        e: 'ELISA 可以定量测浓度，但在亲和力方向只给 EC50/IC50 表观值，受实验条件影响、跨实验室不可直接比较，不能和 SPR 的 KD 放进同一列。SPR 和 BLI 都是实时动力学方法，能给 ka/kd/KD。' },

      { sec: 's3', q: 'IMGT / Kabat / Chothia 是什么？', o: ['三个数据库', '三套序列编号体系', '三种实验方法'], a: 1,
        e: '相当于并存的多套 schema 版本（常用的其实不止三套，还有 Martin/AbM/Contact/AHo/North 等）。同一条序列在不同体系下切出的 CDR 边界不同——但注意 Kabat 与 Chothia 对 CDR-H3 的定义是相同的，差别在 H1/L1。' },
      { sec: 's3', q: '为什么靶点必须归一到 UniProt 登录号？', o: ['登录号更短', '名字有大量别名且会互相冲突', '这是行业规定'], a: 1,
        e: 'PD-1=PDCD1=CD279 是同一个；而 CCR4 同时被记为另一个基因(NOCT)的别名。只有登录号唯一稳定。' },
      { sec: 's3', q: 'FASTA 格式里 &gt; 开头那一行是？', o: ['序列本身', '描述行（defline）', '校验和'], a: 1,
        e: '一行描述 + 一段序列 payload，就这么简单。' },
      { sec: 's3', q: '专利来源的抗体序列，描述行通常缺什么？', o: ['序列本身', '专利号', '靶点标签'], a: 2,
        e: '通常只写「来自专利 US XXXXXXX 的第 N 条序列」。靶点埋在权利要求书正文里，这是全行业的瓶颈。' },
      { sec: 's3', q: 'PDB 结构里，链 ID 字母（A/H/L/P…）代表什么？', o: ['H 一定是重链、L 一定是轻链', '没有语义，由沉积者自定', '按分子量从大到小排'], a: 1,
        e: '链 ID 完全由结构的沉积者自己起名。反例就是本课常用的 5B8C：它的轻链是 A/D/G/J、重链是 B/E/H/K、抗原是 C/F/I/L——按「H=重链」去解析会把轻链当抗原。数据表里的 Hchain/Lchain/Antigen_chain 是策展库替你判定过的结果，不是从 PDB 文件直接读出来的。' },
      { sec: 's3', q: '为什么结构确证的配对被定为最高证据等级？', o: ['结构数据文件更大', '两个分子在坐标里真的贴在一起，是可见的物理事实', '结构数据更新更快'], a: 1,
        e: '其它证据都是「有人说」，结构是「看得见」。所以定为 L1、匹配度 0.98。' }
    ],
    d2: [
      { sec: 's5', q: 'AlphaFold 解决了什么，没解决什么？', o: ['解决了所有蛋白质问题', '单体折叠已基本可用，抗体-抗原复合物仍是公认难点', '只解决了小分子对接'], a: 1,
        e: '复合物预测这些年有明显进展（AlphaFold-Multimer、AlphaFold 3），但抗体-抗原界面仍是公开评测中成功率最低的一类：CDRH3 由随机重组产生，没有进化同源信息可借鉴。这是本领域仍依赖真实数据的根本原因。' },
      { sec: 's5', q: '「从头设计抗体」这个任务最需要什么数据？', o: ['大量抗体序列', '大量「靶点↔抗体序列」配对', '大量小分子结构'], a: 1,
        e: '要学的是 target → antibody 的映射，必须有成对样本。这就是「binding context」的含义。' },
      { sec: 's5', q: 'repertoire（免疫组库）数据对从头设计的最大问题？', o: ['数据量小', '没有抗原配对信息', '序列质量差'], a: 1,
        e: '十亿级序列但不知道各自抓什么。用它凑条数形式合规，对监督训练无用。' },

      { sec: 's6', q: '数据工程四层里，护城河在哪一层？', o: ['多源接入层', '实体归一层', '证据判定层'], a: 2,
        e: '大多数人只做接入层。区分供应商的是「这条配对凭什么成立、强度多少、原文在哪句」。' },
      { sec: 's6', q: 'HER2 的别名 neu 造成 137 条假阳性，根因是？', o: ['数据源有错', '正则没加词边界', '编码问题'], a: 1,
        e: '裸子串匹配命中了 NEURAMINIDASE、NEUTRALIZING 等。注意必须加「两侧」边界断言：只加左侧的 (?<![A-Za-z0-9]) 挡不住 NEURAMINIDASE，因为 NEU 正好在词首。用 \\bneu\\b 或两侧都加。' },
      { sec: 's6', q: 'PD-1 的全名是 PD-L1 全名的前缀，光加词边界能解决吗？', o: ['能', '不能，还需要最长匹配消歧', '不影响'], a: 1,
        e: '两个都会命中。必须做 containment disambiguation：同一段文本里长匹配压制短匹配。' },
      { sec: 's6', q: '接入一个新的公开亲和力库，净增 0 条。这说明？', o: ['接入失败', '公开数据高度重叠，堆源头解决不了稀缺', '该库质量差'], a: 1,
        e: '这是一个有价值的负面结论：它排除了「多接公开库」这条路，说明只能走全文抽取。' },
      { sec: 's6', q: '文献说表位是 S541，但参考序列第 541 位不是丝氨酸。最可能的原因？', o: ['文献写错了', '标注来自另一个毒株/分离株，坐标基准不同', '序列数据损坏'], a: 1,
        e: 'HIV Env、流感 HA 这类超变蛋白尤其明显。配对本身没错，是编号不索引这条参考序列。必须逐条标记。' },

      { sec: 's7', q: '「用 UniProt 归一化，再用 UniProt 检查」这个做法的问题是？', o: ['太慢', '是循环论证/自证', 'API 有限流'], a: 1,
        e: '必须用独立权威源（如 HGNC）复核，两边一致才算过。这和写测试不能用被测代码自己的逻辑断言是一回事。' },
      { sec: 's7', q: 'CCR4 被归错到 NOCT，根因是？', o: ['拼写错误', 'UniProt 把 CCR4 记为 NOCT 的一个基因名同义词', '两者确实是同一个基因'], a: 1,
        e: '别名冲突：CCR4 是 UniProt 里 NOCT(Q9UK39) 的一个 gene name synonym，而真正的 CCR4 是趋化因子受体、一个真实药物靶点。注意 HGNC 记录的 NOCT 旧符号是 CCRN4L 而非 CCR4——所以「拉黑 HGNC 废弃符号」这个防御措施拦不住它。这类错误从数据表面完全看不出来。' },
      { sec: 's7', q: '从三维结构算表位，本质上是什么操作？', o: ['字符串匹配', '空间近邻查询（找距离小于阈值的原子对）', '机器学习预测'], a: 1,
        e: '把两侧原子丢进 KD 树找接触，常用重原子间距 4~5 Å 作为阈值。所以叫「实算」而不是「抄」——但阈值是约定，必须随数据一起写清楚。' },
      { sec: 's7', q: '数据质检的正确形态是？', o: ['出一份统计报告', '写一组必须成立的断言，挂了打印具体哪些行', '人工抽样目测'], a: 1,
        e: '和写 pytest 一样。而且断言语义应该是「不许有未披露的缺陷」，不是「不许有缺陷」。' },
      { sec: 's7', q: '一份数据的 QC_flags 全是 OK，说明？', o: ['质量极高', '可能没认真做质控或把问题藏起来了', '来源单一'], a: 1,
        e: '真实策展数据一定有已知瑕疵（氨基酸模糊码、部分沉积链等）。全 OK 反而可疑。' },
      { sec: 's7', q: '检查溯源链接时收到 HTTP 403，应该判定为？', o: ['链接已失效', '可能是反爬，不等于链接坏', '服务器宕机'], a: 1,
        e: '出版社常返回 403/429。断言写成「必须全部 200」会产生假阴性。验证方法本身也需要被验证。' },

      { sec: 's8', q: '三维验收里，哪一条最能区分供应商？', o: ['数量达标', '可溯源率 + 专家盲评准确率', '交付格式规范'], a: 1,
        e: '数量最容易造假（用 repertoire 凑数）。可溯源率和盲评准确率才是真门槛。' },
      { sec: 's8', q: '供应商报「结合数据 8,000 条」，你首先问什么？', o: ['能不能更多', '其中定量 KD 有多少条', '数据是哪年的'], a: 1,
        e: '「结合数据」可以混入大量定性记录。必须按证据强度分列——真实案例里 8,622 行中定量 KD 只有 49 行。' },
      { sec: 's8', q: '去重应该按什么做？', o: ['按抗体名字', '按序列内容', '按数据来源'], a: 1,
        e: '同一抗体在不同库里名字可能完全不同（专利名/INN名/clone名/PDB链），只有序列是稳定标识。' },
      { sec: 's8', q: '表位数量远超 PDB 里抗体-抗原复合物总数，说明？', o: ['数据很全面', '数据可能是抄的或编的', '用了更好的算法'], a: 1,
        e: '结构实算的表位上限受限于复合物结构数量。超过这个天花板就该追问来源。' },
      { sec: 's8', q: '「专利全文抽取」主要解决什么问题？', o: ['靶点数量', '给已有的大量专利序列补上靶点标签', '降低数据成本'], a: 1,
        e: '专利里只有少数在标题写了靶点。抽取能把海量专利序列变成有标签的配对——是配对数的解药，不是靶点数的。' },
      { sec: 's8', q: '这个领域的核心壁垒是什么？', o: ['爬虫技术', '模型规模', '能证明抓对了多少'], a: 2,
        e: '同一批原始数据，朴素方法能「做」出六万多条配对，其中八成经不起推敲。壁垒在证据判定，不在数据采集。' }
    ]
  };

  var VERDICT = {
    d1: [[0.80, '基础扎实，可以进 Day 2。'], [0.67, '过关。错的题回对应小节再看一遍。'], [0, '建议回头重看 S1–S3，别急着往后。']],
    d2: [[0.80, '你已经可以独立判断这类项目了。'], [0.65, '过关。薄弱的地方回 S6/S7 补一下。'], [0, '重点重看 S7（证伪）和 S8（判定），那是最值钱的两节。']]
  };

  function escapeAttr(s) { return String(s).replace(/"/g, '&quot;'); }

  document.querySelectorAll('.quiz[data-bank]').forEach(function (box, boxIdx) {
    var key = box.getAttribute('data-bank');
    var sec = box.getAttribute('data-sec');
    var all = BANK[key] || [];
    var items = sec ? all.filter(function (it) { return it.sec === sec; }) : all;
    if (!items.length) return;

    // The radio-group name must be unique per mount point, or two quizzes on the
    // same page would share state and silently clobber each other's answers.
    var ns = key + (sec ? '-' + sec : '') + '-' + boxIdx;

    var host = document.createElement('div');
    items.forEach(function (it, i) {
      var d = document.createElement('div');
      d.className = 'q';
      var opts = it.o.map(function (t, j) {
        return '<label><input type="radio" name="' + escapeAttr(ns + i) + '" value="' + j + '"> ' + t + '</label>';
      }).join('');
      d.innerHTML = '<p>' + (i + 1) + '.　' + it.q + '</p><div class="opts">' + opts +
        '</div><div class="ans" id="' + escapeAttr(ns + 'a' + i) + '"></div>';
      host.appendChild(d);
    });

    var foot = document.createElement('div');
    foot.className = 'q';
    foot.style.textAlign = 'center';
    foot.innerHTML = '<button class="grade" type="button">查看得分</button>' +
      '<div class="ans" id="' + escapeAttr(ns + 'score') + '" style="margin-top:14px"></div>';
    host.appendChild(foot);
    box.appendChild(host);

    foot.querySelector('.grade').addEventListener('click', function () {
      var right = 0;
      items.forEach(function (it, i) {
        var sel = box.querySelector('input[name="' + ns + i + '"]:checked');
        var a = document.getElementById(ns + 'a' + i);
        var ok = sel && Number(sel.value) === it.a;
        if (ok) right++;
        a.className = 'ans show';
        a.innerHTML = (ok ? '<b>✓ 正确。</b>'
          : '<b style="color:var(--warn)">✗ 正确答案：' + it.o[it.a] + '。</b>') + ' ' + it.e;
      });
      var pct = right / items.length;
      var msg = '';
      (VERDICT[key] || []).some(function (row) {
        if (pct >= row[0]) { msg = row[1]; return true; }
        return false;
      });
      if (sec) msg = pct >= 0.7 ? '这一节过了，继续下一节。' : '错的题回上面对应段落重看一遍再往下。';
      var s = document.getElementById(ns + 'score');
      s.className = 'ans show';
      s.innerHTML = '<b>得分：' + right + ' / ' + items.length + '</b>　' + msg;
      s.scrollIntoView({ block: 'center', behavior: 'smooth' });
    });
  });
})();
