"""LAB 4 · 亲手做一次交叉源验证  ★ 本课最重要的实验

配套 S7：https://ai4s.runixcloud.io/course/falsification/
运行：python labs/lab4_cross_source.py      （需要联网）

这个实验问同一个问题三次：一次问 HGNC，两次问 UniProt（用两种都很"合理"的查法）。
你会看到一件比"有 bug"更重要的事——

    没有哪一种查法是对的。它们各自以【不同方式】翻车。

所以正确答案不是"换个更好的查法"，是"必须交叉验证"。
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

from _data import rule

HGNC_URL = "https://rest.genenames.org/fetch/{route}/{q}"

# 查法 A —— 朴素：全文检索，不限物种，取第一条命中。
#   看起来"简单直接"，实际是很多管线的默认写法。
UNIPROT_NAIVE = ("https://rest.uniprot.org/uniprotkb/search?query={q}"
                 "&fields=accession,gene_names,organism_name&size=1")

# 查法 B —— 看起来更严谨：精确基因名 + 限人源 + 只要人工审校过的条目。
#   这是"我已经加过防御了"的典型写法。
UNIPROT_STRICT = ("https://rest.uniprot.org/uniprotkb/search?query=gene_exact:{q}"
                  "+AND+organism_id:9606+AND+reviewed:true"
                  "&fields=accession,gene_names,organism_name&size=1")

# 六个真实的药物靶点名，都是数据里天天出现的写法
TOKENS = ["CCR4", "HER2", "PD-1", "4-1BB", "OX40", "CD166"]


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"_http": e.code}
    except Exception as e:
        return {"_err": type(e).__name__}


def ask_hgnc(token):
    """路由顺序有讲究：现用符号必须先查，否则活跃基因会被别的基因的别名劫持。"""
    for route in ("symbol", "alias_symbol", "prev_symbol"):
        d = get(HGNC_URL.format(route=route, q=urllib.parse.quote(token)),
                {"Accept": "application/json"})
        docs = (d.get("response") or {}).get("docs") or []
        if docs:
            return docs[0].get("symbol"), route
    return None, None


def ask_uniprot(template, token):
    d = get(template.format(q=urllib.parse.quote(token)))
    res = d.get("results") or []
    if not res:
        return None, None, None
    r = res[0]
    genes = r.get("genes") or [{}]
    sym = (genes[0].get("geneName") or {}).get("value")
    org = (r.get("organism") or {}).get("scientificName", "")
    return sym, r.get("primaryAccession"), org


rule("同一个问题，三种问法")
print("  HGNC       基因命名权威，按 现用符号 → 别名 → 旧名 的顺序查")
print("  UniProt-A  朴素：全文检索、不限物种、取第一条")
print("  UniProt-B  严谨：gene_exact + 只要人源 + 只要人工审校条目")
print()

rows = []
for tok in TOKENS:
    h, route = ask_hgnc(tok)
    a_sym, a_acc, a_org = ask_uniprot(UNIPROT_NAIVE, tok)
    b_sym, b_acc, b_org = ask_uniprot(UNIPROT_STRICT, tok)
    rows.append((tok, h, route, a_sym, a_acc, a_org, b_sym, b_acc))

print(f"  {'输入':<7}{'HGNC':<10}{'UniProt-A 朴素':<34}{'UniProt-B 严谨'}")
print("  " + "─" * 82)
for tok, h, route, a_sym, a_acc, a_org, b_sym, b_acc in rows:
    a = f"{a_sym or '-'} {a_acc or ''} [{(a_org or '?')[:18]}]" if a_acc else "(查不到)"
    b = f"{b_sym or '-'} {b_acc or ''}" if b_acc else "(查不到)"
    print(f"  {tok:<7}{h or '-':<10}{a:<34}{b}")

rule("现在逐条看这张表——每一行都在教不同的东西")

for tok, h, route, a_sym, a_acc, a_org, b_sym, b_acc in rows:
    notes = []
    # 物种泄漏：朴素查法最危险的失败模式，因为结果长得完全正常
    if a_org and "Homo sapiens" not in a_org:
        notes.append(f"朴素查法命中了【{a_org}】——不是人的基因，但字段齐全、看不出异常")
    # 别名劫持：严谨查法反而中招
    if b_sym and h and b_sym.upper() != h.upper():
        notes.append(f"严谨查法把它解析成了【{b_sym}】({b_acc})，与 HGNC 的 {h} 冲突 ★")
    # 查不到 ≠ 错
    if h and not b_acc:
        notes.append(f"严谨查法查不到——因为 {tok} 是【别名】不是基因符号（HGNC 从 {route} 命中）")
    if a_sym and b_sym and h and a_sym.upper() == h.upper() and b_sym.upper() != h.upper():
        notes.append("注意：朴素查法在这一行反而是对的")

    if notes:
        print(f"\n  {tok}  (HGNC: {h})")
        for n in notes:
            print(f"     · {n}")

rule("这个实验真正要你带走的东西")
print("  ① 两种查法都『合理』，但它们在不同的行上翻车：")
print("     - 朴素查法会悄悄跨物种，把酵母/兔/鲑鱼的基因当成人的靶点；")
print("     - 严谨查法能挡住物种泄漏，却会被【别名劫持】——")
print("       CCR4 被记为 NOCT 的一个基因名同义词，于是解析到了错误的蛋白上。")
print()
print("  ② 所以正确做法不是『找一个更好的查法』，是【交叉验证】：")
print("     拿另一个独立权威源来对，两边一致才算过，不一致的一律人工看。")
print()
print("  ③ 把『冲突』和『查不到』分开处理。")
print("     查不到往往只是说明这个词是别名不是符号——")
print("     全部当成错误会淹没真正的冲突。")
print()
print("  ④ 顺带一个反直觉的点：『拉黑 HGNC 里的废弃符号』这个防御措施")
print("     拦不住 CCR4 这个坑——HGNC 记录的 NOCT 旧符号是 CCRN4L，不是 CCR4。")
print("     两个权威库对『什么算别名』本来就不完全一致，")
print("     而冲突恰好发生在它们不一致的地方。")

rule("推论（对你自己也成立）")
print("  用产出结果的【同一个源】去检查结果 = 循环论证。")
print("  这和写测试时不能用被测代码自己的逻辑去断言，是完全一样的道理。")
print()
print("  所以：你用某个 AI 生成了一份数据，再用同一个 AI 检查它——")
print("  那不是验证，那是让它复述一遍自己的答案。")
print()
print("  ⚠ 这些是实时 API，结果会随数据库更新而变化。")
print("     如果某天某一行不再冲突了，那不是实验失效——")
print("     那正好说明【为什么验证必须是持续跑的，不是一次性的】。")
print()
