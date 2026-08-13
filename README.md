# AI4S for Programmers

**A free, two-day course that teaches AI for Science to programmers with zero biology background —
by mapping every biological concept onto one you already know.**

🔗 **[ai4s.runixcloud.io](https://ai4s.runixcloud.io)** · 中文授课 · [English overview](https://ai4s.runixcloud.io/en/)

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
its data — that is [question 10](https://ai4s.runixcloud.io/course/judgment/#ten-questions)
of the course, and it applies to us too.

Built by [Runix](https://runixcloud.io).
