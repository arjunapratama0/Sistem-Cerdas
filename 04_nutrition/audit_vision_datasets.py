#!/usr/bin/env python3
r"""
NutriVision Vision Dataset Audit
=================================
Comprehensive audit of all 3 vision datasets.
NO training, NO merging, NO modifications to original data.
"""

import json, os, re, sys, csv, glob
from pathlib import Path
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime

import pandas as pd
import numpy as np

BASE = Path(r"c:\Users\Juned\Documents\Nutisi\NutriVision-Datasets")
DS1  = BASE / "01_food_ingredients_roboflow"
DS2  = BASE / "02_foodseg103"
DS3  = BASE / "03_indonesian_food"
OUT_SOURCES = BASE / "00_sources"
OUT_MAPPING = BASE / "04_nutrition" / "01_mapping_input"

OUT_SOURCES.mkdir(parents=True, exist_ok=True)
OUT_MAPPING.mkdir(parents=True, exist_ok=True)

TODAY = datetime.now().strftime("%Y-%m-%d")

# ============================================================
# HELPER: count files
# ============================================================
def count_files(folder, exts=('.jpg','.jpeg','.png','.bmp','.webp')):
    if not folder.exists():
        return 0
    return sum(1 for f in folder.rglob('*') if f.suffix.lower() in exts)

def count_files_flat(folder, exts=('.jpg','.jpeg','.png','.bmp','.webp')):
    if not folder.exists():
        return 0
    return sum(1 for f in folder.iterdir() if f.suffix.lower() in exts)

def count_txt_labels(folder):
    """Count YOLO label files."""
    if not folder.exists():
        return 0
    return sum(1 for f in folder.iterdir() if f.suffix.lower() == '.txt')

# ============================================================
# DATASET 1: Food Ingredients Roboflow
# ============================================================
def audit_ds1():
    print("="*70)
    print(" A. FOOD INGREDIENTS ROBOFLOW (01_food_ingredients_roboflow)")
    print("="*70)
    
    # Read data.yaml
    with open(DS1 / "data.yaml", 'r') as f:
        content = f.read()
    
    # Extract class names from inline list
    names_match = re.search(r"names:\s*\[(.+)\]", content)
    classes = [n.strip().strip("'\"") for n in names_match.group(1).split(',')] if names_match else []
    nc = int(re.search(r"nc:\s*(\d+)", content).group(1))
    
    print(f"  Classes declared (nc): {nc}")
    print(f"  Classes in names list: {len(classes)}")
    
    # Count images per split
    train_img = DS1 / "train" / "images"
    valid_img = DS1 / "valid" / "images"
    test_img  = DS1 / "test"  / "images"
    train_lbl = DS1 / "train" / "labels"
    valid_lbl = DS1 / "valid" / "labels"
    test_lbl  = DS1 / "test"  / "labels"
    
    ti = count_files_flat(train_img) if train_img.exists() else 0
    vi = count_files_flat(valid_img) if valid_img.exists() else 0
    tei = count_files_flat(test_img) if test_img.exists() else 0
    tl = count_txt_labels(train_lbl) if train_lbl.exists() else 0
    vl = count_txt_labels(valid_lbl) if valid_lbl.exists() else 0
    tel = count_txt_labels(test_lbl) if test_lbl.exists() else 0
    
    print(f"  Train images: {ti}, labels: {tl}")
    print(f"  Valid images: {vi}, labels: {vl}")
    print(f"  Test images:  {tei}, labels: {tel}")
    print(f"  Total images: {ti+vi+tei}")
    
    # Count instances per class from YOLO labels
    class_instances = {"train": Counter(), "valid": Counter(), "test": Counter()}
    
    for split, lbl_dir in [("train", train_lbl), ("valid", valid_lbl), ("test", test_lbl)]:
        if not lbl_dir.exists():
            continue
        for lbl_file in lbl_dir.glob("*.txt"):
            try:
                with open(lbl_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if parts:
                            cls_id = int(parts[0])
                            class_instances[split][cls_id] += 1
            except:
                pass
    
    # Build class frequency table
    class_freq = []
    for i, name in enumerate(classes):
        train_inst = class_instances["train"].get(i, 0)
        valid_inst = class_instances["valid"].get(i, 0)
        test_inst = class_instances["test"].get(i, 0)
        total = train_inst + valid_inst + test_inst
        class_freq.append({
            "class_id": i, "class_name": name,
            "train_instances": train_inst, "valid_instances": valid_inst,
            "test_instances": test_inst, "total_instances": total
        })
    
    print(f"\n  Top 10 classes by instance count:")
    sorted_freq = sorted(class_freq, key=lambda x: x["total_instances"], reverse=True)
    for cf in sorted_freq[:10]:
        print(f"    {cf['class_name']:<30} train={cf['train_instances']:>5} valid={cf['valid_instances']:>4} test={cf['test_instances']:>4} total={cf['total_instances']:>5}")
    
    print(f"\n  Bottom 5 classes by instance count:")
    for cf in sorted_freq[-5:]:
        print(f"    {cf['class_name']:<30} train={cf['train_instances']:>5} valid={cf['valid_instances']:>4} test={cf['test_instances']:>4} total={cf['total_instances']:>5}")
    
    zero_count = sum(1 for cf in class_freq if cf["total_instances"] == 0)
    print(f"\n  Classes with 0 instances: {zero_count}")
    
    return {
        "name": "food_ingredients_roboflow",
        "nc": nc,
        "classes": classes,
        "class_freq": class_freq,
        "train_images": ti, "valid_images": vi, "test_images": tei,
        "train_labels": tl, "valid_labels": vl, "test_labels": tel,
        "total_images": ti+vi+tei,
        "annotation_format": "YOLOv8",
        "license": "CC BY 4.0",
        "version": "v4",
        "source_url": "https://universe.roboflow.com/food-recipe-ingredient-images-0gnku/food-ingredients-dataset/dataset/4",
        "download_date": "2026-09-27",
        "owner": "Roboflow user",
        "preprocessing": "Auto-orient, resize 640x640 (stretch)",
        "augmentation": "3x augmented (h-flip, v-flip, Gaussian blur, salt&pepper)"
    }


# ============================================================
# DATASET 2: FoodSeg103
# ============================================================
def audit_ds2():
    print("\n" + "="*70)
    print(" B. FOODSEG103 (02_foodseg103)")
    print("="*70)
    
    with open(DS2 / "meta.json", 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    classes = [c["title"] for c in meta.get("classes", []) if c.get("title")]
    tags = [t["name"] for t in meta.get("tags", [])]
    annotation_shape = meta["classes"][0]["shape"] if meta.get("classes") else "unknown"
    
    print(f"  Classes: {len(classes)}")
    print(f"  Annotation type: {annotation_shape} (semantic segmentation)")
    print(f"  Tags: {tags}")
    
    # Count images
    train_dir = DS2 / "train"
    test_dir  = DS2 / "test"
    
    # FoodSeg103 DatasetNinja format: train/img/ and train/meta/ or train/ann/
    train_img_dir = train_dir / "img"
    test_img_dir  = test_dir  / "img"
    train_ann_dir = train_dir / "ann"
    test_ann_dir  = test_dir  / "ann"
    train_meta_dir = train_dir / "meta"
    test_meta_dir  = test_dir  / "meta"
    
    # Check subdirs
    if train_img_dir.exists():
        ti = count_files_flat(train_img_dir)
    else:
        ti = count_files(train_dir)
    
    if test_img_dir.exists():
        tei = count_files_flat(test_img_dir)
    else:
        tei = count_files(test_dir)
    
    # Check annotation dir
    train_ann_count = 0
    test_ann_count = 0
    if train_ann_dir.exists():
        train_ann_count = sum(1 for f in train_ann_dir.iterdir() if f.suffix == '.json')
    if train_meta_dir.exists():
        train_ann_count = max(train_ann_count, sum(1 for f in train_meta_dir.iterdir() if f.suffix == '.json'))
    if test_ann_dir.exists():
        test_ann_count = sum(1 for f in test_ann_dir.iterdir() if f.suffix == '.json')
    if test_meta_dir.exists():
        test_ann_count = max(test_ann_count, sum(1 for f in test_meta_dir.iterdir() if f.suffix == '.json'))
    
    print(f"  Train images: {ti}, annotations: {train_ann_count}")
    print(f"  Test images:  {tei}, annotations: {test_ann_count}")
    print(f"  Valid images: 0 (no validation split)")
    print(f"  Total images: {ti+tei}")
    
    # Count class instances from annotation JSONs
    class_instances = {"train": Counter(), "test": Counter()}
    
    # Sample a few annotation files to understand structure
    sample_count = 0
    ann_dirs = []
    if train_meta_dir.exists():
        ann_dirs.append(("train", train_meta_dir))
    if train_ann_dir.exists():
        ann_dirs.append(("train", train_ann_dir))
    if test_meta_dir.exists():
        ann_dirs.append(("test", test_meta_dir))
    if test_ann_dir.exists():
        ann_dirs.append(("test", test_ann_dir))
    
    for split, ann_dir in ann_dirs:
        for ann_file in sorted(ann_dir.glob("*.json")):
            try:
                with open(ann_file, 'r', encoding='utf-8') as f:
                    ann = json.load(f)
                # Look for objects/labels in the annotation
                objects = ann.get("objects", [])
                for obj in objects:
                    cls_title = obj.get("classTitle", "")
                    if cls_title:
                        class_instances[split][cls_title] += 1
                if sample_count == 0:
                    print(f"\n  Sample annotation ({ann_file.name}): {len(objects)} objects")
                    if objects:
                        print(f"    Keys: {list(objects[0].keys())}")
                        print(f"    classTitle: {objects[0].get('classTitle','')}")
                sample_count += 1
            except:
                pass
    
    # Build frequency table
    all_class_counts = Counter()
    for split_counts in class_instances.values():
        all_class_counts.update(split_counts)
    
    class_freq = []
    for cls_name in classes:
        train_c = class_instances["train"].get(cls_name, 0)
        test_c = class_instances["test"].get(cls_name, 0)
        class_freq.append({
            "class_id": classes.index(cls_name),
            "class_name": cls_name,
            "train_instances": train_c,
            "valid_instances": 0,
            "test_instances": test_c,
            "total_instances": train_c + test_c
        })
    
    print(f"\n  Top 10 classes by instance count:")
    sorted_freq = sorted(class_freq, key=lambda x: x["total_instances"], reverse=True)
    for cf in sorted_freq[:10]:
        print(f"    {cf['class_name']:<25} train={cf['train_instances']:>5} test={cf['test_instances']:>5} total={cf['total_instances']:>5}")
    
    zero_count = sum(1 for cf in class_freq if cf["total_instances"] == 0)
    print(f"\n  Classes with 0 instances found: {zero_count}")
    if zero_count > 0 and zero_count < len(classes):
        # Might be because we couldn't parse all annotations
        print(f"  NOTE: 0-instance classes may be due to bitmap segmentation (pixel-level, not object-level)")
    
    return {
        "name": "foodseg103",
        "nc": len(classes),
        "classes": classes,
        "class_freq": class_freq,
        "train_images": ti, "valid_images": 0, "test_images": tei,
        "train_labels": train_ann_count, "valid_labels": 0, "test_labels": test_ann_count,
        "total_images": ti+tei,
        "annotation_format": f"Supervisely ({annotation_shape} segmentation)",
        "license": "Apache 2.0",
        "version": "v1",
        "source_url": "https://github.com/LARC-CMU-SMU/FoodSeg103-Benchmark-v1",
        "download_date": "2026-09-27",
        "owner": "LARC-CMU-SMU",
        "preprocessing": "None documented",
        "augmentation": "None",
        "tags": tags
    }


# ============================================================
# DATASET 3: Indonesian Food
# ============================================================
def audit_ds3():
    print("\n" + "="*70)
    print(" C. INDONESIAN FOOD (03_indonesian_food)")
    print("="*70)
    
    with open(DS3 / "data.yaml", 'r') as f:
        content = f.read()
    
    names_match = re.search(r"names:\s*\[(.+)\]", content)
    classes = [n.strip().strip("'\"") for n in names_match.group(1).split(',')] if names_match else []
    nc = int(re.search(r"nc:\s*(\d+)", content).group(1))
    
    print(f"  Classes declared (nc): {nc}")
    print(f"  Classes in names list: {len(classes)}")
    print(f"  Class names: {classes}")
    
    train_img = DS3 / "train" / "images"
    valid_img = DS3 / "valid" / "images"
    test_img  = DS3 / "test"  / "images"
    train_lbl = DS3 / "train" / "labels"
    valid_lbl = DS3 / "valid" / "labels"
    test_lbl  = DS3 / "test"  / "labels"
    
    ti = count_files_flat(train_img) if train_img.exists() else 0
    vi = count_files_flat(valid_img) if valid_img.exists() else 0
    tei = count_files_flat(test_img) if test_img.exists() else 0
    tl = count_txt_labels(train_lbl) if train_lbl.exists() else 0
    vl = count_txt_labels(valid_lbl) if valid_lbl.exists() else 0
    tel = count_txt_labels(test_lbl) if test_lbl.exists() else 0
    
    print(f"  Train images: {ti}, labels: {tl}")
    print(f"  Valid images: {vi}, labels: {vl}")
    print(f"  Test images:  {tei}, labels: {tel}")
    print(f"  Total images: {ti+vi+tei}")
    
    # Count instances per class
    class_instances = {"train": Counter(), "valid": Counter(), "test": Counter()}
    
    for split, lbl_dir in [("train", train_lbl), ("valid", valid_lbl), ("test", test_lbl)]:
        if not lbl_dir.exists():
            continue
        for lbl_file in lbl_dir.glob("*.txt"):
            try:
                with open(lbl_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if parts:
                            cls_id = int(parts[0])
                            class_instances[split][cls_id] += 1
            except:
                pass
    
    class_freq = []
    for i, name in enumerate(classes):
        train_inst = class_instances["train"].get(i, 0)
        valid_inst = class_instances["valid"].get(i, 0)
        test_inst = class_instances["test"].get(i, 0)
        total = train_inst + valid_inst + test_inst
        class_freq.append({
            "class_id": i, "class_name": name,
            "train_instances": train_inst, "valid_instances": valid_inst,
            "test_instances": test_inst, "total_instances": total
        })
    
    print(f"\n  All classes by instance count:")
    sorted_freq = sorted(class_freq, key=lambda x: x["total_instances"], reverse=True)
    for cf in sorted_freq:
        print(f"    {cf['class_name']:<20} train={cf['train_instances']:>5} valid={cf['valid_instances']:>4} test={cf['test_instances']:>4} total={cf['total_instances']:>5}")
    
    return {
        "name": "indonesian_food",
        "nc": nc,
        "classes": classes,
        "class_freq": class_freq,
        "train_images": ti, "valid_images": vi, "test_images": tei,
        "train_labels": tl, "valid_labels": vl, "test_labels": tel,
        "total_images": ti+vi+tei,
        "annotation_format": "YOLOv8",
        "license": "CC BY 4.0",
        "version": "v1",
        "source_url": "https://universe.roboflow.com/aku-yolo/deteksi-makanan-indonesia-spmyy/dataset/1",
        "download_date": "2026-09-27",
        "owner": "Roboflow user (aku-yolo)",
        "preprocessing": "Auto-orient only",
        "augmentation": "None"
    }


# ============================================================
# OUTPUT BUILDERS
# ============================================================

def build_vision_dataset_inventory(ds1, ds2, ds3):
    """Build 00_sources/vision_dataset_inventory.csv"""
    rows = []
    for ds_info in [ds1, ds2, ds3]:
        for cf in ds_info["class_freq"]:
            rows.append({
                "dataset": ds_info["name"],
                "original_label": cf["class_name"],
                "class_id": cf["class_id"],
                "train_images": cf["train_instances"],
                "valid_images": cf["valid_instances"],
                "test_images": cf["test_instances"],
                "total_images": cf["total_instances"],
                "annotation_type": ds_info["annotation_format"],
                "license": ds_info["license"],
                "source_url": ds_info["source_url"],
                "notes": ""
            })
    df = pd.DataFrame(rows)
    df.to_csv(OUT_SOURCES / "vision_dataset_inventory.csv", index=False, encoding='utf-8')
    print(f"\n  Saved: {OUT_SOURCES / 'vision_dataset_inventory.csv'} ({len(rows)} rows)")
    return df


def build_class_overlap(ds1, ds2, ds3):
    """Build 01_mapping_input/class_overlap.csv"""
    # Normalize class names for comparison (lowercase, underscore->space, strip)
    def normalize(s):
        return s.lower().replace('_', ' ').replace('-', ' ').strip()
    
    # Build per-dataset sets
    ds1_labels = {normalize(c): c for c in ds1["classes"]}
    ds2_labels = {normalize(c): c for c in ds2["classes"]}
    ds3_labels = {normalize(c): c for c in ds3["classes"]}
    
    # Manual semantic equivalences
    EQUIV = {
        "brinjal": "eggplant",
        "capsicum": "pepper",
        "rice chamal": "rice",
        "water melon": "watermelon",
        "wallnut": "walnut",
        "okra bhindi": "okra",
        "soyabean bhatmas": "soy",
        "green soyabean hariyo bhatmas": "soy",
        "lemon nimbu": "lemon",
        "lime kagati": "lemon",
        "pumpkin farsi": "pumpkin",
        "palak indian spinach": "spinach",
        "palungo nepali spinach": "spinach",
        "bamboo shoots tama": "bamboo shoots",
        "asparagus kurilo": "asparagus",
        "ash gourd kubhindo": "ash gourd",
        "cassava ghar tarul": "cassava",
        "bitter gourd": "bitter gourd",
        "sweet potato suthuni": "sweet potato",
        "crab meat": "crab",
        "mushroom": "mushroom",
        "chili pepper khursani": "chili",
        "akabare khursani": "chili",
        "coriander dhaniya": "cilantro",
        "green mint pudina": "mint",
        "onion leaves": "spring onion",
    }
    
    # Collect all normalized names
    all_normalized = set()
    all_normalized.update(ds1_labels.keys())
    all_normalized.update(ds2_labels.keys())
    all_normalized.update(ds3_labels.keys())
    
    # Apply equivalences
    canon_groups = defaultdict(lambda: {"ds1": None, "ds2": None, "ds3": None, "datasets": set()})
    
    for norm, orig in ds1_labels.items():
        canon = EQUIV.get(norm, norm)
        canon_groups[canon]["ds1"] = orig
        canon_groups[canon]["datasets"].add("food_ingredients_roboflow")
    
    for norm, orig in ds2_labels.items():
        canon = EQUIV.get(norm, norm)
        canon_groups[canon]["ds2"] = orig
        canon_groups[canon]["datasets"].add("foodseg103")
    
    for norm, orig in ds3_labels.items():
        canon = EQUIV.get(norm, norm)
        canon_groups[canon]["ds3"] = orig
        canon_groups[canon]["datasets"].add("indonesian_food")
    
    rows = []
    for canon, info in sorted(canon_groups.items()):
        rows.append({
            "canonical_candidate": canon,
            "food_ingredients_label": info["ds1"] or "",
            "foodseg103_label": info["ds2"] or "",
            "indonesian_food_label": info["ds3"] or "",
            "dataset_count": len(info["datasets"]),
            "notes": ""
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(OUT_MAPPING / "class_overlap.csv", index=False, encoding='utf-8')
    
    overlap_2 = df[df.dataset_count >= 2]
    overlap_3 = df[df.dataset_count >= 3]
    print(f"\n  Total unique canonical candidates: {len(df)}")
    print(f"  Overlap 2+ datasets: {len(overlap_2)}")
    print(f"  Overlap 3 datasets:  {len(overlap_3)}")
    
    if len(overlap_2) > 0:
        print(f"\n  Classes in 2+ datasets:")
        for _, r in overlap_2.iterrows():
            ds_list = []
            if r["food_ingredients_label"]: ds_list.append(f"DS1:{r['food_ingredients_label']}")
            if r["foodseg103_label"]: ds_list.append(f"DS2:{r['foodseg103_label']}")
            if r["indonesian_food_label"]: ds_list.append(f"DS3:{r['indonesian_food_label']}")
            print(f"    {r['canonical_candidate']:<25} ({', '.join(ds_list)})")
    
    return df


def build_class_relevance(overlap_df, ds1, ds2, ds3):
    """Build 01_mapping_input/class_relevance.csv"""
    
    # Food group assignments
    FOOD_GROUPS = {
        # Karbo
        "rice": "Karbohidrat", "bread": "Karbohidrat", "noodles": "Karbohidrat", "pasta": "Karbohidrat",
        "corn": "Karbohidrat", "potato": "Karbohidrat", "cassava": "Karbohidrat", "wheat": "Karbohidrat",
        "beaten rice chiura": "Karbohidrat", "cornflakec": "Karbohidrat", "sweet potato": "Karbohidrat",
        "nasi goreng": "Karbohidrat", "chowmein noodles": "Karbohidrat", "noodle": "Karbohidrat",
        "thukpa noodles": "Karbohidrat",
        # Protein Hewani
        "egg": "Protein Hewani", "chicken": "Protein Hewani", "fish": "Protein Hewani",
        "shrimp": "Protein Hewani", "crab": "Protein Hewani", "beef": "Protein Hewani",
        "lamb": "Protein Hewani", "pork": "Protein Hewani", "shellfish": "Protein Hewani",
        "chicken duck": "Protein Hewani", "sausage": "Protein Hewani", "steak": "Protein Hewani",
        "fried meat": "Protein Hewani", "mutton": "Protein Hewani", "buff meat": "Protein Hewani",
        "bacon": "Protein Hewani", "ham": "Protein Hewani", "minced meat": "Protein Hewani",
        "chicken gizzards": "Protein Hewani", "sate ayam": "Protein Hewani",
        "rendang": "Protein Hewani", "pepes ikan": "Protein Hewani",
        "telur balado": "Protein Hewani", "bakso": "Protein Hewani",
        # Protein Nabati
        "tofu": "Protein Nabati", "soy": "Protein Nabati", "peanut": "Protein Nabati",
        "red beans": "Protein Nabati", "green beans": "Protein Nabati",
        "chickpeas": "Protein Nabati", "black lentils": "Protein Nabati",
        "green lentils": "Protein Nabati", "red lentils": "Protein Nabati",
        "yellow lentils": "Protein Nabati", "black beans": "Protein Nabati",
        "beans": "Protein Nabati", "garden peas": "Protein Nabati",
        "pea": "Protein Nabati", "green peas": "Protein Nabati",
        "nutrela soya chunks": "Protein Nabati",
        "broad beans bakullo": "Protein Nabati",
        # Sayuran
        "carrot": "Sayuran", "cabbage": "Sayuran", "broccoli": "Sayuran",
        "cauliflower": "Sayuran", "tomato": "Sayuran", "eggplant": "Sayuran",
        "cucumber": "Sayuran", "lettuce": "Sayuran", "onion": "Sayuran",
        "garlic": "Sayuran", "pepper": "Sayuran", "pumpkin": "Sayuran",
        "okra": "Sayuran", "celery stick": "Sayuran", "french beans": "Sayuran",
        "bean sprouts": "Sayuran", "bamboo shoots": "Sayuran", "spring onion": "Sayuran",
        "white radish": "Sayuran", "asparagus": "Sayuran", "snow peas": "Sayuran",
        "rape": "Sayuran", "spinach": "Sayuran", "radish": "Sayuran",
        "turnip": "Sayuran", "bitter gourd": "Sayuran", "long beans bodi": "Sayuran",
        "ash gourd": "Sayuran", "bottle gourd lauka": "Sayuran",
        "pointed gourd chuche karela": "Sayuran", "snake gourd chichindo": "Sayuran",
        "sponge gourd ghiraula": "Sayuran", "chayote iskus": "Sayuran",
        "beetroot": "Sayuran", "kangkung": "Sayuran", "pakcoy": "Sayuran",
        # Buah
        "apple": "Buah", "banana": "Buah", "orange": "Buah", "grape": "Buah",
        "mango": "Buah", "watermelon": "Buah", "melon": "Buah", "pineapple": "Buah",
        "strawberry": "Buah", "lemon": "Buah", "pear": "Buah", "peach": "Buah",
        "cherry": "Buah", "kiwi": "Buah", "avocado": "Buah", "date": "Buah",
        "fig": "Buah", "blueberry": "Buah", "raspberry": "Buah", "apricot": "Buah",
        "papaya": "Buah", "jack fruit": "Buah",
        "lapsi nepali hog plum": "Buah", "tree tomato rukh tamatar": "Buah",
        # Jamur
        "mushroom": "Jamur", "enoki mushroom": "Jamur", "oyster mushroom": "Jamur",
        "king oyster mushroom": "Jamur", "shiitake": "Jamur", "white button mushroom": "Jamur",
        # Kacang
        "almond": "Kacang", "cashew": "Kacang", "walnut": "Kacang",
        # Bumbu/Rempah
        "ginger": "Bumbu/Rempah", "chili": "Bumbu/Rempah", "cilantro": "Bumbu/Rempah",
        "mint": "Bumbu/Rempah", "cinnamon": "Bumbu/Rempah", "chili powder": "Bumbu/Rempah",
        # Susu/Dairy
        "milk": "Susu/Dairy", "cheese": "Susu/Dairy", "butter": "Susu/Dairy",
        "paneer": "Susu/Dairy", "cheese butter": "Susu/Dairy",
        # Rumput Laut
        "kelp": "Rumput Laut", "seaweed": "Rumput Laut",
        # Olahan/Jajanan
        "bika ambon": "Jajanan", "dadar gulung": "Jajanan", "kue cubit": "Jajanan",
        "putu ayu": "Jajanan", "10": "Unknown",
        # Snack/Dessert
        "cake": "Dessert", "pie": "Dessert", "biscuit": "Dessert", "candy": "Dessert",
        "chocolate": "Dessert", "ice cream": "Dessert", "pudding": "Dessert",
        "egg tart": "Dessert", "popcorn": "Snack",
        # Minuman
        "coffee": "Minuman", "tea": "Minuman", "juice": "Minuman",
        "wine": "Minuman", "milkshake": "Minuman",
        # Makanan Olahan
        "hamburg": "Makanan Olahan", "pizza": "Makanan Olahan",
        "french fries": "Makanan Olahan", "hanamaki baozi": "Makanan Olahan",
        "wonton dumplings": "Makanan Olahan", "salad": "Makanan Olahan",
        "soup": "Makanan Olahan", "kimchi": "Makanan Olahan",
        "gundruk": "Makanan Olahan", "masyaura": "Makanan Olahan",
        # Minyak/Bumbu
        "olive oil": "Minyak", "salt": "Bumbu", "sugar": "Bumbu",
        "ketchup": "Bumbu", "soy sauce": "Bumbu", "mayonnaise": "Bumbu",
        "sauce": "Bumbu",
        # Lainnya
        "ice": "Lainnya", "dried cranberries": "Buah Olahan",
        "olives": "Buah", "other ingredients": "Lainnya",
        # Daun
        "taro leaves karkalo": "Sayuran Daun", "taro root pidalu": "Umbi",
        "moringa leaves sajyun ko munta": "Sayuran Daun",
        "sajjyun moringa drumsticks": "Sayuran",
        "garden cress chamsur ko saag": "Sayuran Daun",
        "bethu ko saag": "Sayuran Daun", "rayo ko saag": "Sayuran Daun",
        "tori ko saag": "Sayuran Daun", "stinging nettle sisnu": "Sayuran Daun",
        "fiddlehead ferns niguro": "Sayuran", "farsi ko munta": "Sayuran",
        "rahar ko daal": "Protein Nabati",
    }
    
    # Relevance determination
    HIGH_GROUPS = {"Karbohidrat", "Protein Hewani", "Protein Nabati", "Sayuran", "Buah"}
    MEDIUM_GROUPS = {"Jamur", "Kacang", "Susu/Dairy", "Bumbu/Rempah", "Umbi"}
    LOW_GROUPS = {"Dessert", "Snack", "Minuman", "Minyak", "Rumput Laut", "Buah Olahan",
                  "Jajanan", "Makanan Olahan", "Bumbu", "Sayuran Daun"}
    EXCLUDE_GROUPS = {"Lainnya", "Unknown"}
    
    rows = []
    for _, r in overlap_df.iterrows():
        canon = r["canonical_candidate"]
        fg = FOOD_GROUPS.get(canon, "Lainnya")
        
        if fg in HIGH_GROUPS:
            relevance = "HIGH"
            reason = f"{fg}; directly relevant to daily nutrition education"
        elif fg in MEDIUM_GROUPS:
            relevance = "MEDIUM"
            reason = f"{fg}; relevant but less common in daily meals"
        elif fg in LOW_GROUPS:
            relevance = "LOW"
            reason = f"{fg}; not primary nutritional focus"
        else:
            relevance = "EXCLUDE"
            reason = f"{fg}; not a recognizable food item or too vague"
        
        rows.append({
            "canonical_candidate": canon,
            "food_group": fg,
            "relevance": relevance,
            "reason": reason
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(OUT_MAPPING / "class_relevance.csv", index=False, encoding='utf-8')
    
    print(f"\n  Relevance distribution:")
    for rel in ["HIGH","MEDIUM","LOW","EXCLUDE"]:
        count = (df.relevance == rel).sum()
        print(f"    {rel}: {count}")
    
    return df


def build_problematic_classes(overlap_df, ds1, ds2, ds3):
    """Build 01_mapping_input/problematic_classes.csv"""
    rows = []
    
    # Get all class frequencies
    all_freq = {}
    for ds in [ds1, ds2, ds3]:
        for cf in ds["class_freq"]:
            key = (ds["name"], cf["class_name"])
            all_freq[key] = cf["total_instances"]
    
    # Check each class across all datasets
    for ds in [ds1, ds2, ds3]:
        for cf in ds["class_freq"]:
            name = cf["class_name"]
            total = cf["total_instances"]
            problems = []
            
            # Very few instances
            if total > 0 and total < 10:
                problems.append(("LOW_INSTANCE_COUNT", "HIGH", "REVIEW",
                                f"Only {total} instances"))
            elif total == 0:
                problems.append(("ZERO_INSTANCES", "HIGH", "REVIEW",
                                "No instances found in annotations"))
            
            # Ambiguous names
            ambig_names = {"chicken duck", "cheese butter", "cilantro mint",
                          "other ingredients", "10"}
            if name.lower() in ambig_names:
                problems.append(("AMBIGUOUS_NAME", "HIGH", "EXCLUDE",
                                "Name combines multiple foods or is meaningless"))
            
            # Composite foods
            composite = {"salad", "soup", "sauce", "fried meat", "hamburg",
                         "pizza", "pie", "french fries", "hanamaki baozi",
                         "wonton dumplings", "nasi_goreng", "bakso", "rendang",
                         "sate_ayam", "pepes_ikan", "telur_balado", "steak"}
            if name.lower().replace(' ','_') in composite:
                problems.append(("COMPOSITE_FOOD", "MEDIUM", "REVIEW",
                                "Multi-ingredient dish; hard to map to single nutrition record"))
            
            # Beverages
            beverages = {"coffee", "tea", "juice", "wine", "milkshake", "milk"}
            if name.lower() in beverages and name.lower() != "milk":
                problems.append(("BEVERAGE", "LOW", "REVIEW",
                                "Beverage; nutrition varies by preparation"))
            
            # Non-food
            non_food = {"ice", "salt", "sugar", "olive oil", "soy sauce",
                       "ketchup", "mayonnaise", "chili powder", "cinnamon"}
            if name.lower() in non_food:
                problems.append(("NOT_FOOD_ITEM", "LOW", "EXCLUDE",
                                "Condiment/ingredient, not a food item to recognize"))
            
            # Too specific (local Nepali names)
            nepali_specific = {"Akabare Khursani", "Bethu ko Saag", "Farsi ko Munta",
                              "Fiddlehead Ferns -Niguro-", "Gundruk", "Lapsi -Nepali Hog Plum-",
                              "Masyaura", "Moringa Leaves -Sajyun ko Munta-",
                              "Palak -Indian Spinach-", "Palungo -Nepali Spinach-",
                              "Rahar ko Daal", "Rayo ko Saag", "Sajjyun -Moringa Drumsticks-",
                              "Stinging Nettle -Sisnu-", "Taro Leaves -Karkalo-",
                              "Tori ko Saag", "Tree Tomato -Rukh Tamatar-",
                              "Garden cress-Chamsur ko saag-", "Nutrela -Soya Chunks-",
                              "Green Soyabean -Hariyo Bhatmas-"}
            if name in nepali_specific:
                problems.append(("CULTURE_SPECIFIC", "LOW", "REVIEW",
                                "Nepali-specific food name; limited audience relevance"))
            
            # Semantic overlap
            overlap_sets = [
                ({"Brinjal", "Green Brinjal"}, "eggplant variants"),
                ({"Beans", "French Beans -Bodi-", "Long Beans -Bodi-", "Garden Peas", "Pea", "Green Peas"}, "bean/pea variants"),
                ({"Lemon -Nimbu-", "Lime -Kagati-"}, "citrus overlap"),
                ({"Chowmein Noodles", "Thukpa Noodles", "noodle"}, "noodle variants"),
                ({"Palak -Indian Spinach-", "Palungo -Nepali Spinach-"}, "spinach variants"),
            ]
            for overlap_set, desc in overlap_sets:
                if name in overlap_set:
                    problems.append(("SEMANTIC_OVERLAP", "MEDIUM", "REVIEW",
                                    f"Overlaps with: {desc}"))
            
            for ptype, sev, rec, note in problems:
                rows.append({
                    "original_label": name,
                    "dataset": ds["name"],
                    "problem_type": ptype,
                    "severity": sev,
                    "recommendation": rec,
                    "notes": note
                })
    
    df = pd.DataFrame(rows)
    df.to_csv(OUT_MAPPING / "problematic_classes.csv", index=False, encoding='utf-8')
    
    print(f"\n  Problematic classes: {df.original_label.nunique()} unique labels, {len(df)} issues")
    for sev in ["HIGH","MEDIUM","LOW"]:
        count = (df.severity == sev).sum()
        print(f"    {sev}: {count}")
    
    return df


def build_final_candidates(overlap_df, relevance_df, problematic_df, ds1, ds2, ds3):
    """Build 01_mapping_input/final_class_candidates.csv"""
    
    # Get HIGH relevance candidates
    high = relevance_df[relevance_df.relevance == "HIGH"].canonical_candidate.tolist()
    medium = relevance_df[relevance_df.relevance == "MEDIUM"].canonical_candidate.tolist()
    
    # Get total images per canonical candidate across all datasets
    all_freq = {}
    for ds in [ds1, ds2, ds3]:
        for cf in ds["class_freq"]:
            norm = cf["class_name"].lower().replace('_', ' ').replace('-', ' ').strip()
            if norm not in all_freq:
                all_freq[norm] = {"total": 0, "sources": [], "labels": []}
            all_freq[norm]["total"] += cf["total_instances"]
            if cf["total_instances"] > 0:
                all_freq[norm]["sources"].append(ds["name"])
            all_freq[norm]["labels"].append(f"{ds['name']}:{cf['class_name']}")
    
    # Also check overlap canonical names
    for _, r in overlap_df.iterrows():
        canon = r["canonical_candidate"]
        total = 0
        sources = []
        labels = []
        for ds in [ds1, ds2, ds3]:
            ds_name = ds["name"]
            col_map = {"food_ingredients_roboflow": "food_ingredients_label",
                      "foodseg103": "foodseg103_label",
                      "indonesian_food": "indonesian_food_label"}
            orig_label = r.get(col_map.get(ds_name, ""), "")
            if orig_label:
                # Find instance count
                for cf in ds["class_freq"]:
                    if cf["class_name"] == orig_label:
                        total += cf["total_instances"]
                        if cf["total_instances"] > 0:
                            sources.append(ds_name)
                        labels.append(f"{ds_name}:{orig_label}")
                        break
        if canon not in all_freq or total > all_freq[canon]["total"]:
            all_freq[canon] = {"total": total, "sources": sources, "labels": labels}
    
    # Problematic labels to exclude
    exclude_labels = set(problematic_df[problematic_df.recommendation == "EXCLUDE"]["original_label"].str.lower())
    
    # Select candidates
    candidates = []
    seen = set()
    
    for canon in high + medium:
        if canon in seen:
            continue
        seen.add(canon)
        
        freq_info = all_freq.get(canon, {"total": 0, "sources": [], "labels": []})
        total_img = freq_info["total"]
        sources = freq_info["sources"]
        labels = freq_info["labels"]
        
        # Skip if total images too low and not in 2+ datasets
        if total_img < 5 and len(sources) < 2:
            continue
        
        # Skip excluded
        if canon in exclude_labels:
            continue
        
        # Skip composite foods
        composite_canons = {"salad", "soup", "sauce", "fried meat", "hamburg", "pizza",
                           "pie", "french fries", "hanamaki baozi", "wonton dumplings",
                           "steak", "sausage", "nasi goreng", "bakso", "rendang",
                           "sate ayam", "pepes ikan", "telur balado", "kimchi"}
        if canon in composite_canons:
            continue
        
        # Skip ambiguous
        ambig = {"chicken duck", "cheese butter", "cilantro mint", "other ingredients", "10"}
        if canon in ambig:
            continue
        
        # Determine confidence
        if total_img >= 50 and len(sources) >= 2:
            confidence = "HIGH"
        elif total_img >= 20 or len(sources) >= 2:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        # Get food group
        fg_row = relevance_df[relevance_df.canonical_candidate == canon]
        fg = fg_row.iloc[0]["food_group"] if not fg_row.empty else "Unknown"
        
        # Source datasets
        ov_row = overlap_df[overlap_df.canonical_candidate == canon]
        orig_labels = []
        if not ov_row.empty:
            r = ov_row.iloc[0]
            if r["food_ingredients_label"]: orig_labels.append(f"DS1:{r['food_ingredients_label']}")
            if r["foodseg103_label"]: orig_labels.append(f"DS2:{r['foodseg103_label']}")
            if r["indonesian_food_label"]: orig_labels.append(f"DS3:{r['indonesian_food_label']}")
        
        reason_parts = []
        if canon in high: reason_parts.append("HIGH relevance")
        if len(sources) >= 2: reason_parts.append(f"in {len(sources)} datasets")
        if total_img >= 50: reason_parts.append(f"{total_img} instances")
        elif total_img > 0: reason_parts.append(f"{total_img} instances")
        reason_parts.append(fg)
        
        candidates.append({
            "final_candidate": canon,
            "food_group": fg,
            "source_dataset": ", ".join(sources) if sources else "none",
            "original_labels": "; ".join(orig_labels),
            "total_images": total_img,
            "confidence": confidence,
            "reason": "; ".join(reason_parts),
            "nutrition_mapping_status": "NOT_CHECKED"
        })
    
    # Sort by confidence then total_images
    conf_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    candidates.sort(key=lambda x: (conf_order.get(x["confidence"], 3), -x["total_images"]))
    
    df = pd.DataFrame(candidates)
    df.to_csv(OUT_MAPPING / "final_class_candidates.csv", index=False, encoding='utf-8')
    
    print(f"\n  Final candidates: {len(df)}")
    for conf in ["HIGH","MEDIUM","LOW"]:
        count = (df.confidence == conf).sum()
        print(f"    {conf}: {count}")
    
    return df


def write_audit_report(ds1, ds2, ds3, inventory_df, overlap_df, relevance_df, 
                       problematic_df, candidates_df):
    """Write DATASET_AUDIT_REPORT.md"""
    
    report = f"""# NutriVision Vision Dataset Audit Report

**Generated:** {TODAY}  
**Auditor:** Senior CV Dataset Auditor (automated)

---

## 1. Datasets Available

### A. Food Ingredients Roboflow (`01_food_ingredients_roboflow`)

| Field | Value |
|-------|-------|
| Classes | {ds1['nc']} |
| Train images | {ds1['train_images']} |
| Valid images | {ds1['valid_images']} |
| Test images | {ds1['test_images']} |
| Total images | {ds1['total_images']} |
| Annotation | {ds1['annotation_format']} |
| License | {ds1['license']} |
| Version | {ds1['version']} |
| Source | {ds1['source_url']} |
| Owner | {ds1['owner']} |
| Download date | {ds1['download_date']} |
| Preprocessing | {ds1['preprocessing']} |
| Augmentation | {ds1['augmentation']} |

### B. FoodSeg103 (`02_foodseg103`)

| Field | Value |
|-------|-------|
| Classes | {ds2['nc']} |
| Train images | {ds2['train_images']} |
| Valid images | {ds2['valid_images']} (no validation split) |
| Test images | {ds2['test_images']} |
| Total images | {ds2['total_images']} |
| Annotation | {ds2['annotation_format']} |
| License | {ds2['license']} |
| Version | {ds2['version']} |
| Source | {ds2['source_url']} |
| Owner | {ds2['owner']} |
| Download date | {ds2['download_date']} |
| Tags | {', '.join(ds2.get('tags', []))} |

### C. Indonesian Food (`03_indonesian_food`)

| Field | Value |
|-------|-------|
| Classes | {ds3['nc']} |
| Train images | {ds3['train_images']} |
| Valid images | {ds3['valid_images']} |
| Test images | {ds3['test_images']} |
| Total images | {ds3['total_images']} |
| Annotation | {ds3['annotation_format']} |
| License | {ds3['license']} |
| Version | {ds3['version']} |
| Source | {ds3['source_url']} |
| Owner | {ds3['owner']} |
| Download date | {ds3['download_date']} |
| Augmentation | {ds3.get('augmentation', 'None')} |

---

## 2. Class Count Summary

| Dataset | Classes | Total Images | Annotation |
|---------|---------|-------------|------------|
| Food Ingredients Roboflow | {ds1['nc']} | {ds1['total_images']} | {ds1['annotation_format']} |
| FoodSeg103 | {ds2['nc']} | {ds2['total_images']} | {ds2['annotation_format']} |
| Indonesian Food | {ds3['nc']} | {ds3['total_images']} | {ds3['annotation_format']} |
| **Total** | **{ds1['nc'] + ds2['nc'] + ds3['nc']}** | **{ds1['total_images'] + ds2['total_images'] + ds3['total_images']}** | |

## 3. Train/Valid/Test Structure

| Dataset | Train | Valid | Test | Has Val Split |
|---------|-------|-------|------|---------------|
| Food Ingredients | {ds1['train_images']} | {ds1['valid_images']} | {ds1['test_images']} | {'Yes' if ds1['valid_images'] > 0 else 'No'} |
| FoodSeg103 | {ds2['train_images']} | {ds2['valid_images']} | {ds2['test_images']} | No |
| Indonesian Food | {ds3['train_images']} | {ds3['valid_images']} | {ds3['test_images']} | {'Yes' if ds3['valid_images'] > 0 else 'No'} |

## 4. License / Provenance

| Dataset | License | Owner | Source URL |
|---------|---------|-------|-----------|
| Food Ingredients | CC BY 4.0 | Roboflow user | [link]({ds1['source_url']}) |
| FoodSeg103 | Apache 2.0 | LARC-CMU-SMU | [link]({ds2['source_url']}) |
| Indonesian Food | CC BY 4.0 | Roboflow user (aku-yolo) | [link]({ds3['source_url']}) |

## 5. Class Overlap

"""
    overlap_2plus = overlap_df[overlap_df.dataset_count >= 2]
    if not overlap_2plus.empty:
        report += f"**{len(overlap_2plus)} classes found in 2+ datasets:**\n\n"
        report += "| Canonical | Food Ingredients | FoodSeg103 | Indonesian Food |\n"
        report += "|-----------|-----------------|------------|----------------|\n"
        for _, r in overlap_2plus.iterrows():
            report += f"| {r['canonical_candidate']} | {r['food_ingredients_label'] or '-'} | {r['foodseg103_label'] or '-'} | {r['indonesian_food_label'] or '-'} |\n"
    else:
        report += "No class overlap found between datasets.\n"
    
    report += f"""
## 6. Problematic Classes

**Total: {problematic_df.original_label.nunique()} unique labels with {len(problematic_df)} issues**

| Problem Type | Count |
|-------------|-------|
"""
    for ptype in problematic_df.problem_type.value_counts().index:
        count = (problematic_df.problem_type == ptype).sum()
        report += f"| {ptype} | {count} |\n"
    
    report += f"""
### Recommended EXCLUDE:

"""
    exclude = problematic_df[problematic_df.recommendation == "EXCLUDE"]
    for _, r in exclude.drop_duplicates("original_label").iterrows():
        report += f"- **{r['original_label']}** ({r['dataset']}): {r['notes']}\n"
    
    report += f"""
## 7. Relevance Distribution

| Relevance | Count |
|-----------|-------|
| HIGH | {(relevance_df.relevance == 'HIGH').sum()} |
| MEDIUM | {(relevance_df.relevance == 'MEDIUM').sum()} |
| LOW | {(relevance_df.relevance == 'LOW').sum()} |
| EXCLUDE | {(relevance_df.relevance == 'EXCLUDE').sum()} |

## 8. Final Class Candidates

**{len(candidates_df)} candidates selected**

| Final Candidate | Food Group | Source | Total Images | Confidence |
|-----------------|-----------|--------|-------------|------------|
"""
    for _, r in candidates_df.iterrows():
        report += f"| {r['final_candidate']} | {r['food_group']} | {r['source_dataset']} | {r['total_images']} | {r['confidence']} |\n"
    
    report += f"""
## 9. Excluded Classes and Reasons

Classes NOT selected as final candidates:

"""
    final_canons = set(candidates_df.final_candidate.tolist())
    all_canons = set(overlap_df.canonical_candidate.tolist())
    excluded = all_canons - final_canons
    
    for canon in sorted(excluded):
        rel_row = relevance_df[relevance_df.canonical_candidate == canon]
        if not rel_row.empty:
            reason = rel_row.iloc[0]["reason"]
            report += f"- **{canon}**: {reason}\n"
    
    report += f"""
## 10. Dataset Source Recommendations

For each final candidate, recommended source:

| Candidate | Primary Source | Support Source | Exclude |
|-----------|---------------|---------------|---------|
"""
    for _, r in candidates_df.iterrows():
        sources = r["source_dataset"].split(", ") if r["source_dataset"] != "none" else []
        primary = sources[0] if sources else "none"
        support = ", ".join(sources[1:]) if len(sources) > 1 else "-"
        report += f"| {r['final_candidate']} | {primary} | {support} | - |\n"
    
    report += f"""
## 11. Overall Summary Statistics

| Metric | Value |
|--------|-------|
| Total Original Classes | {ds1['nc'] + ds2['nc'] + ds3['nc']} |
| Unique Canonical Candidates | {len(overlap_df)} |
| Final Candidates | {len(candidates_df)} |
| HIGH confidence | {(candidates_df.confidence == 'HIGH').sum()} |
| MEDIUM confidence | {(candidates_df.confidence == 'MEDIUM').sum()} |
| LOW confidence | {(candidates_df.confidence == 'LOW').sum()} |
| HIGH relevance | {(relevance_df.relevance == 'HIGH').sum()} |
| MEDIUM relevance | {(relevance_df.relevance == 'MEDIUM').sum()} |
| LOW relevance | {(relevance_df.relevance == 'LOW').sum()} |
| EXCLUDE | {(relevance_df.relevance == 'EXCLUDE').sum()} |
| REVIEW needed | {(problematic_df.recommendation == 'REVIEW').sum()} |

## 12. Important Notes

1. **Dataset 1 (Food Ingredients Roboflow)** has 120 classes with 3x augmentation applied.
   Images are resized to 640x640 (stretch). Nepali-specific food names included.

2. **Dataset 2 (FoodSeg103)** uses bitmap segmentation (Supervisely format), NOT bounding boxes.
   Instance counts reflect annotation objects, not images. No validation split.

3. **Dataset 3 (Indonesian Food)** is small (11 classes, ~2081 images) and focused on
   Indonesian prepared dishes (bakso, rendang, sate ayam, etc.). These are composite foods
   that are hard to map to single nutrition records.

4. **No dataset was modified** during this audit. Original labels preserved.

5. **nutrition_mapping_status** is set to NOT_CHECKED for all candidates.
   Nutrition mapping has not been performed in this audit step.
"""
    
    with open(OUT_MAPPING / "DATASET_AUDIT_REPORT.md", 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n  Saved: {OUT_MAPPING / 'DATASET_AUDIT_REPORT.md'}")


# ============================================================
# MAIN
# ============================================================
def main():
    print("="*70)
    print("  NutriVision Vision Dataset Audit")
    print(f"  Date: {TODAY}")
    print("="*70)
    
    ds1 = audit_ds1()
    ds2 = audit_ds2()
    ds3 = audit_ds3()
    
    print("\n" + "="*70)
    print(" BUILDING OUTPUTS")
    print("="*70)
    
    inv_df = build_vision_dataset_inventory(ds1, ds2, ds3)
    overlap_df = build_class_overlap(ds1, ds2, ds3)
    relevance_df = build_class_relevance(overlap_df, ds1, ds2, ds3)
    prob_df = build_problematic_classes(overlap_df, ds1, ds2, ds3)
    cand_df = build_final_candidates(overlap_df, relevance_df, prob_df, ds1, ds2, ds3)
    write_audit_report(ds1, ds2, ds3, inv_df, overlap_df, relevance_df, prob_df, cand_df)
    
    print("\n" + "="*70)
    print(" FINAL SUMMARY")
    print("="*70)
    print(f"\n  Dataset           Classes  Images  Annotation       License")
    print(f"  " + "-"*65)
    for ds in [ds1, ds2, ds3]:
        print(f"  {ds['name']:<20} {ds['nc']:>5}  {ds['total_images']:>6}  {ds['annotation_format']:<18} {ds['license']}")
    
    total_orig = ds1['nc'] + ds2['nc'] + ds3['nc']
    total_imgs = ds1['total_images'] + ds2['total_images'] + ds3['total_images']
    print(f"\n  TOTAL UNIQUE ORIGINAL CLASSES: {total_orig}")
    print(f"  TOTAL IMAGES: {total_imgs}")
    print(f"  TOTAL UNIQUE CANONICAL CANDIDATES: {len(overlap_df)}")
    print(f"  TOTAL CANDIDATE CLASSES: {len(cand_df)}")
    
    rel_counts = relevance_df.relevance.value_counts()
    for rel in ["HIGH","MEDIUM","LOW","EXCLUDE"]:
        print(f"  TOTAL {rel}: {rel_counts.get(rel, 0)}")
    
    rec_counts = prob_df.recommendation.value_counts()
    print(f"  TOTAL REVIEW: {rec_counts.get('REVIEW', 0)}")
    
    print(f"\n  === FINAL CANDIDATE TABLE ===")
    print(f"  {'final_candidate':<25} {'food_group':<18} {'source_dataset':<30} {'total_images':>6} {'confidence'}")
    print(f"  " + "-"*100)
    for _, r in cand_df.iterrows():
        print(f"  {r['final_candidate']:<25} {r['food_group']:<18} {r['source_dataset']:<30} {r['total_images']:>6} {r['confidence']}")
    
    print(f"\n  === OUTPUT FILES ===")
    print(f"  1. {OUT_SOURCES / 'vision_dataset_inventory.csv'}")
    print(f"  2. {OUT_MAPPING / 'class_overlap.csv'}")
    print(f"  3. {OUT_MAPPING / 'class_relevance.csv'}")
    print(f"  4. {OUT_MAPPING / 'problematic_classes.csv'}")
    print(f"  5. {OUT_MAPPING / 'final_class_candidates.csv'}")
    print(f"  6. {OUT_MAPPING / 'DATASET_AUDIT_REPORT.md'}")


if __name__ == "__main__":
    main()
