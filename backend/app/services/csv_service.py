"""
CSV Comparable Transfer Service.

Ported from Dev 1's scoutr-backend. Provides comparable historical transfers
by searching the Transfermarkt CSV data for similar fee amounts.
"""

import csv
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data_pipeline/data/transfermarkt.csv')


def get_comparables(target_fee: float, limit: int = 5):
    """
    Find the top comparable historical transfers closest to the target fee.
    Returns top `limit` results sorted by fee similarity.
    """
    if not os.path.exists(CSV_PATH):
        return []

    comparables = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                fee = float(row.get('fee_m', 0))
            except (ValueError, TypeError):
                continue
            diff = abs(fee - target_fee)
            comp = dict(row)
            comp["similarity_diff"] = diff
            comparables.append(comp)

    # Sort by closest fee match
    comparables.sort(key=lambda x: x["similarity_diff"])

    # Return top results, excluding the synthetic diff key
    top = comparables[:limit]
    for c in top:
        del c["similarity_diff"]

    return top
