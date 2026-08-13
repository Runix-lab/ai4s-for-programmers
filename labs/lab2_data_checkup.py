"""LAB 2 · 给数据做体检

配套 S4：https://ai4s.runixcloud.io/course/hands-on-day1/
运行：python labs/lab2_data_checkup.py

这就是 SELECT COUNT(*) ... GROUP BY，只不过字段名是生物术语。
拿到任何一份陌生数据，先做这四项，五分钟。
"""
from _data import load, rule

df = load()

rule("① 规模与外键基数  ≈ COUNT(*) / COUNT(DISTINCT fk)")
print(f"  总行数            {len(df)}")
print(f"  独立靶点(UniProt) {df[df.Target_UniProt != ''].Target_UniProt.nunique()}")
print(f"  独立结构(PDB)     {df.PDB.nunique()}")
print()
print("  为什么先看这个：外键基数太低 = 数据集中在少数几个靶点上，")
print("  模型学到的可能只是『这几个靶点长什么样』，换个靶点就废。")

rule("② 证据分层  ≈ GROUP BY confidence_tier")
for tier, n in df.Evidence_tier.value_counts().items():
    print(f"  {tier}   {n:>4} 行   ({n / len(df):.0%})")
print()
print("  这是最重要的一项。总数好看但全堆在最低等级，等于没有。")
print("  （这份样本全是 L1 结构确证，因为它就是从 PDB 建的。")
print("   真实的商业数据集里 L4 通常占大头——问清楚比例。）")

rule("③ 字段填充率  ≈ COUNT(col) / COUNT(*)")
for col in ["VH_sequence", "VL_sequence", "CDRH3_IMGT", "Target_UniProt",
            "Epitope_str", "Source_URL"]:
    filled = (df[col] != "").sum()
    bar = "█" * round(filled / len(df) * 24)
    print(f"  {col:<16} {filled:>3}/{len(df)}  {filled / len(df):>4.0%}  {bar}")
print()
n_nolight = (df.VL_sequence == "").sum()
print(f"  VL_sequence 缺 {n_nolight} 条 —— 这不是缺陷，是 {n_nolight} 条单域抗体。")
print("  把『空值』一律当成『数据质量问题』，会误伤一整类合法数据。")

rule("④ QC 标记分布  ≈ GROUP BY qc_flag")
for flag, n in df.QC_flags.value_counts().items():
    print(f"  {n:>3} 行   {flag}")
print()
ok_frac = (df.QC_flags == "OK").mean()
print(f"  标记为 OK 的比例：{ok_frac:.0%}")
if ok_frac == 1.0:
    print("  ⚠ 全部 OK —— 按 S8 的红旗清单，这本身就值得怀疑。")
else:
    print("  有 OK 之外的标记是好事：说明质检真的在跑，而且缺陷被披露了。")
    print("  拿不出缺陷清单的数据供应商，比拿得出缺陷清单的更可疑。")

rule("⑤ 一个只有这一步能发现的问题")
odd = df[df.Antigen_chain != "A"]
print(f"  抗原链不是 'A' 的行：{len(odd)} / {len(df)}  ({len(odd) / len(df):.0%})")
print(f"  实际出现过的抗原链 ID：{sorted(df.Antigen_chain.unique())}")
print()
print("  如果你的解析代码里写了 chain == 'A'，")
print(f"  这份数据里 {len(odd)} 行会被算错，而且不会报任何错。")
print()
