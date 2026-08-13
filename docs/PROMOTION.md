# 投放包

站点 <https://ai4s.runixcloud.io> · 仓库 <https://github.com/Runix-lab/ai4s-for-programmers>

所有文案共用一条主张，不要换：

> **AI for Science 里最难的不是科学，是数据工程——而那是程序员的主场。**
> 两天，零生物背景，学会读懂一份抗体／蛋白数据集并判断它可不可信。

配套三个硬钩子（都能自证，别用形容词）：

1. **同一批原始数据，朴素方法能"做"出六万多条配对，八成经不起推敲。**
2. **两种都"合理"的查法各自翻车**：一种把 HER2 认成酿酒酵母的基因，另一种把 CCR4 认成另一个蛋白。
3. **发布前逐条核查改掉了自己 14 处错误**，包括"Kabat 与 Chothia 的 CDR-H3 其实相同"——
   而这条广为流传的错误说法，原本是本课的招牌例子。

---

## 一、GitHub 引流

**已完成**：仓库公开、13 个 topics、README 带核心对照表与「Accuracy」自曝章节。

**待做（按性价比排序）**：

| 目标 | 怎么做 | 备注 |
|---|---|---|
| `awesome-bioinformatics` | PR 加到 Education / Tutorials 段 | 最对口 |
| `awesome-python-in-science` / `awesome-biology` | 同上 | |
| `awesome-ai4science` 系列 | 搜 `awesome ai for science`，逐个提 PR | 注意标注是**生物数据方向**，别冒充全领域 |
| 自有 `awesome-ai-gateway` | README 底部加一行 Related | 零成本 |
| GitHub Discussions | 开一个「发现错误请提 issue」置顶帖 | 兑现 README 的承诺 |

**PR 文案模板**（英文，投英文列表用）：

```
- [AI4S for Programmers](https://ai4s.runixcloud.io) — A free two-day course
  teaching the data-engineering side of AI for Science (antibody/protein data)
  to programmers with zero biology background. Six runnable labs over a
  reproducible public dataset; every claim verified against primary sources.
```

---

## 二、公众号 / 中文社区

**标题候选**（都指向同一个反差，别用「保姆级」「一文读懂」）：

1. 我把一份抗体数据集的六万条配对，验到只剩一万二
2. 程序员两天入门 AI for Science：难的不是生物，是你早就会的那些事
3. Kabat 和 Chothia 的 CDR-H3 其实是一样的——我这门课第一版抄错了

**正文结构**（3000 字以内，别长）：

1. **开场用第 2 个钩子**：贴那张三方对照表，问读者能不能看出哪行错了
2. **翻译层**：生物↔编程对照表（直接搬站点首页那张）
3. **五个真实的坑**，重点讲"数据表面完全正常"
4. **自曝 14 处错误**——这是全文最有说服力的部分，别删
5. **结尾**：站点链接 + GitHub + 免费开源 + 结业证明

**投放渠道**：公众号首发 → 掘金 / 知乎（改标题 1）→ V2EX（改标题 3，社区吃这个）

⚠️ **对客口径**：不点名任何客户或数据供应商；踩坑案例一律用"某份数据"表述。

---

## 三、SEO 收录（需要域名所有权验证，只能人工做）

1. **Google Search Console** → 加 `ai4s.runixcloud.io` → DNS TXT 验证（Cloudflare 里加）→ 提交 `sitemap.xml`
2. **Bing Webmaster Tools** → 可从 GSC 导入
3. **百度搜索资源平台** —— 中文流量主要来源，别漏

**已就位**：17 页 sitemap、robots 放行 GPTBot/ClaudeBot/PerplexityBot、
每页 canonical + JSON-LD（Course/LearningResource/FAQPage/BreadcrumbList）、
旧路径 301、OG 图。

**主打长尾词**（都已在页面里）：
`IMGT Kabat Chothia 区别`、`表位 互补位 区别`、`KD 解离常数 怎么看`、
`AlphaFold 没解决什么`、`交叉源验证`、`AI for Science 入门`

---

## 四、别做的事

- 不买量、不互推垃圾站，这个站的价值全在可信度上
- 不夸大覆盖面（它只是 AI4S 的生物数据方向）
- 不把结业证明包装成资质认证
