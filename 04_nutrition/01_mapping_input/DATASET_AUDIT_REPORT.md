# NutriVision Vision Dataset Audit Report

**Generated:** 2026-09-28  
**Auditor:** Senior CV Dataset Auditor (automated)

---

## 1. Datasets Available

### A. Food Ingredients Roboflow (`01_food_ingredients_roboflow`)

| Field | Value |
|-------|-------|
| Classes | 120 |
| Train images | 8331 |
| Valid images | 823 |
| Test images | 572 |
| Total images | 9726 |
| Annotation | YOLOv8 |
| License | CC BY 4.0 |
| Version | v4 |
| Source | https://universe.roboflow.com/food-recipe-ingredient-images-0gnku/food-ingredients-dataset/dataset/4 |
| Owner | Roboflow user |
| Download date | 2026-09-27 |
| Preprocessing | Auto-orient, resize 640x640 (stretch) |
| Augmentation | 3x augmented (h-flip, v-flip, Gaussian blur, salt&pepper) |

### B. FoodSeg103 (`02_foodseg103`)

| Field | Value |
|-------|-------|
| Classes | 103 |
| Train images | 4983 |
| Valid images | 0 (no validation split) |
| Test images | 2135 |
| Total images | 7118 |
| Annotation | Supervisely (bitmap segmentation) |
| License | Apache 2.0 |
| Version | v1 |
| Source | https://github.com/LARC-CMU-SMU/FoodSeg103-Benchmark-v1 |
| Owner | LARC-CMU-SMU |
| Download date | 2026-09-27 |
| Tags | beverage, dessert, egg, fruit, fungus, main, meat, nut, other ingredients, salad, sauce, seafood, soup, tofu, vegetable |

### C. Indonesian Food (`03_indonesian_food`)

| Field | Value |
|-------|-------|
| Classes | 11 |
| Train images | 1456 |
| Valid images | 417 |
| Test images | 208 |
| Total images | 2081 |
| Annotation | YOLOv8 |
| License | CC BY 4.0 |
| Version | v1 |
| Source | https://universe.roboflow.com/aku-yolo/deteksi-makanan-indonesia-spmyy/dataset/1 |
| Owner | Roboflow user (aku-yolo) |
| Download date | 2026-09-27 |
| Augmentation | None |

---

## 2. Class Count Summary

| Dataset | Classes | Total Images | Annotation |
|---------|---------|-------------|------------|
| Food Ingredients Roboflow | 120 | 9726 | YOLOv8 |
| FoodSeg103 | 103 | 7118 | Supervisely (bitmap segmentation) |
| Indonesian Food | 11 | 2081 | YOLOv8 |
| **Total** | **234** | **18925** | |

## 3. Train/Valid/Test Structure

| Dataset | Train | Valid | Test | Has Val Split |
|---------|-------|-------|------|---------------|
| Food Ingredients | 8331 | 823 | 572 | Yes |
| FoodSeg103 | 4983 | 0 | 2135 | No |
| Indonesian Food | 1456 | 417 | 208 | Yes |

## 4. License / Provenance

| Dataset | License | Owner | Source URL |
|---------|---------|-------|-----------|
| Food Ingredients | CC BY 4.0 | Roboflow user | [link](https://universe.roboflow.com/food-recipe-ingredient-images-0gnku/food-ingredients-dataset/dataset/4) |
| FoodSeg103 | Apache 2.0 | LARC-CMU-SMU | [link](https://github.com/LARC-CMU-SMU/FoodSeg103-Benchmark-v1) |
| Indonesian Food | CC BY 4.0 | Roboflow user (aku-yolo) | [link](https://universe.roboflow.com/aku-yolo/deteksi-makanan-indonesia-spmyy/dataset/1) |

## 5. Class Overlap

**32 classes found in 2+ datasets:**

| Canonical | Food Ingredients | FoodSeg103 | Indonesian Food |
|-----------|-----------------|------------|----------------|
| apple | Apple | apple | - |
| avocado | Avocado | avocado | - |
| banana | Banana | banana | - |
| bread | Bread | bread | - |
| broccoli | Broccoli | broccoli | - |
| cabbage | Cabbage | cabbage | - |
| carrot | Carrot | carrot | - |
| cauliflower | Cauliflower | cauliflower | - |
| corn | Corn | corn | - |
| crab | Crab Meat | crab | - |
| cucumber | Cucumber | cucumber | - |
| egg | Egg | egg | - |
| eggplant | Brinjal | eggplant | - |
| fish | Fish | fish | - |
| garlic | Garlic | garlic | - |
| ginger | Ginger | ginger | - |
| milk | Milk | milk | - |
| onion | Onion | onion | - |
| orange | Orange | orange | - |
| pear | Pear | pear | - |
| pepper | Capsicum | pepper | - |
| pork | Pork | pork | - |
| potato | Potato | potato | - |
| red beans | Red Beans | red beans | - |
| sausage | Sausage | sausage | - |
| seaweed | seaweed | seaweed | - |
| spring onion | Onion Leaves | spring onion | - |
| strawberry | Strawberry | strawberry | - |
| tofu | Tofu | tofu | - |
| tomato | Tomato | tomato | - |
| walnut | Wallnut | walnut | - |
| watermelon | Water Melon | watermelon | - |

## 6. Problematic Classes

**Total: 81 unique labels with 87 issues**

| Problem Type | Count |
|-------------|-------|
| LOW_INSTANCE_COUNT | 21 |
| CULTURE_SPECIFIC | 20 |
| SEMANTIC_OVERLAP | 14 |
| COMPOSITE_FOOD | 13 |
| NOT_FOOD_ITEM | 9 |
| AMBIGUOUS_NAME | 5 |
| BEVERAGE | 5 |

### Recommended EXCLUDE:

- **Chili Powder** (food_ingredients_roboflow): Condiment/ingredient, not a food item to recognize
- **Cinnamon** (food_ingredients_roboflow): Condiment/ingredient, not a food item to recognize
- **Ice** (food_ingredients_roboflow): Condiment/ingredient, not a food item to recognize
- **Ketchup** (food_ingredients_roboflow): Condiment/ingredient, not a food item to recognize
- **Olive Oil** (food_ingredients_roboflow): Condiment/ingredient, not a food item to recognize
- **Salt** (food_ingredients_roboflow): Condiment/ingredient, not a food item to recognize
- **Soy Sauce** (food_ingredients_roboflow): Condiment/ingredient, not a food item to recognize
- **Sugar** (food_ingredients_roboflow): Condiment/ingredient, not a food item to recognize
- **mayonnaise** (food_ingredients_roboflow): Condiment/ingredient, not a food item to recognize
- **cheese butter** (foodseg103): Name combines multiple foods or is meaningless
- **chicken duck** (foodseg103): Name combines multiple foods or is meaningless
- **cilantro mint** (foodseg103): Name combines multiple foods or is meaningless
- **other ingredients** (foodseg103): Name combines multiple foods or is meaningless
- **10** (indonesian_food): Name combines multiple foods or is meaningless

## 7. Relevance Distribution

| Relevance | Count |
|-----------|-------|
| HIGH | 103 |
| MEDIUM | 19 |
| LOW | 42 |
| EXCLUDE | 38 |

## 8. Final Class Candidates

**23 candidates selected** (strictly curated from 202 canonical candidates)

Criteria: 2+ dataset overlap preferred, minimum instance threshold, relevant to Indonesian family nutrition education, clear food identity (no composite/ambiguous), no culture-specific names.

| Final Candidate | Food Group | Source | Total Images | Confidence |
|-----------------|-----------|--------|-------------|------------|
| rice | Karbohidrat | foodseg103 | 670 | MEDIUM |
| potato | Karbohidrat | food_ingredients_roboflow, foodseg103 | 1677 | HIGH |
| corn | Karbohidrat | food_ingredients_roboflow, foodseg103 | 657 | HIGH |
| bread | Karbohidrat | food_ingredients_roboflow, foodseg103 | 1584 | HIGH |
| egg | Protein Hewani | food_ingredients_roboflow, foodseg103 | 1123 | HIGH |
| fish | Protein Hewani | food_ingredients_roboflow, foodseg103 | 359 | HIGH |
| chicken | Protein Hewani | food_ingredients_roboflow | 26 | LOW |
| shrimp | Protein Hewani | foodseg103 | 144 | MEDIUM |
| tofu | Protein Nabati | food_ingredients_roboflow, foodseg103 | 86 | MEDIUM |
| red beans | Protein Nabati | food_ingredients_roboflow, foodseg103 | 164 | HIGH |
| carrot | Sayuran | food_ingredients_roboflow, foodseg103 | 1486 | HIGH |
| tomato | Sayuran | food_ingredients_roboflow, foodseg103 | 1474 | HIGH |
| broccoli | Sayuran | food_ingredients_roboflow, foodseg103 | 1112 | HIGH |
| cabbage | Sayuran | food_ingredients_roboflow, foodseg103 | 472 | HIGH |
| cucumber | Sayuran | food_ingredients_roboflow, foodseg103 | 726 | HIGH |
| onion | Sayuran | food_ingredients_roboflow, foodseg103 | 693 | HIGH |
| eggplant | Sayuran | food_ingredients_roboflow, foodseg103 | 338 | HIGH |
| cauliflower | Sayuran | food_ingredients_roboflow, foodseg103 | 288 | HIGH |
| banana | Buah | food_ingredients_roboflow, foodseg103 | 357 | HIGH |
| apple | Buah | food_ingredients_roboflow, foodseg103 | 159 | HIGH |
| orange | Buah | food_ingredients_roboflow, foodseg103 | 256 | HIGH |
| watermelon | Buah | food_ingredients_roboflow, foodseg103 | 46 | MEDIUM |
| mango | Buah | foodseg103 | 55 | MEDIUM |

## 9. Excluded Classes and Reasons

Classes NOT selected as final candidates:

- **10**: Unknown; not a recognizable food item or too vague
- **artichoke**: Lainnya; not a recognizable food item or too vague
- **ash gourd  kubhindo**: Lainnya; not a recognizable food item or too vague
- **asparagus  kurilo**: Lainnya; not a recognizable food item or too vague
- **bakso**: Protein Hewani; directly relevant to daily nutrition education
- **bamboo shoots  tama**: Lainnya; not a recognizable food item or too vague
- **beaten rice  chiura**: Lainnya; not a recognizable food item or too vague
- **bethu ko saag**: Sayuran Daun; not primary nutritional focus
- **bika ambon**: Jajanan; not primary nutritional focus
- **biscuit**: Dessert; not primary nutritional focus
- **bottle gourd  lauka**: Lainnya; not a recognizable food item or too vague
- **broad beans  bakullo**: Lainnya; not a recognizable food item or too vague
- **cake**: Dessert; not primary nutritional focus
- **candy**: Dessert; not primary nutritional focus
- **cassava  ghar tarul**: Lainnya; not a recognizable food item or too vague
- **cheese butter**: Susu/Dairy; relevant but less common in daily meals
- **chicken duck**: Protein Hewani; directly relevant to daily nutrition education
- **chili pepper  khursani**: Lainnya; not a recognizable food item or too vague
- **chili powder**: Bumbu/Rempah; relevant but less common in daily meals
- **chocolate**: Dessert; not primary nutritional focus
- **cilantro mint**: Lainnya; not a recognizable food item or too vague
- **cinnamon**: Bumbu/Rempah; relevant but less common in daily meals
- **coffee**: Minuman; not primary nutritional focus
- **coriander  dhaniya**: Lainnya; not a recognizable food item or too vague
- **dadar gulung**: Jajanan; not primary nutritional focus
- **dried cranberries**: Buah Olahan; not primary nutritional focus
- **egg tart**: Dessert; not primary nutritional focus
- **fiddlehead ferns  niguro**: Lainnya; not a recognizable food item or too vague
- **french fries**: Makanan Olahan; not primary nutritional focus
- **fried meat**: Protein Hewani; directly relevant to daily nutrition education
- **garden cress chamsur ko saag**: Sayuran Daun; not primary nutritional focus
- **green brinjal**: Lainnya; not a recognizable food item or too vague
- **green mint  pudina**: Lainnya; not a recognizable food item or too vague
- **green soyabean  hariyo bhatmas**: Lainnya; not a recognizable food item or too vague
- **gundruk**: Makanan Olahan; not primary nutritional focus
- **hamburg**: Makanan Olahan; not primary nutritional focus
- **hanamaki baozi**: Makanan Olahan; not primary nutritional focus
- **ice**: Lainnya; not a recognizable food item or too vague
- **ice cream**: Dessert; not primary nutritional focus
- **juice**: Minuman; not primary nutritional focus
- **kelp**: Rumput Laut; not primary nutritional focus
- **ketchup**: Bumbu; not primary nutritional focus
- **kimchi**: Makanan Olahan; not primary nutritional focus
- **kue cubit**: Jajanan; not primary nutritional focus
- **lapsi  nepali hog plum**: Lainnya; not a recognizable food item or too vague
- **lemon  nimbu**: Lainnya; not a recognizable food item or too vague
- **lime  kagati**: Lainnya; not a recognizable food item or too vague
- **long beans  bodi**: Lainnya; not a recognizable food item or too vague
- **masyaura**: Makanan Olahan; not primary nutritional focus
- **mayonnaise**: Bumbu; not primary nutritional focus
- **milkshake**: Minuman; not primary nutritional focus
- **moringa leaves  sajyun ko munta**: Lainnya; not a recognizable food item or too vague
- **nasi goreng**: Karbohidrat; directly relevant to daily nutrition education
- **nutrela  soya chunks**: Lainnya; not a recognizable food item or too vague
- **okra  bhindi**: Lainnya; not a recognizable food item or too vague
- **olive oil**: Minyak; not primary nutritional focus
- **other ingredients**: Lainnya; not a recognizable food item or too vague
- **palak  indian spinach**: Lainnya; not a recognizable food item or too vague
- **palungo  nepali spinach**: Lainnya; not a recognizable food item or too vague
- **pea**: Protein Nabati; directly relevant to daily nutrition education
- **pepes ikan**: Protein Hewani; directly relevant to daily nutrition education
- **pie**: Dessert; not primary nutritional focus
- **pizza**: Makanan Olahan; not primary nutritional focus
- **pointed gourd  chuche karela**: Lainnya; not a recognizable food item or too vague
- **popcorn**: Snack; not primary nutritional focus
- **pudding**: Dessert; not primary nutritional focus
- **pumpkin  farsi**: Lainnya; not a recognizable food item or too vague
- **putu ayu**: Jajanan; not primary nutritional focus
- **rayo ko saag**: Sayuran Daun; not primary nutritional focus
- **rendang**: Protein Hewani; directly relevant to daily nutrition education
- **rice  chamal**: Lainnya; not a recognizable food item or too vague
- **sajjyun  moringa drumsticks**: Lainnya; not a recognizable food item or too vague
- **salad**: Makanan Olahan; not primary nutritional focus
- **salt**: Bumbu; not primary nutritional focus
- **sate ayam**: Protein Hewani; directly relevant to daily nutrition education
- **sauce**: Bumbu; not primary nutritional focus
- **sausage**: Protein Hewani; directly relevant to daily nutrition education
- **seaweed**: Rumput Laut; not primary nutritional focus
- **snake gourd  chichindo**: Lainnya; not a recognizable food item or too vague
- **soup**: Makanan Olahan; not primary nutritional focus
- **soy sauce**: Bumbu; not primary nutritional focus
- **soyabean  bhatmas**: Lainnya; not a recognizable food item or too vague
- **sponge gourd  ghiraula**: Lainnya; not a recognizable food item or too vague
- **steak**: Protein Hewani; directly relevant to daily nutrition education
- **stinging nettle  sisnu**: Lainnya; not a recognizable food item or too vague
- **sugar**: Bumbu; not primary nutritional focus
- **sweet potato  suthuni**: Lainnya; not a recognizable food item or too vague
- **taro leaves  karkalo**: Lainnya; not a recognizable food item or too vague
- **tea**: Minuman; not primary nutritional focus
- **telur balado**: Protein Hewani; directly relevant to daily nutrition education
- **tori ko saag**: Sayuran Daun; not primary nutritional focus
- **tree tomato  rukh tamatar**: Lainnya; not a recognizable food item or too vague
- **wheat**: Karbohidrat; directly relevant to daily nutrition education
- **wine**: Minuman; not primary nutritional focus
- **wonton dumplings**: Makanan Olahan; not primary nutritional focus

## 10. Dataset Source Recommendations

For each final candidate, recommended source:

| Candidate | Primary Source | Support Source | Notes |
|-----------|---------------|---------------|-------|
| rice | foodseg103 | - | 670 instances; pokok Indonesia |
| potato | food_ingredients_roboflow | foodseg103 | 1677 instances; 2 datasets |
| corn | food_ingredients_roboflow | foodseg103 | 657 instances; 2 datasets |
| bread | food_ingredients_roboflow | foodseg103 | 1584 instances; 2 datasets |
| egg | food_ingredients_roboflow | foodseg103 | 1123 instances; 2 datasets |
| fish | food_ingredients_roboflow | foodseg103 | 359 instances; 2 datasets |
| chicken | food_ingredients_roboflow | - | Only 26 instances; needs augmentation |
| shrimp | foodseg103 | - | 144 instances |
| tofu | food_ingredients_roboflow | foodseg103 | 86 instances; 2 datasets |
| red beans | food_ingredients_roboflow | foodseg103 | 164 instances; 2 datasets |
| carrot | food_ingredients_roboflow | foodseg103 | 1486 instances; 2 datasets |
| tomato | food_ingredients_roboflow | foodseg103 | 1474 instances; 2 datasets |
| broccoli | food_ingredients_roboflow | foodseg103 | 1112 instances; 2 datasets |
| cabbage | food_ingredients_roboflow | foodseg103 | 472 instances; 2 datasets |
| cucumber | food_ingredients_roboflow | foodseg103 | 726 instances; 2 datasets |
| onion | food_ingredients_roboflow | foodseg103 | 693 instances; 2 datasets |
| eggplant | food_ingredients_roboflow | foodseg103 | 338 instances; 2 datasets |
| cauliflower | food_ingredients_roboflow | foodseg103 | 288 instances; 2 datasets |
| banana | food_ingredients_roboflow | foodseg103 | 357 instances; 2 datasets |
| apple | food_ingredients_roboflow | foodseg103 | 159 instances; 2 datasets |
| orange | food_ingredients_roboflow | foodseg103 | 256 instances; 2 datasets |
| watermelon | food_ingredients_roboflow | foodseg103 | 46 instances; 2 datasets |
| mango | foodseg103 | - | 55 instances |

## 11. Overall Summary Statistics

| Metric | Value |
|--------|-------|
| Total Original Classes | 234 |
| Unique Canonical Candidates | 202 |
| **Final Candidates (strict)** | **23** |
| HIGH confidence | 17 |
| MEDIUM confidence | 5 |
| LOW confidence | 1 |
| HIGH relevance (all candidates) | 103 |
| MEDIUM relevance | 19 |
| LOW relevance | 42 |
| EXCLUDE | 38 |
| REVIEW needed | 73 |

### Food Group Distribution (Final 23)

| Food Group | Count |
|-----------|-------|
| Karbohidrat | 4 |
| Protein Hewani | 4 |
| Protein Nabati | 2 |
| Sayuran | 8 |
| Buah | 5 |

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
