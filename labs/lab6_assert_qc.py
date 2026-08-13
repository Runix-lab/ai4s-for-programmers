"""LAB 6 · 用写单元测试的方式做质检

配套 S7：https://ai4s.runixcloud.io/course/falsification/
运行：python labs/lab6_assert_qc.py         （最后一项需要联网，可用 --offline 跳过）

质检不是「出一份统计报告」，是【写一组必须成立的断言】，挂了就打印具体哪几行。
里面埋了一个陷阱——关于 HTTP 403 该不该判定为「链接坏了」。
"""
import sys
import urllib.error
import urllib.request

from _data import load, rule

OFFLINE = "--offline" in sys.argv
df = load()
results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"  {'✓ PASS' if ok else '✗ FAIL'}  {name}")
    if detail:
        print(f"          {detail}")


rule("① 数据库约束级断言")

dupes = df.Antibody_ID[df.Antibody_ID.duplicated()].tolist()
check("主键唯一 (Antibody_ID)", not dupes,
      f"重复：{dupes}" if dupes else "")

orphan = df[(df.Evidence_tier == "L1") & (df.PDB == "")]
check("L1 记录必须有 PDB（外键不为空）", len(orphan) == 0,
      f"{len(orphan)} 行 L1 却没有 PDB" if len(orphan) else "")

bad_tier = sorted(set(df.Evidence_tier) - {"L1", "L2", "L3", "L4"})
check("Evidence_tier 值域合法", not bad_tier,
      f"非法值：{bad_tier}" if bad_tier else "")

bad_pdb = df[~df.PDB.str.fullmatch(r"[0-9][A-Za-z0-9]{3}")]
check("PDB 号格式合法（4 位）", len(bad_pdb) == 0,
      f"{len(bad_pdb)} 行格式不对" if len(bad_pdb) else "")


rule("② 内部一致性断言 —— 最容易被忽略的一类")

# 每个 CDR 都必须是所在链的子串。这条不需要任何外部数据就能查，
# 却能一次性抓出「CDR 是从别的地方拼来的」这种严重问题。
bad = []
for _, r in df.iterrows():
    for col in ("CDRH1_IMGT", "CDRH2_IMGT", "CDRH3_IMGT"):
        if r[col] and r[col] not in r.VH_sequence:
            bad.append(f"{r.Antibody_ID}: {col}={r[col]} 不在 VH 里")
    if r.CDRL3_IMGT and r.VL_sequence and r.CDRL3_IMGT not in r.VL_sequence:
        bad.append(f"{r.Antibody_ID}: CDRL3 不在 VL 里")
check("每个 CDR 都是所在链的子串", not bad, "\n          ".join(bad[:5]))

# 表位残基数必须和表位串里的残基个数对得上
mismatch = [r.Antibody_ID for _, r in df.iterrows()
            if r.Epitope_str and int(r.N_epitope_residues) != len(r.Epitope_str.split(";"))]
check("N_epitope_residues 与 Epitope_str 自洽", not mismatch,
      f"不一致：{mismatch[:5]}" if mismatch else "")

# 抗原链不能同时是抗体链
overlap = [r.Antibody_ID for _, r in df.iterrows()
           if r.Antigen_chain in (r.Hchain, r.Lchain) and r.Antigen_chain]
check("抗原链 ≠ 抗体链", not overlap,
      f"重叠：{overlap[:5]}" if overlap else "")


rule("③ 注意这一条断言的【语义】")

# 关键：断言的不是「不许有缺陷」，是「不许有【未披露的】缺陷」。
undisclosed = []
for _, r in df.iterrows():
    if not r.VL_sequence and "NO_LIGHT_CHAIN" not in r.QC_flags:
        undisclosed.append(f"{r.Antibody_ID}: 无轻链但 QC_flags 没披露")
    if "X" in r.VH_sequence and "AMBIGUOUS_RESIDUE" not in r.QC_flags:
        undisclosed.append(f"{r.Antibody_ID}: 含模糊码但 QC_flags 没披露")
    if not r.Target_UniProt and "ANTIGEN_UNIPROT_MISSING" not in r.QC_flags:
        undisclosed.append(f"{r.Antibody_ID}: 缺 UniProt 但 QC_flags 没披露")
check("所有缺陷均已在 QC_flags 披露", not undisclosed,
      "\n          ".join(undisclosed[:5]))

n_defect = (df.QC_flags != "OK").sum()
print()
print(f"  这份数据有 {n_defect} 行带缺陷标记，占 {n_defect / len(df):.0%}。")
print("  断言过了【不是因为数据完美】，是因为缺陷都被如实披露了。")
print("  如果把断言写成「不许有缺陷」，你会被迫去『修』一批本来合法的数据")
print("  ——比如把单域抗体删掉，只因为它没有轻链。")


rule("④ 抽样溯源检查 —— 这里有个陷阱")

if OFFLINE:
    print("  （--offline 已跳过）")
else:
    sample = df.head(5)
    hard_fail, soft = [], []
    for _, r in sample.iterrows():
        url = r.Source_URL
        try:
            req = urllib.request.Request(url, method="HEAD",
                                         headers={"User-Agent": "ai4s-lab/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                code = resp.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:
            code = type(e).__name__
        state = "OK" if code == 200 else str(code)
        print(f"     {r.PDB}  HTTP {state:<12} {url}")
        if code in (403, 429, 405):
            soft.append((r.PDB, code))
        elif code != 200:
            hard_fail.append((r.PDB, code))

    print()
    if soft:
        print(f"  ⚠ 有 {len(soft)} 条返回了 403/429/405：{soft}")
        print("    这【不等于】链接坏了——403 是反爬、429 是限流、405 是不支持 HEAD。")
        print("    如果断言写成「必须全部 200」，这些好链接会被误判成坏的，")
        print("    然后你会去『修』一个根本不存在的问题。")
    check("溯源链接无硬失败（4xx/5xx 中排除 403/429/405）", not hard_fail,
          f"真失败：{hard_fail}" if hard_fail else "")
    print()
    print("  教训：【验证方法本身也需要被验证】。")
    print("  这和「测试挂了先看是代码错了还是测试写错了」是同一件事——")
    print("  只不过在数据工程里，没有人会自动提醒你去看第二种可能。")


rule("汇总")
passed = sum(1 for _, ok, _ in results if ok)
print(f"  {passed} / {len(results)} 项断言通过")
print()
print("  把这组断言挂进 CI，数据变了、管线改了，重跑一遍立刻知道有没有破。")
print("  这就是把「数据质量」从一个形容词变成可执行、可回归的东西。")
print()
sys.exit(0 if passed == len(results) else 1)
