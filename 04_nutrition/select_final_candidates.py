#!/usr/bin/env python3
"""Strict candidate selection for NutriVision - 15-25 strong classes."""

import pandas as pd

OUT = r'c:\Users\Juned\Documents\Nutisi\NutriVision-Datasets\04_nutrition\01_mapping_input'

df = pd.read_csv(f'{OUT}\\final_class_candidates.csv')

# Final 23 candidates - strictly curated
FINAL_SELECTION = [
    # Karbohidrat (4) - sumber energi utama
    'rice', 'potato', 'corn', 'bread',
    # Protein Hewani (4) - sumber protein
    'egg', 'fish', 'chicken', 'shrimp',
    # Protein Nabati (2)
    'tofu', 'red beans',
    # Sayuran (8) - sayuran umum
    'carrot', 'tomato', 'broccoli', 'cabbage',
    'cucumber', 'onion', 'eggplant', 'cauliflower',
    # Buah (5) - buah yang umum
    'banana', 'apple', 'orange', 'watermelon', 'mango',
]

REASONS = {
    'rice': 'Karbohidrat pokok Indonesia; 670 instances; FoodSeg103',
    'potato': 'Karbohidrat umum; 1677 instances; 2 dataset cross-validated',
    'corn': 'Sumber karbohidrat; 657 instances; 2 dataset',
    'bread': 'Karbohidrat olahan; 1584 instances; 2 dataset',
    'egg': 'Protein hewani paling umum; 1123 instances; 2 dataset',
    'fish': 'Protein hewani utama; 359 instances; 2 dataset',
    'chicken': 'Protein hewani terpenting; 26 instances; hanya DS1 tapi kritis untuk use case',
    'shrimp': 'Protein hewani/seafood; 144 instances; FoodSeg103',
    'tofu': 'Protein nabati/olahan kedelai; 86 instances; 2 dataset; makanan Indonesia',
    'red beans': 'Protein nabati; 164 instances; 2 dataset',
    'carrot': 'Sayuran bergizi; 1486 instances; 2 dataset; kaya vitamin A',
    'tomato': 'Sayuran paling umum; 1474 instances; 2 dataset',
    'broccoli': 'Sayuran bergizi tinggi; 1112 instances; 2 dataset',
    'cabbage': 'Sayuran umum Indonesia; 472 instances; 2 dataset',
    'cucumber': 'Sayuran umum; 726 instances; 2 dataset',
    'onion': 'Bumbu dapur utama; 693 instances; 2 dataset',
    'eggplant': 'Sayuran umum (terong); 338 instances; 2 dataset',
    'cauliflower': 'Sayuran bergizi; 288 instances; 2 dataset',
    'banana': 'Buah paling umum Indonesia; 357 instances; 2 dataset',
    'apple': 'Buah umum; 159 instances; 2 dataset',
    'orange': 'Buah kaya vitamin C; 256 instances; 2 dataset',
    'watermelon': 'Buah populer; 46 instances; 2 dataset',
    'mango': 'Buah tropis populer; 55 instances; FoodSeg103',
}

rows = []
for canon in FINAL_SELECTION:
    match = df[df.final_candidate == canon]
    if match.empty:
        print(f"  WARNING: {canon} not found in candidates, skipping")
        continue
    r = match.iloc[0]
    total = int(r['total_images'])
    source = r['source_dataset']
    labels = r['original_labels']
    fg = r['food_group']
    reason = REASONS.get(canon, r['reason'])
    
    multi = ',' in str(source)
    if total >= 100 and multi:
        conf = 'HIGH'
    elif total >= 50 or multi:
        conf = 'MEDIUM'
    else:
        conf = 'LOW'
    
    rows.append({
        'final_candidate': canon,
        'food_group': fg,
        'source_dataset': source,
        'original_labels': labels,
        'total_images': total,
        'confidence': conf,
        'reason': reason,
        'nutrition_mapping_status': 'NOT_CHECKED'
    })

df_final = pd.DataFrame(rows)
df_final.to_csv(f'{OUT}\\final_class_candidates.csv', index=False, encoding='utf-8')

# Print summary
high_c = (df_final.confidence == "HIGH").sum()
med_c = (df_final.confidence == "MEDIUM").sum()
low_c = (df_final.confidence == "LOW").sum()

print(f"Final candidates: {len(df_final)}")
print(f"  HIGH:   {high_c}")
print(f"  MEDIUM: {med_c}")
print(f"  LOW:    {low_c}")
print()

hdr = f"{'Candidate':<20} {'Group':<18} {'Images':>8} {'Conf':<8} Source"
print(hdr)
print("-" * 90)
for _, r in df_final.iterrows():
    print(f"{r['final_candidate']:<20} {r['food_group']:<18} {r['total_images']:>8} {r['confidence']:<8} {r['source_dataset']}")

# Food group distribution
print()
print("Food group distribution:")
for fg in df_final.food_group.unique():
    count = (df_final.food_group == fg).sum()
    print(f"  {fg}: {count}")
