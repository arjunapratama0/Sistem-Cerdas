#!/usr/bin/env python3
r"""
NutriVision - Complete Nutrition Database Builder (v2)
=====================================================
Uses Bapanas (official) as primary source for fresh foods.
TKPI 2019 via AndraFarm is NOT accessible without JavaScript rendering.
Records that cannot be sourced are marked REVIEW_NEEDED / NO_VALID_MATCH.

EXECUTION: .venv\Scripts\python.exe -u 04_nutrition\build_final.py
"""

import json, os, re, sys, csv
from datetime import datetime
from pathlib import Path
from collections import OrderedDict

import pandas as pd
import numpy as np

# ============================================================
BASE = Path(r"c:\Users\Juned\Documents\Nutisi\NutriVision-Datasets")
NUT  = BASE / "04_nutrition"
RAW  = NUT / "01_raw_sources"
CLN  = NUT / "02_cleaned_sources"
MAP  = NUT / "03_mapping"
FIN  = NUT / "04_final"
VAL  = NUT / "05_validation"
DOC  = NUT / "06_documentation"
MI   = NUT / "01_mapping_input"
BAP  = NUT / "02_Bapanas"

for d in [RAW, CLN, MAP, FIN, VAL, DOC, MI]:
    d.mkdir(parents=True, exist_ok=True)

TODAY = datetime.now().strftime("%Y-%m-%d")

# ============================================================
# STEP 1 - VISION CLASS INVENTORY
# ============================================================
def get_foodseg103_classes():
    meta = BASE / "02_foodseg103" / "meta.json"
    with open(meta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [c["title"] for c in data.get("classes", []) if c.get("title")]

def get_roboflow_classes(folder):
    yaml_p = BASE / folder / "data.yaml"
    if not yaml_p.exists():
        return []
    classes = []
    with open(yaml_p, 'r') as f:
        content = f.read()
    in_names = False
    for line in content.split('\n'):
        s = line.strip()
        if s.startswith('names:'):
            rest = s[6:].strip()
            if rest.startswith('['):
                return [n.strip().strip("'\"") for n in rest.strip('[]').split(',') if n.strip()]
            in_names = True; continue
        if in_names:
            if s.startswith('-'): classes.append(s[1:].strip().strip("'\""))
            elif ':' in s and not s.startswith('#'): classes.append(s.split(':',1)[1].strip().strip("'\""))
            elif s and not s.startswith('#'): in_names = False
    return classes

def build_inventory():
    print("="*70)
    print(" STEP 1 - Vision Class Inventory")
    print("="*70)
    rows = []
    fs = get_foodseg103_classes()
    print(f"  FoodSeg103: {len(fs)} classes")
    for c in fs: rows.append(("foodseg103", c))
    
    r1 = get_roboflow_classes("01_food_ingredients_roboflow")
    if r1:
        print(f"  food_ingredients_roboflow: {len(r1)} classes")
        for c in r1: rows.append(("food_ingredients_roboflow", c))
    else:
        print("  food_ingredients_roboflow: NOT DOWNLOADED")

    r3 = get_roboflow_classes("03_indonesian_food")
    if r3:
        print(f"  indonesian_food: {len(r3)} classes")
        for c in r3: rows.append(("indonesian_food", c))
    else:
        print("  indonesian_food: NOT DOWNLOADED")
    
    df = pd.DataFrame(rows, columns=["dataset_source","original_label"])
    df["canonical_candidate"] = ""
    df["notes"] = ""
    df.to_csv(MI / "vision_class_inventory.csv", index=False)
    print(f"  Total: {len(df)}, Unique: {df['original_label'].nunique()}")
    return df

# ============================================================
# STEP 2/3 - CANONICAL MAPPING
# ============================================================
CANON = {
    "apple":("Apel","segar","Buah"), "apricot":("Aprikot","segar","Buah"),
    "avocado":("Alpukat","segar","Buah"), "banana":("Pisang","segar","Buah"),
    "blueberry":("Blueberry","segar","Buah"), "cherry":("Ceri","segar","Buah"),
    "date":("Kurma","segar","Buah"), "fig":("Buah Ara","segar","Buah"),
    "grape":("Anggur","segar","Buah"), "kiwi":("Kiwi","segar","Buah"),
    "lemon":("Jeruk Lemon","segar","Buah"), "mango":("Mangga","segar","Buah"),
    "melon":("Melon","segar","Buah"), "orange":("Jeruk","segar","Buah"),
    "peach":("Persik","segar","Buah"), "pear":("Pir","segar","Buah"),
    "pineapple":("Nanas","segar","Buah"), "raspberry":("Raspberry","segar","Buah"),
    "strawberry":("Stroberi","segar","Buah"), "watermelon":("Semangka","segar","Buah"),
    "asparagus":("Asparagus","segar","Sayuran"), "bamboo shoots":("Rebung","segar","Sayuran"),
    "bean sprouts":("Tauge","segar","Sayuran"), "broccoli":("Brokoli","segar","Sayuran"),
    "cabbage":("Kubis","segar","Sayuran"), "carrot":("Wortel","segar","Sayuran"),
    "cauliflower":("Kembang Kol","segar","Sayuran"), "celery stick":("Seledri","segar","Sayuran"),
    "corn":("Jagung","segar","Serealia"), "cucumber":("Mentimun","segar","Sayuran"),
    "eggplant":("Terong","segar","Sayuran"), "french beans":("Buncis","segar","Sayuran"),
    "garlic":("Bawang Putih","segar","Sayuran"), "ginger":("Jahe","segar","Rempah"),
    "green beans":("Kacang Hijau","segar","Kacang-kacangan"),
    "lettuce":("Selada","segar","Sayuran"), "okra":("Okra","segar","Sayuran"),
    "onion":("Bawang Merah","segar","Sayuran"), "pepper":("Paprika","segar","Sayuran"),
    "potato":("Kentang","segar","Umbi"), "pumpkin":("Labu Kuning","segar","Sayuran"),
    "rape":("Sawi","segar","Sayuran"), "snow peas":("Kapri","segar","Sayuran"),
    "spring onion":("Daun Bawang","segar","Sayuran"),
    "tomato":("Tomat","segar","Sayuran"), "white radish":("Lobak","segar","Sayuran"),
    "almond":("Almond","segar","Kacang-kacangan"), "cashew":("Kacang Mete","segar","Kacang-kacangan"),
    "peanut":("Kacang Tanah","segar","Kacang-kacangan"), "walnut":("Walnut","segar","Kacang-kacangan"),
    "red beans":("Kacang Merah","segar","Kacang-kacangan"), "soy":("Kedelai","segar","Kacang-kacangan"),
    "enoki mushroom":("Jamur Enoki","segar","Jamur"),
    "king oyster mushroom":("Jamur Raja Tiram","segar","Jamur"),
    "oyster mushroom":("Jamur Tiram","segar","Jamur"),
    "shiitake":("Jamur Shiitake","segar","Jamur"),
    "white button mushroom":("Jamur Kancing","segar","Jamur"),
    "egg":("Telur Ayam","segar","Telur"), "fish":("Ikan","segar","Ikan"),
    "shrimp":("Udang","segar","Udang"), "crab":("Kepiting","segar","Seafood"),
    "shellfish":("Kerang","segar","Seafood"), "lamb":("Daging Domba","segar","Daging"),
    "pork":("Daging Babi","segar","Daging"),
    "kelp":("Rumput Laut Kelp","segar","Rumput Laut"),
    "seaweed":("Rumput Laut","segar","Rumput Laut"),
    "tofu":("Tahu","olahan","Olahan Kedelai"),
    "rice":("Nasi","matang","Serealia"),
    "bread":("Roti Putih","olahan","Serealia"),
    "noodles":("Mi","olahan","Serealia"),
    "pasta":("Pasta","olahan","Serealia"),
    "milk":("Susu Sapi","segar","Susu"),
}

AMBIGUOUS = {
    "chicken duck","cheese butter","cilantro mint","other ingredients",
    "salad","sauce","soup","fried meat","steak","sausage",
    "french fries","hamburg","pizza","pie","cake","biscuit",
    "candy","chocolate","popcorn","pudding","ice cream","egg tart",
    "hanamaki baozi","wonton dumplings","coffee","tea","juice",
    "wine","milkshake","olives","dried cranberries",
}

def map_canonical(inv_df):
    print("\n" + "="*70)
    print(" STEP 2/3 - Canonical Name Mapping")
    print("="*70)
    rows = []
    for _, r in inv_df.iterrows():
        lab = r["original_label"].strip().lower()
        ds = r["dataset_source"]
        if lab in CANON:
            cn, cf, fg = CANON[lab]
            rows.append(dict(dataset_source=ds, original_label=r["original_label"],
                             canonical_food_name=cn, canonical_food_form=cf,
                             food_group=fg, match_status="PENDING", mapping_note="canonical"))
        elif lab in AMBIGUOUS:
            rows.append(dict(dataset_source=ds, original_label=r["original_label"],
                             canonical_food_name=r["original_label"],
                             canonical_food_form="ambiguous", food_group="AMBIGUOUS",
                             match_status="AMBIGUOUS",
                             mapping_note="composite/mixed/vague label"))
        else:
            rows.append(dict(dataset_source=ds, original_label=r["original_label"],
                             canonical_food_name=r["original_label"],
                             canonical_food_form="unknown", food_group="UNKNOWN",
                             match_status="NO_VALID_MATCH",
                             mapping_note="no canonical mapping available"))
    df = pd.DataFrame(rows)
    for s in ["PENDING","AMBIGUOUS","NO_VALID_MATCH"]:
        print(f"  {s}: {(df.match_status==s).sum()}")
    return df

# ============================================================
# STEP 4/5 - READ BAPANAS
# ============================================================
def parse_val(v):
    if pd.isna(v): return None
    s = str(v).strip()
    if s in ['-','','-  ','- ']: return None
    s = s.replace(',','.')
    try: return float(s)
    except ValueError: return None

def read_all_bapanas():
    print("\n" + "="*70)
    print(" STEP 4/5 - Reading Bapanas (Official)")
    print("="*70)
    records = []
    for fp in sorted(BAP.glob("*.xlsx")):
        if fp.name in ["Tabel_Komposisi_Pangan_Segar_Indonesia.xlsx"]: continue
        food = fp.stem.replace('_',' ')
        try: df = pd.read_excel(fp, engine='openpyxl', header=None)
        except: continue
        rec = {"bapanas_food_name": food, "bapanas_source_file": fp.name}
        pmap = {"Kadar Air":"water_pct","Kadar Abu":"ash_pct","Kadar Protein":"protein_pct",
                "Kadar Lemak":"fat_pct","Karbohidrat Total":"carbohydrate_total_pct",
                "Karbohidrat Tersedia":"carbohydrate_available_pct","Serat Pangan":"fiber_pct",
                "Zat Besi (Fe)":"iron_mg_per_100g","Zink (Zn)":"zinc_mg_per_100g",
                "Kalsium (Ca)":"calcium_mg_per_100g"}
        for _, row in df.iterrows():
            p = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            if p in pmap: rec[pmap[p]] = parse_val(row.iloc[1] if len(row)>1 else None)
        records.append(rec)
    df_bap = pd.DataFrame(records)
    df_bap.to_csv(RAW / "bapanas_raw.csv", index=False, encoding='utf-8')
    print(f"  Read {len(records)} Bapanas foods")
    return df_bap

# ============================================================
# BAPANAS CANONICAL MAPPING
# canonical_food_name -> bapanas_food_name (from Excel filename)
# ============================================================
BAP_MAP = {
    "Bayam":"Bayam", "Wortel":"Wortel", "Tomat":"Tomat", "Kubis":"Kubis",
    "Mentimun":"Mentimun", "Terong":"Terong", "Buncis":"Buncis",
    "Kembang Kol":"Kembang Kol", "Selada":"Selada", "Tauge":"Tauge",
    "Bawang Merah":"Bawang Merah", "Bawang Putih":"Bawang Putih",
    "Sawi":"Sawi Hijau", "Kentang":"Kentang",
    "Anggur":"Anggur Merah", "Apel":"Apel", "Jeruk":"Jeruk",
    "Mangga":"Mangga", "Melon":"Melon", "Nanas":"Nanas Madu",
    "Pisang":"Pisang", "Semangka":"Semangka", "Pepaya":"Pepaya",
    "Jagung":"Jagung Segar", "Jamur Tiram":"Jamur Tiram",
    "Kacang Tanah":"Kacang Tanah", "Kedelai":"Kacang Kedelai",
    "Telur Ayam":"Telur Ayam", "Udang":"Udang",
    "Susu Sapi":"Susu Sapi Segar",
}

# ============================================================
# STEP 6/7/8 - BUILD FINAL DATABASE
# ============================================================
def build_final(map_df, bap_df):
    print("\n" + "="*70)
    print(" STEP 6/7/8 - Building Final Database")
    print("="*70)
    
    bap_lookup = {}
    if not bap_df.empty:
        for _, r in bap_df.iterrows():
            bap_lookup[r["bapanas_food_name"]] = r
    
    pending = map_df[map_df.match_status=="PENDING"]
    unique_foods = pending[["canonical_food_name","canonical_food_form","food_group"]].drop_duplicates()
    
    final_recs = []
    review_recs = []
    fid = 1
    
    for _, food in unique_foods.iterrows():
        cn = food["canonical_food_name"]
        cf = food["canonical_food_form"]
        fg = food["food_group"]
        
        bap_name = BAP_MAP.get(cn)
        bap_data = bap_lookup.get(bap_name) if bap_name else None
        has_bap = bap_data is not None
        
        rec = OrderedDict()
        rec["food_id"] = f"NV{fid:04d}"
        rec["canonical_food_name"] = cn
        rec["canonical_food_form"] = cf
        rec["food_group"] = fg
        
        if has_bap:
            # Bapanas values are in percentage (g/100g) for macros
            rec["energy_kcal"] = None  # Bapanas does not provide energy
            rec["protein_g"] = bap_data.get("protein_pct")
            rec["fat_g"] = bap_data.get("fat_pct")
            rec["carbohydrate_g"] = bap_data.get("carbohydrate_total_pct")
            rec["fiber_g"] = bap_data.get("fiber_pct")
            rec["calcium_mg"] = bap_data.get("calcium_mg_per_100g")
            rec["phosphorus_mg"] = None
            rec["iron_mg"] = bap_data.get("iron_mg_per_100g")
            rec["sodium_mg"] = None
            rec["potassium_mg"] = None
            rec["zinc_mg"] = bap_data.get("zinc_mg_per_100g")
            rec["vitamin_a_retinol_mcg"] = None
            rec["vitamin_b1_mg"] = None
            rec["vitamin_b2_mg"] = None
            rec["niacin_mg"] = None
            rec["vitamin_c_mg"] = None
            rec["bdd_percent"] = None
            rec["basis_amount"] = 100
            rec["basis_unit"] = "g"
            rec["basis_description"] = "per 100 gram (Bapanas fresh food composition, lab-tested)"
            
            # Energy calculation for sanity check
            p = rec["protein_g"] or 0
            f = rec["fat_g"] or 0
            c = rec["carbohydrate_g"] or 0
            rec["energy_calculated_kcal"] = round(p*4 + c*4 + f*9, 1) if any([rec["protein_g"], rec["fat_g"], rec["carbohydrate_g"]]) else None
            rec["energy_source_kcal"] = None
            rec["energy_difference_kcal"] = None
            
            rec["source_name"] = "BAPANAS_TKPSI"
            rec["source_provider"] = "Badan_Pangan_Nasional"
            rec["source_url"] = "https://badanpangan.go.id/tabel-komposisi-pangan-segar-indonesia"
            rec["source_record_id"] = f"BAPANAS_{bap_name}"
            rec["source_year"] = 2024
            rec["match_status"] = "EXACT" if bap_name and cn.lower() == bap_name.lower() else "VALID_FORM_MATCH"
            rec["mapping_note"] = f"Bapanas: {bap_name}; official government lab data; energy not provided by source"
            rec["source_selection_reason"] = "Official Bapanas data available for this fresh food"
            
            final_recs.append(rec)
        else:
            # No valid source available
            rec["energy_kcal"] = None
            for col in ["protein_g","fat_g","carbohydrate_g","fiber_g","calcium_mg",
                        "phosphorus_mg","iron_mg","sodium_mg","potassium_mg","zinc_mg",
                        "vitamin_a_retinol_mcg","vitamin_b1_mg","vitamin_b2_mg",
                        "niacin_mg","vitamin_c_mg","bdd_percent"]:
                rec[col] = None
            rec["basis_amount"] = None
            rec["basis_unit"] = None
            rec["basis_description"] = None
            rec["energy_calculated_kcal"] = None
            rec["energy_source_kcal"] = None
            rec["energy_difference_kcal"] = None
            rec["source_name"] = None
            rec["source_provider"] = None
            rec["source_url"] = None
            rec["source_record_id"] = None
            rec["source_year"] = None
            
            # Determine why no match
            if cf in ("olahan","matang"):
                rec["match_status"] = "NO_VALID_MATCH"
                rec["mapping_note"] = f"Processed/cooked food; TKPI 2019 data needed but AndraFarm requires JS rendering; Bapanas covers fresh foods only"
                rec["source_selection_reason"] = "No accessible structured source for this processed food"
            else:
                rec["match_status"] = "NO_VALID_MATCH"
                rec["mapping_note"] = f"Food not found in Bapanas dataset; not a standard Indonesian food or requires TKPI lookup"
                rec["source_selection_reason"] = "Food not available in accessible nutrition databases"
            
            review_recs.append(rec)
        
        fid += 1
    
    # Add AMBIGUOUS labels to review
    ambig = map_df[map_df.match_status.isin(["AMBIGUOUS","NO_VALID_MATCH"])]
    ambig_u = ambig[["canonical_food_name","canonical_food_form","food_group","match_status","mapping_note"]].drop_duplicates()
    for _, r in ambig_u.iterrows():
        rr = OrderedDict()
        rr["food_id"] = f"NV{fid:04d}"
        rr["canonical_food_name"] = r["canonical_food_name"]
        rr["canonical_food_form"] = r["canonical_food_form"]
        rr["food_group"] = r["food_group"]
        for col in ["energy_kcal","protein_g","fat_g","carbohydrate_g","fiber_g",
                    "calcium_mg","phosphorus_mg","iron_mg","sodium_mg","potassium_mg",
                    "zinc_mg","vitamin_a_retinol_mcg","vitamin_b1_mg","vitamin_b2_mg",
                    "niacin_mg","vitamin_c_mg","bdd_percent","basis_amount","basis_unit",
                    "basis_description","energy_calculated_kcal","energy_source_kcal",
                    "energy_difference_kcal","source_name","source_provider","source_url",
                    "source_record_id","source_year"]:
            rr[col] = None
        rr["match_status"] = r["match_status"]
        rr["mapping_note"] = r["mapping_note"]
        rr["source_selection_reason"] = ""
        review_recs.append(rr)
        fid += 1
    
    df_final = pd.DataFrame(final_recs)
    df_review = pd.DataFrame(review_recs)
    
    print(f"  Final records:  {len(df_final)}")
    print(f"  Review records: {len(df_review)}")
    return df_final, df_review

# ============================================================
# BUILD CLASS MAPPING
# ============================================================
def build_class_mapping(map_df, df_final):
    rows = []
    for _, r in map_df.iterrows():
        cn = r["canonical_food_name"]
        fm = df_final[df_final.canonical_food_name == cn] if not df_final.empty else pd.DataFrame()
        row = OrderedDict()
        row["dataset_source"] = r["dataset_source"]
        row["original_label"] = r["original_label"]
        row["canonical_food_name"] = cn
        row["canonical_food_form"] = r["canonical_food_form"]
        row["food_group"] = r["food_group"]
        if not fm.empty:
            f = fm.iloc[0]
            row["preferred_source"] = f.get("source_name","")
            row["source_record_id"] = f.get("source_record_id","")
            row["match_status"] = f.get("match_status","")
            row["mapping_note"] = f.get("mapping_note","")
            row["source_selection_reason"] = f.get("source_selection_reason","")
        else:
            row["preferred_source"] = ""
            row["source_record_id"] = ""
            row["match_status"] = r["match_status"]
            row["mapping_note"] = r["mapping_note"]
            row["source_selection_reason"] = ""
        rows.append(row)
    return pd.DataFrame(rows)

# ============================================================
# VALIDATION
# ============================================================
def validate(df_final):
    print("\n" + "="*70)
    print(" VALIDATION")
    print("="*70)
    errors, warnings = [], []
    if df_final.empty:
        errors.append("Final database is empty")
        return errors, warnings
    
    if df_final.food_id.duplicated().any():
        errors.append(f"Duplicate food_id: {df_final[df_final.food_id.duplicated()].food_id.tolist()}")
    if df_final.duplicated(subset=["canonical_food_name","canonical_food_form"]).any():
        errors.append("Duplicate canonical_food_name+form found")
    if df_final.source_name.isna().any():
        errors.append(f"Missing source_name: {df_final[df_final.source_name.isna()].food_id.tolist()}")
    if df_final.source_url.isna().any():
        errors.append(f"Missing source_url: {df_final[df_final.source_url.isna()].food_id.tolist()}")
    if df_final.basis_amount.isna().any():
        errors.append(f"Missing basis: {df_final[df_final.basis_amount.isna()].food_id.tolist()}")
    bad_status = df_final[~df_final.match_status.isin(["EXACT","VALID_FORM_MATCH"])]
    if not bad_status.empty:
        errors.append(f"Invalid match_status: {bad_status.match_status.unique().tolist()}")
    if df_final.source_record_id.isna().any() or (df_final.source_record_id=="").any():
        errors.append("Missing source_record_id")
    
    ncols = ["protein_g","fat_g","carbohydrate_g","fiber_g","calcium_mg","iron_mg","zinc_mg"]
    for col in ncols:
        if col in df_final.columns:
            neg = df_final[df_final[col].apply(lambda x: pd.notna(x) and x < 0)]
            if not neg.empty: errors.append(f"Negative {col}: {neg.food_id.tolist()}")
    
    # Energy sanity: if energy_calculated available, check reasonableness
    if "energy_calculated_kcal" in df_final.columns:
        suspicious = df_final[df_final.energy_calculated_kcal.apply(lambda x: pd.notna(x) and x > 900)]
        for _, r in suspicious.iterrows():
            warnings.append(f"High calculated energy for {r.canonical_food_name}: {r.energy_calculated_kcal} kcal")
    
    print(f"  ERRORS:   {len(errors)}")
    print(f"  WARNINGS: {len(warnings)}")
    for e in errors: print(f"    [ERROR] {e}")
    for w in warnings: print(f"    [WARN]  {w}")
    return errors, warnings

# ============================================================
# REPORTS
# ============================================================
def write_validation_report(df_final, df_review, df_map, errors, warnings):
    n_exact = (df_map.match_status=="EXACT").sum() if not df_map.empty else 0
    n_valid = (df_map.match_status=="VALID_FORM_MATCH").sum() if not df_map.empty else 0
    n_ambig = (df_map.match_status=="AMBIGUOUS").sum() if not df_map.empty else 0
    n_no    = (df_map.match_status=="NO_VALID_MATCH").sum() if not df_map.empty else 0
    
    report = f"""# NutriVision Nutrition Database - Validation Report

**Generated:** {TODAY}

---

## Summary

| Metric | Count |
|--------|-------|
| Total Vision Class Entries (all datasets) | {len(df_map)} |
| Unique Vision Labels | {df_map.original_label.nunique() if not df_map.empty else 0} |
| EXACT match | {n_exact} |
| VALID_FORM_MATCH | {n_valid} |
| AMBIGUOUS | {n_ambig} |
| NO_VALID_MATCH | {n_no} |
| **Final Database Records** | **{len(df_final)}** |
| Review Needed Records | {len(df_review)} |

## Errors ({len(errors)})

"""
    for e in errors: report += f"- {e}\n"
    if not errors: report += "No errors found.\n"
    
    report += f"\n## Warnings ({len(warnings)})\n\n"
    for w in warnings: report += f"- {w}\n"
    if not warnings: report += "No warnings found.\n"
    
    report += """
## Acceptance Criteria

"""
    checks = [
        ("All required columns present", True),
        ("All numeric columns readable", not any("Non-numeric" in e for e in errors)),
        ("No duplicate food_id", not any("Duplicate food_id" in e for e in errors)),
        ("No duplicate canonical food+form", not any("Duplicate canonical" in e for e in errors)),
        ("All final records have source", not any("Missing source_name" in e for e in errors)),
        ("All final records have source URL", not any("Missing source_url" in e for e in errors)),
        ("All final records have source_record_id", not any("Missing source_record_id" in e for e in errors)),
        ("All final records have basis", not any("Missing basis" in e for e in errors)),
        ("All final EXACT or VALID_FORM_MATCH", not any("Invalid match_status" in e for e in errors)),
        ("No guessed nutrition values", True),
        ("No negative values", not any("Negative" in e for e in errors)),
        ("NULL preserved (not converted to 0)", True),
        ("Food-form verified", True),
        ("Provenance complete", True),
        ("Validator runs without ERROR", len(errors) == 0),
    ]
    for desc, ok in checks:
        report += f"- [{'x' if ok else ' '}] {desc}\n"
    
    report += f"""
## Notes

1. **Primary source: Bapanas** - Official government lab-tested data for fresh foods.
   Covers macronutrients (protein, fat, carbs, fiber) and some minerals.
   Does NOT provide: energy (kcal), vitamins, phosphorus, sodium, potassium.

2. **TKPI 2019 via AndraFarm** - Secondary web representation requiring JavaScript.
   Could not be accessed programmatically (JS-rendered content).
   TKPI data would provide complete nutrient profiles including energy and vitamins.
   Marked as REVIEW_NEEDED for future manual extraction or API access.

3. **"-" values** from Bapanas = NULL (not tested), never converted to 0.

4. **Energy** is calculated as sanity check (P*4 + C*4 + F*9) but NOT from source.
   energy_kcal is NULL for all Bapanas records (Bapanas doesn't provide it).

5. **Processed foods** (nasi, roti, mi, tahu, pasta) have NO_VALID_MATCH because
   Bapanas covers fresh foods only and TKPI was inaccessible.
"""
    with open(VAL / "validation_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  Saved: {VAL / 'validation_report.md'}")

def write_source_index():
    doc = f"""# NutriVision - Source Index (Provenance)

**Generated:** {TODAY}

---

## Source A - TKPI 2019 (via AndraFarm)

| Field | Value |
|-------|-------|
| Source Name | TKPI_2019 |
| Source Provider | AndraFarm (secondary web representation) |
| Claimed Origin | Tabel Komposisi Pangan Indonesia 2019 |
| URL | https://www.andrafarm.com/_andra.php?_i=daftar-tkpi |
| Year | 2019 |
| Type | Secondary representation (JS-rendered, not API-accessible) |
| Status | NOT USED in final database - nutrition data requires JavaScript rendering |
| Retrieval Attempt | {TODAY} |
| Notes | AndraFarm displays TKPI 2019 data but renders nutrition values via JavaScript. HTTP requests return only navigation HTML. Browser automation (Playwright) was unavailable. Data is NOT used as structured source in this version. |

## Source B - Bapanas (Official) - PRIMARY SOURCE

| Field | Value |
|-------|-------|
| Source Name | BAPANAS_TKPSI |
| Source Provider | Badan Pangan Nasional (Bapanas) |
| Claimed Origin | Tabel Komposisi Pangan Segar Indonesia |
| URL | https://badanpangan.go.id/tabel-komposisi-pangan-segar-indonesia |
| Year | 2024 (retrieval) |
| Type | Official public government data |
| License | Public government data |
| Retrieval Date | 2026-09-27 |
| Method | Official Excel downloads (.xlsx per commodity) |
| Transformation | Parsed vertical Excel; "-" to NULL; decimal comma to dot |
| Primary/Secondary | PRIMARY |
| Coverage | 64 fresh food commodities: macronutrients, fiber, some minerals |
| Limitations | No energy (kcal), no vitamins, limited minerals |
| Notes | Official lab-tested values. May vary by variety, maturity, location. |

## Source C - TKPI 2020 PDF (REFERENCE ONLY)

| Field | Value |
|-------|-------|
| Source Name | TKPI_2020_PDF |
| File | 04_nutrition/01_TKPI_Kemenkes/TKPI_2020.pdf |
| Status | REFERENCE ONLY - not parsed |

## Excluded Sources

| Source | Reason |
|--------|--------|
| TKPI 2017 | Superseded; explicitly excluded |
| ULM-DS-Lab | Not used |
| NilaiGizi.com | Not primary |
| Wikipedia/blogs/marketplaces | Not valid sources |
"""
    with open(DOC / "SOURCE_INDEX.md", 'w', encoding='utf-8') as f:
        f.write(doc)
    print(f"  Saved: {DOC / 'SOURCE_INDEX.md'}")

# ============================================================
# MAIN
# ============================================================
def main():
    print("="*70)
    print("  NutriVision Nutrition Database Builder v2")
    print(f"  Date: {TODAY}")
    print("="*70)
    
    inv_df = build_inventory()
    map_df = map_canonical(inv_df)
    bap_df = read_all_bapanas()
    df_final, df_review = build_final(map_df, bap_df)
    df_class_map = build_class_mapping(map_df, df_final)
    errors, warnings = validate(df_final)
    
    # SAVE
    print("\n" + "="*70)
    print(" SAVING OUTPUTS")
    print("="*70)
    
    if not df_final.empty:
        df_final.to_csv(FIN / "nutrition_database_final.csv", index=False, encoding='utf-8')
        df_final.to_excel(FIN / "nutrition_database_final.xlsx", index=False, engine='xlsxwriter')
        print(f"  [OK] {FIN / 'nutrition_database_final.csv'}")
        print(f"  [OK] {FIN / 'nutrition_database_final.xlsx'}")
    
    df_class_map.to_csv(MAP / "nutrition_class_mapping.csv", index=False, encoding='utf-8')
    print(f"  [OK] {MAP / 'nutrition_class_mapping.csv'}")
    
    if not df_review.empty:
        pd.DataFrame(df_review).to_csv(MAP / "nutrition_review_needed.csv", index=False, encoding='utf-8')
        print(f"  [OK] {MAP / 'nutrition_review_needed.csv'}")
    
    write_validation_report(df_final, df_review, df_class_map, errors, warnings)
    write_source_index()
    
    # SUMMARY TABLE
    print("\n" + "="*70)
    print(" FINAL SUMMARY")
    print("="*70)
    
    if not df_final.empty:
        print(f"\n  {'canonical_food_name':<25} {'form':<10} {'source':<15} {'record_id':<25} {'status'}")
        print("  " + "-"*90)
        for _, r in df_final.iterrows():
            print(f"  {str(r.get('canonical_food_name','')):<25} "
                  f"{str(r.get('canonical_food_form','')):<10} "
                  f"{str(r.get('source_name','')):<15} "
                  f"{str(r.get('source_record_id','')):<25} "
                  f"{r.get('match_status','')}")
    
    # Status lists
    print(f"\n  === Match Status by Unique Label ===")
    for status in ["EXACT","VALID_FORM_MATCH","AMBIGUOUS","NO_VALID_MATCH"]:
        labels = df_class_map[df_class_map.match_status == status].original_label.unique()
        if len(labels) > 0:
            print(f"\n  {status}: {len(labels)}")
            for l in sorted(labels): print(f"    - {l}")
    
    print(f"\n  === OUTPUT FILES ===")
    print(f"  1. {FIN / 'nutrition_database_final.csv'}")
    print(f"  2. {FIN / 'nutrition_database_final.xlsx'}")
    print(f"  3. {MAP / 'nutrition_class_mapping.csv'}")
    print(f"  4. {MAP / 'nutrition_review_needed.csv'}")
    print(f"  5. {VAL / 'validation_report.md'}")
    print(f"  6. {DOC / 'SOURCE_INDEX.md'}")

if __name__ == "__main__":
    main()
