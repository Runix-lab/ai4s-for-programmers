"""LAB 1 · 打开一条真实记录，看清所有字段

配套 S4：https://ai4s.runixcloud.io/course/hands-on-day1/
运行：python labs/lab1_read_one_record.py

目标不是读懂输出，是拿着 S1–S3 的概念清单，逐个在输出里指出来。
"""
from _data import load, rule

df = load()
r = df[df.PDB == "5E2W"].iloc[0]   # AT8：识别磷酸化 Tau 的著名抗体

rule("① 这条记录是谁")
print(f"抗体 ID       {r.Antibody_ID}")
print(f"靶点          {r.Target}")
print(f"靶点主键      UniProt {r.Target_UniProt or '(缺失)'}")
print(f"证据等级      {r.Evidence_tier}  ← L1 = 有三维结构确证，最高等级")
print(f"质检标记      {r.QC_flags}")

rule("② 序列：S1 说的『蛋白质就是字符串』")
print(f"VH 可变区 ({len(r.VH_sequence)} aa)")
print(f"  {r.VH_sequence}")
if r.VL_sequence:
    print(f"VL 可变区 ({len(r.VL_sequence)} aa)")
    print(f"  {r.VL_sequence}")
else:
    print("VL 可变区   (无 —— 这是单域抗体)")

rule("③ CDR：S3 说的『三套编号切出不同边界』")
print(f"  CDRH1 IMGT     {r.CDRH1_IMGT}")
print(f"  CDRH2 IMGT     {r.CDRH2_IMGT}")
print(f"  CDRH3 IMGT     {r.CDRH3_IMGT}")
print(f"  CDRH3 Kabat    {r.CDRH3_Kabat}")
print(f"  CDRH3 Chothia  {r.CDRH3_Chothia}")
print()
if r.CDRH3_Kabat == r.CDRH3_Chothia:
    print("  ⚠ 注意：Kabat 和 Chothia 的 CDRH3 完全相同 —— 这不是 bug。")
    print("    这两套体系对 CDR-H3 的定义本来就一致，差别在 H1 / L1。")
    print("    网上流传的『三套体系在每个 CDR 上都不同』是错的。")
print(f"  而 IMGT 比 Kabat 长 {len(r.CDRH3_IMGT) - len(r.CDRH3_Kabat)} 个残基"
      f" —— 用哪套切，去重结果就不一样。")

rule("④ 结构与表位：S3 说的『链 ID 没有语义』")
print(f"  PDB            {r.PDB}   https://www.rcsb.org/structure/{r.PDB}")
print(f"  重链 / 轻链    {r.Hchain} / {r.Lchain or '-'}")
print(f"  抗原链         {r.Antigen_chain}   ← 不是 A！硬编码 chain=='A' 会算错")
print(f"  表位 ({r.N_epitope_residues} 个残基)  {r.Epitope_str}")
print(f"  原子级接触     {r.N_contacts} 对")
print()
print("  这一串表位不是从文献抄的，是从三维坐标算出来的。")
print("  Lab 5 会让你亲手把它算一遍，结果应当逐字符一致。")

rule("⑤ 溯源：S8 说的『可溯源率』")
print(f"  {r.Source_db}  →  {r.Source_URL}")
print("\n  现在做一件事：把上面这个链接贴进浏览器，确认它真的存在、")
print("  且页面里确实是一个抗体-抗原复合物。这就是 S8 的 5 分钟抽查第 1 步。")
print()
