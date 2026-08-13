"""LAB 5 · 亲手从三维结构算出表位

配套 S7：https://ai4s.runixcloud.io/course/falsification/
运行：python labs/lab5_compute_epitope.py       （结构文件已内置，离线可跑）

程序员视角：这就是一次【空间近邻查询】。
把抗体的所有原子和抗原的所有原子丢进 KD 树，找出距离小于阈值的原子对。
「表位」不是从文献抄的，是这么算出来的。
"""
import pathlib
import sys
import urllib.request

from _data import load, rule

PDB = "5E2W"       # AT8 抗体 + 磷酸化 Tau 肽段
CUTOFF = 4.5       # Å（埃，10⁻¹⁰ 米）。重原子间距。是【约定】不是真理。

try:
    import gemmi
except ImportError:
    sys.exit("需要 gemmi：pip install -r labs/requirements.txt")

# 链名从数据表里读，不硬编码 —— 这正是 S3 教的那一条
row = load().query("PDB == @PDB").iloc[0]
AB_CHAINS = [c for c in (row.Hchain, row.Lchain) if c]
AG_CHAIN = row.Antigen_chain

cache = pathlib.Path(__file__).resolve().parent / "data" / "structures" / f"{PDB}.cif.gz"
if not cache.exists():
    print(f"本地没有 {PDB}，从 RCSB 下载 …")
    cache.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(f"https://files.rcsb.org/download/{PDB}.cif.gz", timeout=90) as r:
        cache.write_bytes(r.read())

st = gemmi.read_structure(str(cache))
st.setup_entities()
st.remove_ligands_and_waters()
st.remove_hydrogens()          # 只算重原子 —— 这是阈值定义的一部分
model = st[0]

rule("① 先看清楚结构里有什么")
print(f"  PDB               {PDB}")
print(f"  结构里的链        {[ch.name for ch in model]}")
print(f"  抗体链（来自数据表）{AB_CHAINS}")
print(f"  抗原链（来自数据表）{AG_CHAIN}")
print()
print(f"  ⚠ 抗原链是 '{AG_CHAIN}' 而不是 'A'。链 ID 由沉积者自定、没有语义，")
print("    所以这里从数据表读，不硬编码。写死 chain=='A' 是这一步最常见的 bug。")

rule("② 做空间近邻查询")
print(f"  阈值 {CUTOFF} Å，只算重原子（已移除氢原子）")
ns = gemmi.NeighborSearch(model, st.cell, CUTOFF + 1).populate()

epitope, paratope, contacts = {}, {}, 0
for ch in model:
    if ch.name != AG_CHAIN:
        continue
    for res in ch:
        for at in res:
            for mark in ns.find_atoms(at.pos, "\0", radius=CUTOFF):
                cra = mark.to_cra(model)
                if cra.chain.name not in AB_CHAINS:
                    continue
                if at.pos.dist(cra.atom.pos) > CUTOFF:
                    continue
                contacts += 1
                epitope[(res.seqid.num, res.name)] = epitope.get((res.seqid.num, res.name), 0) + 1
                key = (cra.chain.name, cra.residue.seqid.num, cra.residue.name)
                paratope[key] = paratope.get(key, 0) + 1


def one(name):
    info = gemmi.find_tabulated_residue(name)
    return (info.one_letter_code.upper() if info else "X") or "X"


print(f"  原子级接触 {contacts} 对")

rule("③ 表位：抗原一侧被抓住的残基")
for (num, name), c in sorted(epitope.items()):
    mod = "   ← 磷酸化修饰！" if name in ("SEP", "TPO", "PTR") else ""
    print(f"     {one(name)}{num:<5} ({name})   接触 {c:>3} 次{mod}")

print()
print("  SEP = 磷酸化的丝氨酸，TPO = 磷酸化的苏氨酸。")
print("  它们说明这个抗体识别的是【磷酸化状态的】Tau，而不是 Tau 本身——")
print("  这个信息只在三维结构里有，一维序列里没有。")

rule("④ 互补位：抗体一侧伸出去接触的残基（前 10 个）")
for (chn, num, name), c in sorted(paratope.items())[:10]:
    print(f"     {chn} 链  {one(name)}{num:<5} ({name})   接触 {c:>3} 次")
print(f"\n  共 {len(epitope)} 个表位残基、{len(paratope)} 个互补位残基。")

rule("⑤ 和数据表对账")
computed = ";".join(f"{one(n)}{num}" for (num, n) in sorted(epitope))
print(f"  刚算出来的  {computed}")
print(f"  数据表里的  {row.Epitope_str}")
print()
if computed == row.Epitope_str:
    print("  ✓ 逐字符一致 —— 因为表里那一列就是这么算出来的，不是抄的。")
else:
    print("  ✗ 不一致！这说明表里那列用了不同的阈值、不同的链、或者根本是抄的。")
    print("    在真实项目里，这一步对不上就该停下来查，不该改断言。")

rule("⑥ 这个实验最值钱的两句话")
print(f"  ① 阈值和原子集合都是【约定】。这里用的是 {CUTOFF} Å 重原子间距；")
print("     4.0 / 4.5 / 5.0 Å 都有人用，算出的残基数会不一样。")
print("     所以阈值必须随数据一起交付——不写清楚的表位列没法和别人的比较。")
print()
print("  ② 残基编号也要说明基准。上面的 202-209 是按 tau 的 2N4R 亚型（441 aa）编的；")
print("     换一个亚型，同一个残基的编号就变了。")
print("     这和『跨毒株表位编号失效』是同一个问题——【坐标基准】。")
print()
print("  自己试试：把上面的 CUTOFF 改成 4.0 再跑一遍，看表位少了几个残基。")
print()
