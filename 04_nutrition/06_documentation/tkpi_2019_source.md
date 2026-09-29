# TKPI 2019 — Source Provenance & Data Extraction Report

## 1. Source Metadata
- **Source Name:** AndraFarm (Tabel Komposisi Pangan Indonesia / TKPI)
- **Source URL:** https://www.andrafarm.com/_andra.php?_i=daftar-tkpi
- **Claimed Origin:** Tabel Komposisi Pangan Indonesia (TKPI) 2019, Kementerian Kesehatan RI
- **Provider:** PT Andra Farm (www.andrafarm.com)
- **Source Type:** Secondary web representation (public tabular listing)
- **Retrieval Method:** Browser Automation (Playwright headless Chromium with system Chrome channel)
- **Retrieval Timestamp:** 2026-09-29T09:03:14.122507+07:00
- **Total Duration:** 10.16 seconds

## 2. Extraction Statistics
| Metric | Value |
|---|---|
| Pages Discovered | 29 |
| Pages Successfully Extracted | 29 |
| Total Records Extracted | 1148 |
| Numbering Range (No.) | 1 to 1148 |
| Unique Food Codes (`Kode Baru`) | 1148 |
| Duplicate Food Codes | 0 |
| Missing Food Codes | 0 |
| Missing Food Names | 0 |
| Bad / Malformed Rows | 0 |

## 3. Pagination Breakdown
| Page | Record Count |
|---|---|
| Page 01 | 40 |
| Page 02 | 40 |
| Page 03 | 40 |
| Page 04 | 40 |
| Page 05 | 40 |
| Page 06 | 40 |
| Page 07 | 40 |
| Page 08 | 40 |
| Page 09 | 40 |
| Page 10 | 40 |
| Page 11 | 40 |
| Page 12 | 40 |
| Page 13 | 40 |
| Page 14 | 40 |
| Page 15 | 40 |
| Page 16 | 40 |
| Page 17 | 40 |
| Page 18 | 40 |
| Page 19 | 40 |
| Page 20 | 40 |
| Page 21 | 40 |
| Page 22 | 40 |
| Page 23 | 40 |
| Page 24 | 40 |
| Page 25 | 40 |
| Page 26 | 40 |
| Page 27 | 40 |
| Page 28 | 40 |
| Page 29 | 28 |

## 4. Column Schema (28 Raw Columns)
1. `No.` — Sequential item number (1..1148)
2. `Kode Baru` — Food item code in TKPI 2019 (e.g. AP001, NP011)
3. `Nama Bahan Makanan` — Food item name
4. `Air` — Water content (g)
5. `Energi` — Energy (Kal)
6. `Protein` — Protein (g)
7. `Lemak` — Fat (g)
8. `Karbohidrat` — Carbohydrates (g)
9. `Serat` — Dietary fiber (g)
10. `Abu` — Ash (g)
11. `Kalsium` — Calcium (mg)
12. `Fosfor` — Phosphorus (mg)
13. `Besi` — Iron (mg)
14. `Natrium` — Sodium (mg)
15. `Kalium` — Potassium (mg)
16. `Tembaga` — Copper (mg)
17. `Seng` — Zinc (mg)
18. `Retinol` — Retinol / Vitamin A (mcg)
19. `β-karoten` — Beta-carotene (mcg)
20. `Karoten total` — Total carotene (mcg)
21. `Thiamin` — Thiamin / Vitamin B1 (mg)
22. `Riboflavin` — Riboflavin / Vitamin B2 (mg)
23. `Niasin` — Niacin / Vitamin B3 (mg)
24. `Vitamin C` — Vitamin C (mg)
25. `BDD` — Bagian yang Dapat Dimakan / Edible portion (%)
26. `Mentah/Olahan` — Raw or processed state (Mentah / Olahan)
27. `Kelompok Makanan` — Food group category
28. `Sumber` — Citation / source literature code

Plus metadata tracking columns:
- `retrieval_page` — Page number where the record was scraped from
- `retrieval_timestamp` — ISO 8601 timestamp of extraction

## 5. Methodological Constraints & Rules Adhered To
1. **Browser Automation:** Playwright was utilized to render the DOM and access the publicly visible table structure.
2. **No OCR / Screenshots:** Data was extracted strictly via DOM element traversal.
3. **No Auth Bypass:** Only freely accessible public pages were fetched.
4. **No Image Scraping:** Nutrition table text only; no multimedia assets downloaded.
5. **No Numeric Transformation:** All values are saved in their pure raw form (preserving Indonesian decimal commas, e.g. `56,7`, and hyphen dashes `-` for unmeasured nutrients).
6. **No Imputation:** Missing or unmeasured values are preserved as raw `-` or blank without artificial imputation.
7. **No Premature Mapping:** Extracted strictly as raw source dataset before any downstream matching to vision datasets.

## 6. Authoritative Caveat
AndraFarm is a **secondary web aggregator** of TKPI data and is not an official government agency. For critical clinical or regulatory purposes, figures should be cross-referenced with the official Ministry of Health publication (*Tabel Komposisi Pangan Indonesia 2019*, Kementerian Kesehatan RI).
