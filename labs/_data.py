"""Shared loader for the labs.

The sample dataset ships with the repo and was built entirely from public RCSB
data by data/build_sample.py, so every lab runs offline out of the box.
"""
import pathlib
import sys

DATA = pathlib.Path(__file__).resolve().parent / "data" / "sample_antibodies.csv"


def load():
    """Return the sample dataset as a pandas DataFrame."""
    try:
        import pandas as pd
    except ImportError:
        sys.exit("需要 pandas：pip install -r labs/requirements.txt")
    if not DATA.exists():
        sys.exit(f"找不到样本数据 {DATA}\n请先跑：python labs/data/build_sample.py")
    # keep_default_na=False matters: without it, pandas turns an empty Lchain
    # (a legitimate single-domain antibody) into NaN, and every downstream
    # "does this row have a light chain" check silently changes meaning.
    return pd.read_csv(DATA, keep_default_na=False, dtype=str)


def rule(title=""):
    print(f"\n{'─' * 68}")
    if title:
        print(title)
        print("─" * 68)
