import csv
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data_pipeline/data/transfermarkt.csv')

def get_comparables(target_fee: float):
    if not os.path.exists(CSV_PATH):
        return []
        
    comparables = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fee = float(row['fee_m'])
            diff = abs(fee - target_fee)
            # Create a copy with the diff to sort by similarity
            comp = dict(row)
            comp["similarity_diff"] = diff
            comparables.append(comp)
            
    # Sort by the closest fee match
    comparables.sort(key=lambda x: x["similarity_diff"])
    
    # Return top 5, excluding the synthetic diff key for cleaner API JSON
    top_5 = comparables[:5]
    for c in top_5:
        del c["similarity_diff"]
        
    return top_5
