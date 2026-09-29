#!/usr/bin/env python3
"""
NutriVision Nutrition Database Builder
======================================
Senior Data Engineer + Nutrition Data Quality Auditor

This script:
1. Extracts class inventory from vision datasets (FoodSeg103, Roboflow status)
2. Reads Bapanas (official) fresh food nutrition data
3. Retrieves TKPI 2019 data from AndraFarm (secondary representation)
4. Maps vision classes -> canonical food names -> nutrition records
5. Validates everything
6. Produces final database

PROVENANCE:
- Bapanas = official public government source (badanpangan.go.id)
- TKPI 2019 via AndraFarm = secondary web representation of data labeled TKPI 2019
- TKPI 2020 PDF = REFERENCE ONLY, not used as primary structured source
"""

import json
import os
import re
import sys
import csv
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(r"c:\Users\Juned\Documents\Nutisi\NutriVision-Datasets")
NUTRITION_DIR = BASE_DIR / "04_nutrition"
RAW_SOURCES_DIR = NUTRITION_DIR / "01_raw_sources"
CLEANED_SOURCES_DIR = NUTRITION_DIR / "02_cleaned_sources"
MAPPING_DIR = NUTRITION_DIR / "03_mapping"
FINAL_DIR = NUTRITION_DIR / "04_final"
VALIDATION_DIR = NUTRITION_DIR / "05_validation"
DOCS_DIR = NUTRITION_DIR / "06_documentation"
MAPPING_INPUT_DIR = NUTRITION_DIR / "01_mapping_input"
BAPANAS_DIR = NUTRITION_DIR / "02_Bapanas"

RETRIEVAL_DATE = datetime.now().strftime("%Y-%m-%d")

# Ensure directories exist
for d in [RAW_SOURCES_DIR, CLEANED_SOURCES_DIR, MAPPING_DIR, FINAL_DIR,
          VALIDATION_DIR, DOCS_DIR, MAPPING_INPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ============================================================
# STEP 1: EXTRACT CLASS INVENTORY FROM VISION DATASETS
# ============================================================

def extract_foodseg103_classes():
    """Extract classes from FoodSeg103 meta.json."""
    meta_path = BASE_DIR / "02_foodseg103" / "meta.json"
    if not meta_path.exists():
        print(f"[WARN] FoodSeg103 meta.json not found at {meta_path}")
        return []

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    classes = []
    for cls in meta.get("classes", []):
        title = cls.get("title", "")
        if title:
            classes.append({
                "dataset_source": "foodseg103",
                "original_label": title,
                "canonical_candidate": "",
                "notes": f"id={cls.get('id', '')}"
            })
    return classes


def extract_roboflow_classes_from_yaml(dataset_dir, dataset_name):
    """Extract classes from data.yaml if available."""
    yaml_path = dataset_dir / "data.yaml"
    if not yaml_path.exists():
        return []

    classes = []
    with open(yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse YAML-like format manually (avoid pyyaml dependency)
    in_names = False
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('names:'):
            in_names = True
            # Check if inline list
            rest = line[len('names:'):].strip()
            if rest.startswith('['):
                # Inline list format
                names = rest.strip('[]').split(',')
                for name in names:
                    name = name.strip().strip("'\"")
                    if name:
                        classes.append({
                            "dataset_source": dataset_name,
                            "original_label": name,
                            "canonical_candidate": "",
                            "notes": ""
                        })
                in_names = False
            continue
        if in_names:
            if line.startswith('-'):
                name = line[1:].strip().strip("'\"")
                if name:
                    classes.append({
                        "dataset_source": dataset_name,
                        "original_label": name,
                        "canonical_candidate": "",
                        "notes": ""
                    })
            elif ':' in line and not line.startswith('#'):
                # numbered format: 0: name
                parts = line.split(':', 1)
                name = parts[1].strip().strip("'\"")
                if name:
                    classes.append({
                        "dataset_source": dataset_name,
                        "original_label": name,
                        "canonical_candidate": "",
                        "notes": ""
                    })
            elif line and not line.startswith('#'):
                in_names = False
    return classes


def build_class_inventory():
    """Build complete vision class inventory."""
    print("=" * 60)
    print("STEP 1: Building Vision Class Inventory")
    print("=" * 60)

    all_classes = []

    # FoodSeg103
    fs103 = extract_foodseg103_classes()
    print(f"  FoodSeg103: {len(fs103)} classes")
    all_classes.extend(fs103)

    # Roboflow datasets (check if downloaded)
    roboflow1_dir = BASE_DIR / "01_food_ingredients_roboflow"
    roboflow1_yaml = extract_roboflow_classes_from_yaml(roboflow1_dir, "food_ingredients_roboflow")
    if roboflow1_yaml:
        print(f"  food_ingredients_roboflow: {len(roboflow1_yaml)} classes")
        all_classes.extend(roboflow1_yaml)
    else:
        print(f"  food_ingredients_roboflow: data.yaml not found (dataset not yet downloaded)")

    roboflow3_dir = BASE_DIR / "03_indonesian_food"
    roboflow3_yaml = extract_roboflow_classes_from_yaml(roboflow3_dir, "indonesian_food")
    if roboflow3_yaml:
        print(f"  indonesian_food: {len(roboflow3_yaml)} classes")
        all_classes.extend(roboflow3_yaml)
    else:
        print(f"  indonesian_food: data.yaml not found (dataset not yet downloaded)")

    # Save inventory
    df = pd.DataFrame(all_classes)
    out_path = MAPPING_INPUT_DIR / "vision_class_inventory.csv"
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"\n  Saved: {out_path}")
    print(f"  Total classes: {len(all_classes)}")

    # Find overlaps
    if len(all_classes) > 0:
        labels_by_ds = {}
        for c in all_classes:
            ds = c['dataset_source']
            if ds not in labels_by_ds:
                labels_by_ds[ds] = set()
            labels_by_ds[ds].add(c['original_label'].lower())

        datasets = list(labels_by_ds.keys())
        for i in range(len(datasets)):
            for j in range(i + 1, len(datasets)):
                overlap = labels_by_ds[datasets[i]] & labels_by_ds[datasets[j]]
                if overlap:
                    print(f"\n  Overlap between {datasets[i]} and {datasets[j]}: {len(overlap)}")
                    for o in sorted(overlap):
                        print(f"    - {o}")

    return df


# ============================================================
# STEP 2: STANDARDIZE CANONICAL NAMES
# ============================================================

# Mapping: original_label -> (canonical_food_name, canonical_food_form, food_group)
# ONLY for foods that have clear, unambiguous identities.
# Composite/ambiguous labels get AMBIGUOUS status.
CANONICAL_MAP = {
    # === FRESH FRUITS ===
    "apple": ("Apel", "segar", "Buah"),
    "apricot": ("Aprikot", "segar", "Buah"),
    "avocado": ("Alpukat", "segar", "Buah"),
    "banana": ("Pisang", "segar", "Buah"),
    "blueberry": ("Blueberry", "segar", "Buah"),
    "cherry": ("Ceri", "segar", "Buah"),
    "date": ("Kurma", "segar", "Buah"),
    "fig": ("Buah Ara", "segar", "Buah"),
    "grape": ("Anggur", "segar", "Buah"),
    "kiwi": ("Kiwi", "segar", "Buah"),
    "lemon": ("Jeruk Lemon", "segar", "Buah"),
    "mango": ("Mangga", "segar", "Buah"),
    "melon": ("Melon", "segar", "Buah"),
    "orange": ("Jeruk", "segar", "Buah"),
    "peach": ("Persik", "segar", "Buah"),
    "pear": ("Pir", "segar", "Buah"),
    "pineapple": ("Nanas", "segar", "Buah"),
    "raspberry": ("Raspberry", "segar", "Buah"),
    "strawberry": ("Stroberi", "segar", "Buah"),
    "watermelon": ("Semangka", "segar", "Buah"),
    # === FRESH VEGETABLES ===
    "asparagus": ("Asparagus", "segar", "Sayuran"),
    "bamboo shoots": ("Rebung", "segar", "Sayuran"),
    "bean sprouts": ("Tauge", "segar", "Sayuran"),
    "broccoli": ("Brokoli", "segar", "Sayuran"),
    "cabbage": ("Kubis", "segar", "Sayuran"),
    "carrot": ("Wortel", "segar", "Sayuran"),
    "cauliflower": ("Kembang Kol", "segar", "Sayuran"),
    "celery stick": ("Seledri", "segar", "Sayuran"),
    "corn": ("Jagung", "segar", "Sayuran"),
    "cucumber": ("Mentimun", "segar", "Sayuran"),
    "eggplant": ("Terong", "segar", "Sayuran"),
    "french beans": ("Buncis", "segar", "Sayuran"),
    "garlic": ("Bawang Putih", "segar", "Sayuran"),
    "ginger": ("Jahe", "segar", "Sayuran"),
    "green beans": ("Kacang Hijau", "segar", "Kacang-kacangan"),
    "lettuce": ("Selada", "segar", "Sayuran"),
    "okra": ("Okra", "segar", "Sayuran"),
    "onion": ("Bawang Merah", "segar", "Sayuran"),
    "pepper": ("Paprika", "segar", "Sayuran"),
    "potato": ("Kentang", "segar", "Umbi"),
    "pumpkin": ("Labu Kuning", "segar", "Sayuran"),
    "rape": ("Sawi", "segar", "Sayuran"),
    "snow peas": ("Kapri", "segar", "Sayuran"),
    "spring onion": ("Daun Bawang", "segar", "Sayuran"),
    "tomato": ("Tomat", "segar", "Sayuran"),
    "white radish": ("Lobak", "segar", "Sayuran"),
    # === NUTS & SEEDS ===
    "almond": ("Almond", "segar", "Kacang-kacangan"),
    "cashew": ("Kacang Mete", "segar", "Kacang-kacangan"),
    "peanut": ("Kacang Tanah", "segar", "Kacang-kacangan"),
    "walnut": ("Walnut", "segar", "Kacang-kacangan"),
    "red beans": ("Kacang Merah", "segar", "Kacang-kacangan"),
    "soy": ("Kedelai", "segar", "Kacang-kacangan"),
    # === MUSHROOMS ===
    "enoki mushroom": ("Jamur Enoki", "segar", "Jamur"),
    "king oyster mushroom": ("Jamur Raja Tiram", "segar", "Jamur"),
    "oyster mushroom": ("Jamur Tiram", "segar", "Jamur"),
    "shiitake": ("Jamur Shiitake", "segar", "Jamur"),
    "white button mushroom": ("Jamur Kancing", "segar", "Jamur"),
    # === PROTEINS (fresh/generic form) ===
    "egg": ("Telur Ayam", "segar", "Telur"),
    "fish": ("Ikan", "segar", "Ikan"),
    "shrimp": ("Udang", "segar", "Udang"),
    "crab": ("Kepiting", "segar", "Seafood"),
    "shellfish": ("Kerang", "segar", "Seafood"),
    "lamb": ("Daging Domba", "segar", "Daging"),
    "pork": ("Daging Babi", "segar", "Daging"),
    # === SEAWEED ===
    "kelp": ("Rumput Laut Kelp", "segar", "Rumput Laut"),
    "seaweed": ("Rumput Laut", "segar", "Rumput Laut"),
    # === PROCESSED/PREPARED — need specific form match ===
    "tofu": ("Tahu", "olahan", "Olahan Kedelai"),
    "rice": ("Nasi", "matang", "Serealia"),
    "bread": ("Roti Putih", "olahan", "Serealia"),
    "noodles": ("Mi", "olahan", "Serealia"),
    "pasta": ("Pasta", "olahan", "Serealia"),
    # === DAIRY ===
    "milk": ("Susu Sapi", "segar", "Susu"),
    # === AMBIGUOUS / COMPOSITE — these CANNOT be mapped to a single nutrition record ===
    # "chicken duck" — combines two different animals
    # "cheese butter" — combines two different dairy products
    # "cilantro mint" — combines two different herbs
    # "other ingredients" — catch-all, no specific food
    # "salad" — mixed dish
    # "sauce" — varied composition
    # "soup" — varied composition
    # "fried meat" — unknown base meat, processed
    # "steak" — could be beef/other, processed
    # "sausage" — processed, varied composition
    # "french fries" — processed potato
    # "hamburg" — processed mixed
    # "pizza" — processed mixed
    # "pie" — processed mixed
    # "cake" — processed mixed
    # "biscuit" — processed mixed
    # "candy" — processed mixed
    # "chocolate" — processed
    # "popcorn" — processed corn
    # "pudding" — processed mixed
    # "ice cream" — processed mixed
    # "egg tart" — processed mixed
    # "hanamaki baozi" — processed mixed
    # "wonton dumplings" — processed mixed
    # "coffee" — beverage
    # "tea" — beverage
    # "juice" — beverage
    # "wine" — beverage
    # "milkshake" — beverage
    # "olives" — not common in Indonesian nutrition tables
    # "dried cranberries" — processed fruit
}

# These labels are AMBIGUOUS and cannot be mapped to a single nutrition record
AMBIGUOUS_LABELS = {
    "chicken duck", "cheese butter", "cilantro mint", "other ingredients",
    "salad", "sauce", "soup", "fried meat", "steak", "sausage",
    "french fries", "hamburg", "pizza", "pie", "cake", "biscuit",
    "candy", "chocolate", "popcorn", "pudding", "ice cream", "egg tart",
    "hanamaki baozi", "wonton dumplings", "coffee", "tea", "juice",
    "wine", "milkshake", "olives", "dried cranberries"
}


def standardize_names(inventory_df):
    """Apply canonical name standardization."""
    print("\n" + "=" * 60)
    print("STEP 3: Standardizing Canonical Names")
    print("=" * 60)

    records = []
    for _, row in inventory_df.iterrows():
        label = row['original_label'].strip().lower()
        ds = row['dataset_source']

        if label in CANONICAL_MAP:
            cname, cform, fgroup = CANONICAL_MAP[label]
            records.append({
                "dataset_source": ds,
                "original_label": row['original_label'],
                "canonical_food_name": cname,
                "canonical_food_form": cform,
                "food_group": fgroup,
                "match_status": "PENDING_NUTRITION_MATCH",
                "mapping_note": "Canonical mapping applied"
            })
        elif label in AMBIGUOUS_LABELS:
            records.append({
                "dataset_source": ds,
                "original_label": row['original_label'],
                "canonical_food_name": row['original_label'],
                "canonical_food_form": "ambiguous",
                "food_group": "AMBIGUOUS",
                "match_status": "AMBIGUOUS",
                "mapping_note": "Label is composite, mixed, or too vague to map to single nutrition record"
            })
        else:
            records.append({
                "dataset_source": ds,
                "original_label": row['original_label'],
                "canonical_food_name": row['original_label'],
                "canonical_food_form": "unknown",
                "food_group": "UNKNOWN",
                "match_status": "NO_VALID_MATCH",
                "mapping_note": "No canonical mapping defined; food not identifiable or not in Indonesian nutrition tables"
            })

    df = pd.DataFrame(records)
    print(f"  MAPPED: {len(df[df['match_status'] == 'PENDING_NUTRITION_MATCH'])}")
    print(f"  AMBIGUOUS: {len(df[df['match_status'] == 'AMBIGUOUS'])}")
    print(f"  NO_VALID_MATCH: {len(df[df['match_status'] == 'NO_VALID_MATCH'])}")

    return df


# ============================================================
# STEP 4 & 5: READ NUTRITION SOURCES
# ============================================================

def read_bapanas_data():
    """Read Bapanas official Excel data."""
    print("\n" + "=" * 60)
    print("STEP: Reading Bapanas Data")
    print("=" * 60)

    master_path = BAPANAS_DIR / "Tabel_Komposisi_Pangan_Segar_Indonesia.xlsx"
    if not master_path.exists():
        print(f"  [WARN] Bapanas master file not found: {master_path}")
        return pd.DataFrame()

    try:
        df = pd.read_excel(master_path, engine='openpyxl')
        print(f"  Bapanas master: {df.shape[0]} rows x {df.shape[1]} columns")
        print(f"  Columns: {df.columns.tolist()}")
        print(f"  First 3 rows:")
        print(df.head(3).to_string())
        return df
    except Exception as e:
        print(f"  [ERROR] Failed to read Bapanas master: {e}")

    # Try reading individual Excel files
    print("  Attempting to read individual Excel files...")
    all_data = []
    for xlsx_file in sorted(BAPANAS_DIR.glob("*.xlsx")):
        if xlsx_file.name == "Tabel_Komposisi_Pangan_Segar_Indonesia.xlsx":
            continue
        try:
            df_item = pd.read_excel(xlsx_file, engine='openpyxl')
            df_item['_source_file'] = xlsx_file.name
            all_data.append(df_item)
        except Exception as e:
            print(f"    [WARN] Failed to read {xlsx_file.name}: {e}")

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        print(f"  Read {len(all_data)} individual files, {combined.shape[0]} total rows")
        return combined

    return pd.DataFrame()


def read_bapanas_individual_files():
    """Read individual Bapanas Excel files and extract nutrition data."""
    print("\n  Reading individual Bapanas Excel files for structure...")

    sample_files = list(BAPANAS_DIR.glob("*.xlsx"))
    sample_files = [f for f in sample_files
                    if f.name != "Tabel_Komposisi_Pangan_Segar_Indonesia.xlsx"
                    and f.name != "page.html"]

    if not sample_files:
        return {}

    # Read first file to understand structure
    sample = sample_files[0]
    try:
        df = pd.read_excel(sample, engine='openpyxl', header=None)
        print(f"  Sample file: {sample.name}")
        print(f"  Shape: {df.shape}")
        print(df.to_string())
        return {"sample_df": df, "sample_name": sample.name}
    except Exception as e:
        print(f"  [ERROR] {e}")
        return {}


def parse_bapanas_nutrition(bapanas_df):
    """Parse Bapanas data into standardized nutrition records."""
    print("\n  Parsing Bapanas nutrition data...")

    if bapanas_df.empty:
        return []

    records = []
    # Will be populated based on actual column structure
    return records


# ============================================================
# TKPI 2019 DATA (from AndraFarm secondary representation)
# ============================================================

def build_tkpi_search_index(all_items_content_path):
    """
    Build a search index from the TKPI listing page.
    Each item has a code (APxxx) and name.
    """
    items = []
    with open(all_items_content_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Pattern: [Food Name](https://www.andrafarm.com/_andra.php?_i=daftar-tkpi&kmakan=APxxx#AndraFarm)
            match = re.findall(r'\[([^\]]+)\]\(https://www\.andrafarm\.com/_andra\.php\?_i=daftar-tkpi&kmakan=(AP\d+)', line)
            for name, code in match:
                items.append({"code": code, "name": name})

    print(f"  TKPI index: {len(items)} food items found")
    return items


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print("=" * 70)
    print("  NutriVision Nutrition Database Builder")
    print("  Date: " + RETRIEVAL_DATE)
    print("=" * 70)

    # === STEP 1: Class Inventory ===
    inventory_df = build_class_inventory()

    # === STEP 3: Standardize Names ===
    mapping_df = standardize_names(inventory_df)

    # === Read Bapanas ===
    bapanas_df = read_bapanas_data()

    # === Read individual Bapanas files for structure ===
    bapanas_sample = read_bapanas_individual_files()

    # === Build TKPI index ===
    tkpi_content_path = Path(r"C:\Users\Juned\.gemini\antigravity-ide\brain\4d275ead-c35b-473b-8b9c-7ce41f646874\.system_generated\steps\58\content.md")
    tkpi_items = []
    if tkpi_content_path.exists():
        tkpi_items = build_tkpi_search_index(tkpi_content_path)

    # === Summary ===
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Vision classes: {len(inventory_df)}")
    print(f"  Mappable (with canonical name): {len(mapping_df[mapping_df['match_status'] == 'PENDING_NUTRITION_MATCH'])}")
    print(f"  Ambiguous: {len(mapping_df[mapping_df['match_status'] == 'AMBIGUOUS'])}")
    print(f"  No valid match: {len(mapping_df[mapping_df['match_status'] == 'NO_VALID_MATCH'])}")
    print(f"  Bapanas records: {len(bapanas_df)}")
    print(f"  TKPI items: {len(tkpi_items)}")

    # Print unique canonical foods that need nutrition data
    mappable = mapping_df[mapping_df['match_status'] == 'PENDING_NUTRITION_MATCH']
    unique_canonical = mappable[['canonical_food_name', 'canonical_food_form', 'food_group']].drop_duplicates()
    print(f"\n  Unique canonical foods requiring nutrition data: {len(unique_canonical)}")
    for _, row in unique_canonical.iterrows():
        print(f"    {row['canonical_food_name']} ({row['canonical_food_form']}) [{row['food_group']}]")

    # Save intermediate mapping
    mapping_df.to_csv(MAPPING_DIR / "vision_class_mapping_draft.csv", index=False, encoding='utf-8')
    print(f"\n  Draft mapping saved: {MAPPING_DIR / 'vision_class_mapping_draft.csv'}")

    return {
        "inventory_df": inventory_df,
        "mapping_df": mapping_df,
        "bapanas_df": bapanas_df,
        "tkpi_items": tkpi_items,
        "unique_canonical": unique_canonical
    }


if __name__ == "__main__":
    results = main()
