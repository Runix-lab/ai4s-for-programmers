"""LAB 3 · 亲手复现子串匹配 bug

配套 S7：https://ai4s.runixcloud.io/course/falsification/
运行：python labs/lab3_substring_bug.py

三类 bug 现场发生。前两类能修，第三类修不了——只能承认并披露。
"""
import re
from _data import load, rule

df = load()

# 真实的抗原名字段里会出现的字符串。这里用样本里的真实 Target，
# 再补几条在真实数据里确实存在、且专门用来触发这三类 bug 的名字。
NAMES = list(df.Target.unique()) + [
    "NEURAMINIDASE",
    "INFLUENZA A VIRUS NEURAMINIDASE",
    "BROADLY NEUTRALIZING ANTIBODY FAB FRAGMENT",
    "RECEPTOR TYROSINE-PROTEIN KINASE ERBB-2",       # HER2 本尊
    "PROGRAMMED CELL DEATH 1",                        # PD-1（基因全名）
    "PROGRAMMED CELL DEATH 1 LIGAND 1",               # PD-L1（前缀关系！）
    "ANTI-APP TAG FAB",                               # 语义陷阱
    "AMYLOID-BETA PRECURSOR PROTEIN",                 # 真正的 APP
    "HEMAGGLUTININ",                                  # 流感 HA
    "ANTI-HA TAG ANTIBODY",                           # 标签 HA，同名不同物
]

rule("BUG 1 · 没加词边界：HER2 的别名 'neu'")
naive = [n for n in NAMES if "NEU" in n.upper()]
print(f"  裸子串 'NEU' 命中 {len(naive)} 条：")
for n in naive:
    print(f"     - {n}")

left_only = re.compile(r"(?<![A-Za-z0-9])neu", re.I)
hits_left = [n for n in NAMES if left_only.search(n)]
print(f"\n  只加【左侧】边界 (?<![A-Za-z0-9])neu  →  还剩 {len(hits_left)} 条：")
for n in hits_left:
    print(f"     - {n}   ← 还在！因为 NEU 正好在词首")

both = re.compile(r"(?<![A-Za-z0-9])neu(?![A-Za-z0-9])", re.I)
hits_both = [n for n in NAMES if both.search(n)]
print(f"\n  两侧都加 (?<![A-Za-z0-9])neu(?![A-Za-z0-9])  →  剩 {len(hits_both)} 条")
print(f"  等价写法 \\bneu\\b  →  剩 {len([n for n in NAMES if re.search(r'\\bneu\\b', n, re.I)])} 条")
print()
print("  教训：单边断言看起来『加了边界』，其实只挡住了一半。")
print("  这门课第一版就写成了单边——修好了，和验证过修好了，是两件事。")

rule("BUG 2 · 前缀关系：加词边界也救不了")
PD1 = "programmed cell death 1"
PDL1 = "programmed cell death 1 ligand 1"
pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(PD1) + r"(?![A-Za-z0-9])", re.I)
print(f"  用 PD-1 的基因全名做带词边界的匹配：")
print(f"    '{PD1}'")
for n in NAMES:
    if pat.search(n):
        verdict = "✓ 对" if n.upper() == PD1.upper() else "✗ 误判！这其实是 PD-L1"
        print(f"      命中 → {n}   {verdict}")
print()
print("  为什么：PD-1 的基因全名是 PD-L1 基因全名的【前缀】，")
print("  而 'death 1' 后面跟的是空格，不是字母数字，所以右边界断言通过了。")
print("  解法是包含消歧：同一段文本里，长匹配压制短匹配。")
print()
print("  ⚠ 顺带注意：换成 UniProt 的【蛋白】名就不构成前缀了")
print("    （'Programmed cell death protein 1'，多一个 protein）。")
print("    『是不是前缀』取决于你用的是哪个源的哪个字段。")

rule("BUG 3 · 语义陷阱：正则解决不了")
print("  'ANTI-APP TAG FAB'")
print("    → 这是结合实验室【标签肽】的试剂抗体，不是抗 APP 蛋白的。")
print("    → 但它包含 'APP'，任何基于名字的匹配都会命中。")
print()
print("  'ANTI-HA TAG ANTIBODY'  vs  'HEMAGGLUTININ'")
print("    → 前者的 HA 是标签肽，后者的 HA 是流感血凝素。")
print("    → 同一个缩写，两个完全无关的东西。")
print()
print("  这一类没有正则解法。只能靠语境规则、人工规则表，")
print("  或者干脆承认『这部分我们盖不住』并在交付时披露占比。")
print()
print("  → 前两类是【实现 bug】，能修。")
print("  → 第三类是【方法边界】，只能承认。")
print("     成熟供应商会告诉你第三类占多少；不成熟的假装它不存在。")
print()
