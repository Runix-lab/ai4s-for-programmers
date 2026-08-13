#!/usr/bin/env python3
"""Build the teaching sample dataset from public sources only.

Everything this script writes is derived from two public services:

  * RCSB PDB   — structures, polymer entity sequences, chain roles, UniProt xrefs
  * ANARCI     — antibody numbering (IMGT / Kabat / Chothia), computed locally

Nothing here comes from any private or commercial dataset. The output is
committed to the repo so that the labs run without network access, but this
script is what produced it and re-running it should reproduce the same rows.

    pip install gemmi anarci pandas requests
    python labs/data/build_sample.py

Note the deliberate design choice: the sample keeps its real defects — missing
light chains, ambiguity codes, unresolved residues. A dataset scrubbed clean for
teaching would install intuitions that do not survive contact with real data.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import pathlib
import sys
import time
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "sample_antibodies.csv"
CIF_DIR = HERE / "structures"

# Well-known antibody-antigen complexes. Every one of these PDB IDs is public
# knowledge; the point of the list is pedagogical coverage, not completeness:
# it deliberately mixes a nanobody (no light chain), a phospho-epitope, and
# structures whose antigen chain is NOT chain A.
SEED = [
    "5B8C",  # PD-1 + pembrolizumab  — antigen chain is NOT A (teaching point)
    "5E2W",  # phospho-tau + AT8     — SEP/TPO modified residues in the epitope
    "1BJ1",  # VEGF + bevacizumab
    "1N8Z",  # HER2 + trastuzumab
    "3NGB",  # HIV gp120 + VRC01
    "4G6K",  # beta-secretase Fab
    "5NGV",  # nanobody complex      — heavy chain only
    "6XDG",  # SARS-CoV-2 RBD + REGN antibodies
    "3W2D",  # influenza HA + antibody
    "4KRP",  # complement C5 + antibody
    "2FJG",  # VEGF + Fab
    "1YY9",  # EGFR + cetuximab
    "5DHV",  # IL-6 + antibody
    "6BF4",  # TNF + antibody
    "5VJ6",  # PCSK9 + antibody
    "6WPS",  # SARS-CoV-2 spike + S309
    "4YDK",  # HIV Env + antibody
    "1ADQ",  # IgG Fc + rheumatoid factor Fab
    "5KVD",  # Zika E protein + antibody
    "4XVT",  # Ebola GP + antibody
    "6O9H",  # RSV F + antibody
    "5U8R",  # nanobody + antigen
    "3IDX",  # influenza HA + CR6261
    "6WIT",  # SARS-CoV-2 RBD + nanobody
    "2VXQ",  # nanobody + amylase
    "4LVN",  # nanobody complex
    "5MY6",  # peptide antigen complex
    "6IEB",  # cytokine + Fab
    "5TE4",  # malaria CSP + antibody
    "7KMG",  # SARS-CoV-2 RBD + antibody
]

RCSB_ENTRY = "https://data.rcsb.org/rest/v1/core/entry/{}"
RCSB_ENTITY = "https://data.rcsb.org/rest/v1/core/polymer_entity/{}/{}"
RCSB_INSTANCE = "https://data.rcsb.org/rest/v1/core/polymer_entity_instance/{}/{}"
CIF_URL = "https://files.rcsb.org/download/{}.cif.gz"

CUTOFF = 4.5  # Å, heavy-atom distance. A convention, not a law — see S7.


def get_json(url: str, tries: int = 3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return json.load(r)
        except Exception as exc:  # RCSB rate-limits; back off rather than fail
            if i == tries - 1:
                print(f"  ! {url} -> {exc}", file=sys.stderr)
                return None
            time.sleep(2 * (i + 1))
    return None


def fetch_cif(pdb: str) -> pathlib.Path:
    CIF_DIR.mkdir(parents=True, exist_ok=True)
    dst = CIF_DIR / f"{pdb}.cif.gz"
    if dst.exists():
        return dst
    print(f"  downloading {pdb}.cif.gz")
    with urllib.request.urlopen(CIF_URL.format(pdb), timeout=90) as r:
        dst.write_bytes(r.read())
    time.sleep(1)
    return dst


def classify_chains(pdb: str):
    """Work out which chains are heavy, light and antigen.

    This is exactly the judgement call that S3 warns about: chain IDs carry no
    meaning, so the roles have to be derived from the entity descriptions and
    from whether ANARCI can number the sequence at all.
    """
    entry = get_json(RCSB_ENTRY.format(pdb))
    if not entry:
        return None
    n_entities = entry.get("rcsb_entry_info", {}).get("polymer_entity_count", 0)

    chains = []
    for eid in range(1, n_entities + 1):
        ent = get_json(RCSB_ENTITY.format(pdb, eid))
        if not ent:
            continue
        seq = ent.get("entity_poly", {}).get("pdbx_seq_one_letter_code_can", "").replace("\n", "")
        name = (ent.get("rcsb_polymer_entity", {}) or {}).get("pdbx_description", "") or ""
        ids = ent.get("rcsb_polymer_entity_container_identifiers", {}) or {}
        auth_ids = ids.get("auth_asym_ids") or ids.get("asym_ids") or []
        uni = None
        for ref in (ids.get("uniprot_ids") or []):
            uni = ref
            break
        chains.append({"entity": eid, "seq": seq, "name": name,
                       "auth_ids": auth_ids, "uniprot": uni})
    return chains


def number_chain(seq: str):
    """Return (chain_type, {scheme: {cdr: seq}}) or None if not an antibody V-domain."""
    try:
        from abnumber import Chain
    except ImportError:
        print("abnumber not installed — cannot compute CDRs", file=sys.stderr)
        raise

    out = {}
    ctype = None
    for scheme in ("imgt", "kabat", "chothia"):
        try:
            ch = Chain(seq[:150], scheme=scheme)
        except Exception:
            return None
        ctype = "H" if ch.is_heavy_chain() else "L"
        out[scheme] = {"cdr1": ch.cdr1_seq, "cdr2": ch.cdr2_seq, "cdr3": ch.cdr3_seq,
                       "v": str(ch)}
    return ctype, out


def compute_epitope(pdb: str, ab_chains: list[str], ag_chain: str):
    import gemmi
    st = gemmi.read_structure(str(fetch_cif(pdb)))
    st.setup_entities()
    st.remove_ligands_and_waters()
    st.remove_hydrogens()
    model = st[0]
    ns = gemmi.NeighborSearch(model, st.cell, CUTOFF + 1).populate()

    epitope, paratope, contacts = {}, {}, 0
    for ch in model:
        if ch.name != ag_chain:
            continue
        for res in ch:
            for at in res:
                for mark in ns.find_atoms(at.pos, "\0", radius=CUTOFF):
                    cra = mark.to_cra(model)
                    if cra.chain.name not in ab_chains:
                        continue
                    if at.pos.dist(cra.atom.pos) > CUTOFF:
                        continue
                    contacts += 1
                    epitope[(res.seqid.num, res.name)] = epitope.get((res.seqid.num, res.name), 0) + 1
                    key = (cra.chain.name, cra.residue.seqid.num, cra.residue.name)
                    paratope[key] = paratope.get(key, 0) + 1

    def one(name: str) -> str:
        info = gemmi.find_tabulated_residue(name)
        return (info.one_letter_code.upper() if info else "X") or "X"

    ep = ";".join(f"{one(n)}{num}" for (num, n) in sorted(epitope))
    pt = ";".join(f"{c}:{one(n)}{num}" for (c, num, n) in sorted(paratope))
    return ep, pt, len(epitope), contacts


FIELDS = [
    "Antibody_ID", "Antibody_name", "Target", "Target_UniProt",
    "PDB", "Hchain", "Lchain", "Antigen_chain",
    "VH_sequence", "VL_sequence",
    "CDRH1_IMGT", "CDRH2_IMGT", "CDRH3_IMGT",
    "CDRH3_Kabat", "CDRH3_Chothia",
    "CDRL3_IMGT",
    "Epitope_str", "Paratope_str", "N_epitope_residues", "N_contacts",
    "Evidence_tier", "Source_db", "Source_URL", "QC_flags",
]


def main() -> int:
    rows = []
    for pdb in SEED:
        print(f"[{pdb}]")
        chains = classify_chains(pdb)
        if not chains:
            print("  skip: no entity data")
            continue

        heavy = light = antigen = None
        for c in chains:
            if not c["seq"]:
                continue
            # A V-domain needs ~100 residues, but an antigen can be a short
            # peptide — 5E2W's tau fragment is ~15 residues. Using one length
            # floor for both roles silently drops every peptide-antigen complex.
            numbered = number_chain(c["seq"]) if len(c["seq"]) >= 90 else None
            if numbered:
                ctype, cdrs = numbered
                c["cdrs"] = cdrs
                if ctype == "H" and heavy is None:
                    heavy = c
                elif ctype == "L" and light is None:
                    light = c
            elif antigen is None and len(c["seq"]) >= 5:
                antigen = c

        if not heavy or not antigen:
            print("  skip: could not identify heavy chain + antigen")
            continue

        ab_ids = list(heavy["auth_ids"]) + (list(light["auth_ids"]) if light else [])
        ag_id = antigen["auth_ids"][0] if antigen["auth_ids"] else None
        if not ag_id:
            print("  skip: no antigen chain id")
            continue

        try:
            ep, pt, n_ep, n_ct = compute_epitope(pdb, ab_ids, ag_id)
        except Exception as exc:
            print(f"  skip: epitope failed ({exc})")
            continue

        flags = []
        if not light:
            flags.append("NO_LIGHT_CHAIN")          # nanobody / VHH — not an error
        if "X" in heavy["seq"]:
            flags.append("AMBIGUOUS_RESIDUE")
        if not n_ep:
            flags.append("NO_CONTACT_AT_CUTOFF")
        if not antigen["uniprot"]:
            flags.append("ANTIGEN_UNIPROT_MISSING")

        rows.append({
            "Antibody_ID": f"{pdb}_{heavy['auth_ids'][0]}",
            "Antibody_name": f"{pdb}_Fab" if light else f"{pdb}_VHH",
            "Target": antigen["name"][:80],
            "Target_UniProt": antigen["uniprot"] or "",
            "PDB": pdb,
            "Hchain": heavy["auth_ids"][0],
            "Lchain": light["auth_ids"][0] if light else "",
            "Antigen_chain": ag_id,
            "VH_sequence": heavy["cdrs"]["imgt"]["v"],
            "VL_sequence": light["cdrs"]["imgt"]["v"] if light else "",
            "CDRH1_IMGT": heavy["cdrs"]["imgt"]["cdr1"],
            "CDRH2_IMGT": heavy["cdrs"]["imgt"]["cdr2"],
            "CDRH3_IMGT": heavy["cdrs"]["imgt"]["cdr3"],
            "CDRH3_Kabat": heavy["cdrs"]["kabat"]["cdr3"],
            "CDRH3_Chothia": heavy["cdrs"]["chothia"]["cdr3"],
            "CDRL3_IMGT": light["cdrs"]["imgt"]["cdr3"] if light else "",
            "Epitope_str": ep,
            "Paratope_str": pt,
            "N_epitope_residues": n_ep,
            "N_contacts": n_ct,
            "Evidence_tier": "L1",
            "Source_db": "RCSB PDB",
            "Source_URL": f"https://www.rcsb.org/structure/{pdb}",
            "QC_flags": ";".join(flags) or "OK",
        })
        print(f"  ok  H={heavy['auth_ids'][0]} L={light['auth_ids'][0] if light else '-'} "
              f"Ag={ag_id}  epitope={n_ep} residues")

    if not rows:
        print("no rows produced", file=sys.stderr)
        return 1

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {len(rows)} rows -> {OUT.relative_to(HERE.parents[1])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
