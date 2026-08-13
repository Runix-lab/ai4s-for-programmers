# AI4S for Programmers · 程序员的 AI for Science 入门（生物数据方向）

> **两天，零生物背景，学会读懂一份抗体／蛋白数据集，并在五分钟内判断它可不可信。**
> AI for Science 里最难的部分不是科学，是数据工程——而那是程序员的主场。

**🔗 [ai4s.runixcloud.io](https://ai4s.runixcloud.io)**　·　中文授课　·　[English overview](https://ai4s.runixcloud.io/en/)

![content: CC BY-SA 4.0](https://img.shields.io/badge/content-CC%20BY--SA%204.0-1c6b58)
![code: MIT](https://img.shields.io/badge/code-MIT-2e3f8c)
![prerequisites: Python](https://img.shields.io/badge/前置-会写%20Python-697080)
![biology: none](https://img.shields.io/badge/生物基础-零-a8382c)

**关键词**：AI for Science 入门 · AI4S 教程 · 生物信息学 入门 · 抗体数据 · 蛋白数据清洗 ·
生物数据工程 · 程序员转 AI 制药 · IMGT Kabat Chothia 区别 · 表位 互补位 · UniProt 归一化 ·
交叉源验证 · AlphaFold 局限

> ⚠️ **范围声明**：这门课只覆盖 AI for Science 的**生物数据方向**（抗体与蛋白质的数据采集、
> 清洗、实体归一与质量验证）。材料、气候、天文等其它 AI4S 方向不在范围内，模型训练也不讲。
> 一门讲「怎么识破夸大数据」的课，没有资格夸大自己的覆盖面。

---

## 两天学什么

| 阶段 | 内容 | 时长 |
|---|---|---|
| **1 · 建立词汇表** | 蛋白质是字符串、抗体是 4 条链的对象、UniProt 登录号是主键 | 150 min |
| **2 · 看懂真实数据** | FASTA / PDB / 三套编号体系；打开一条真实记录逐字段对照 | 150 min |
| **3 · 建立判断力 ★** | 亲手把四个真实的 bug 跑出来：词边界假阳性、别名劫持、实算表位、断言式质检 | 210 min |
| **4 · 拿去用** | 三维验收、十个必问问题、五分钟抽查法、红旗清单 | 60 min |

学完做[结业考试](https://ai4s.runixcloud.io/study/exam/)，答对 16/20 可下载结业证明
（浏览器本地生成，**不是第三方认证**）。

---

## The premise

Biology is not hard because it is complicated. It is hard because every introduction
assumes you already have the vocabulary. So this course never explains a biological
concept on its own terms first:

| Biology | What you already know |
|---|---|
| Protein sequence | `string` over a 20-letter alphabet |
| Antibody | an object holding 4 strings |
| Variable / constant region | instance fields / shared class members |
| CDR | the few substrings that decide behaviour |
| KD (affinity) | a float on a log scale — read it like p99 latency |
| UniProt accession | primary key / UUID |
| Protein aliases | display names, and **they collide** |
| IMGT / Kabat / Chothia | competing schema versions |
| Cross-source validation | you cannot verify a source with itself |
| QC flags | a known-issues list |

**Every data problem in this field is one you have already met in software engineering.
What is missing is the vocabulary, not the ability.**

---

## What is in this repo

```
content/          course text, one HTML fragment per page + pages.py (metadata & SEO)
assets/           stylesheet, client JS, the 35-question bank, OG image template
labs/             six runnable Python labs + the public sample dataset
build.py          stdlib-only static site generator
dist/             the built site (committed; CI fails if it is stale)
```

## The six labs

Every lab is a real script producing real output — no pseudocode, no toy data.

| Lab | What it does | Network |
|---|---|---|
| `lab1_read_one_record.py` | Print one antibody record field by field | offline |
| `lab2_data_checkup.py` | `COUNT(*) / GROUP BY` health check over the dataset | offline |
| `lab3_substring_bug.py` | Reproduce three classes of name-matching false positive | offline |
| **`lab4_cross_source.py`** | **Ask HGNC and UniProt the same question, watch them disagree** | required |
| `lab5_compute_epitope.py` | Compute an epitope from 3D coordinates via neighbour search | offline |
| `lab6_assert_qc.py` | Data QC written as assertions, with a deliberate trap | required |

```bash
git clone https://github.com/Runix-lab/ai4s-for-programmers
cd ai4s-for-programmers
python3 -m venv .venv && source .venv/bin/activate
pip install -r labs/requirements.txt

python labs/lab1_read_one_record.py
```

### About the sample dataset

`labs/data/sample_antibodies.csv` holds 29 antibody-antigen complexes and is built
**entirely from public RCSB PDB data** by `labs/data/build_sample.py` — structures and
sequences from RCSB, CDRs numbered locally with ANARCI/abnumber, epitopes computed with
gemmi. The build script is in the repo, so the dataset is reproducible rather than
asserted.

It deliberately keeps its defects: 3 single-domain antibodies with no light chain,
2 rows missing a UniProt cross-reference, 1 with an ambiguity code — all flagged in
`QC_flags`. A teaching dataset scrubbed clean installs intuitions that do not survive
contact with real data.

The sample also independently confirms two claims the course makes:
**29/29 rows have identical Kabat and Chothia CDR-H3**, and **16/29 rows have an antigen
chain that is not `A`**. Run `lab2` and count for yourself.

---

## Accuracy

Every checkable claim was re-verified against primary sources before publication —
database REST APIs, the original numbering-scheme papers, and the structures themselves.
**That pass found and corrected fourteen errors in the first draft**, including one in
the table this site uses as its flagship example. Two worth naming, because they get
copied around unexamined:

- **Kabat and Chothia define CDR-H3 identically.** The widely repeated claim that all
  three schemes carve different H3 boundaries is wrong; the differences are in H1 and L1.
- **VHH nanobodies come from camelids only.** Shark single-domain antibodies are VNAR,
  from IgNAR — a separate evolutionary origin, not a kind of VHH.

A course about verifying other people's data has no business hiding its own corrections.
**Found an error? [Open an issue](https://github.com/Runix-lab/ai4s-for-programmers/issues)** —
it gets fixed in public.

---

## Building the site

No npm, no framework, no build dependencies beyond the Python standard library.

```bash
python3 build.py           # build into dist/
python3 build.py --check   # what CI runs: fails if dist/ is stale or lint trips
```

`build.py` also lints for the SEO mistakes that are invisible in a browser: over-long
titles (measured in display width, since a CJK glyph is twice as wide), duplicate or
badly sized meta descriptions, and dead internal links. OG images are rendered to PNG
by headless Chrome at build time; the step is skipped where Chrome is absent.

**`dist/` is committed** so the site deploys with no build step. `--check` in CI is what
keeps that honest — edit a source file without rebuilding and the build fails.

---

## Licence

- **Content** (course text, glossary, quiz questions): [CC BY-SA 4.0](LICENSE-CONTENT)
- **Code** (`build.py`, `labs/`, `assets/*.js`, `assets/*.css`): [MIT](LICENSE)

The sample dataset is derived from [RCSB PDB](https://www.rcsb.org/), which places its
data in the public domain (CC0). Check the terms of any other database before reusing
its data — that is [question 10](https://ai4s.runixcloud.io/study/judgment/#ten-questions)
of the course, and it applies to us too.

## 社交预览图

`docs/social-preview.png`（1280×640）可在 GitHub 仓库
**Settings → General → Social preview → Upload an image** 上传，
决定这个仓库被分享到任何地方时的卡片长什么样。

---

Built by [Runix](https://runixcloud.io).
