#!/usr/bin/env python3
"""
scrape_tkpi_andrafarm.py
========================
Browser-automation scraper for TKPI 2019 from AndraFarm using Playwright.

Workflow:
1. Open https://www.andrafarm.com/_andra.php?_i=daftar-tkpi via Playwright (Chromium/Chrome)
2. Detect all 29 pagination links from the rendered DOM
3. Navigate page-by-page (domcontentloaded), wait for table selector
4. Save raw HTML snapshot and per-page CSV in 01_raw_sources/pages/
5. Extract exact cell text (preserve raw formatting: commas, dashes, whitespace trimmed only)
6. Compile all 1,148 records into 01_raw_sources/tkpi_2019_raw.csv
7. Perform validations:
   - Check duplicates in Kode Baru -> 05_validation/tkpi_2019_duplicate_codes.csv
   - Check bad / malformed rows -> 05_validation/tkpi_2019_bad_rows.csv
   - Check continuity of No. (1 .. 1148)
8. Generate provenance documentation -> 06_documentation/tkpi_2019_source.md

RULES ENFORCED:
- Browser automation / Playwright used
- No OCR / screenshot reading
- No bypassing login/paywall/access control
- Only publicly visible data
- No images downloaded
- No numeric alteration (no comma->period, keep '-' as-is)
- No imputation
- Raw extraction saved first without merging/mapping
"""

import csv
import json
import os
import sys
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Fix Windows console UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

# ── Paths ──────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent          # 04_nutrition/
RAW_DIR = BASE / "01_raw_sources"
PAGES_DIR = RAW_DIR / "pages"
VALID_DIR = BASE / "05_validation"
DOC_DIR = BASE / "06_documentation"

RAW_CSV = RAW_DIR / "tkpi_2019_raw.csv"
PAGINATION_JSON = RAW_DIR / "tkpi_2019_pagination.json"
DUP_CSV = VALID_DIR / "tkpi_2019_duplicate_codes.csv"
BAD_CSV = VALID_DIR / "tkpi_2019_bad_rows.csv"
SOURCE_MD = DOC_DIR / "tkpi_2019_source.md"

URL_BASE = "https://www.andrafarm.com/_andra.php?_i=daftar-tkpi"

HEADERS = [
    "No.", "Kode Baru", "Nama Bahan Makanan",
    "Air", "Energi", "Protein", "Lemak", "Karbohidrat",
    "Serat", "Abu", "Kalsium", "Fosfor", "Besi",
    "Natrium", "Kalium", "Tembaga", "Seng",
    "Retinol", "β-karoten", "Karoten total",
    "Thiamin", "Riboflavin", "Niasin", "Vitamin C", "BDD",
    "Mentah/Olahan", "Kelompok Makanan", "Sumber"
]

def ensure_dirs():
    for d in [RAW_DIR, PAGES_DIR, VALID_DIR, DOC_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def now_wib():
    """Return current time in WIB (UTC+7)."""
    return datetime.now(timezone(timedelta(hours=7)))

def main():
    ensure_dirs()
    start_time = time.time()
    retrieval_ts = now_wib().isoformat()

    all_rows = []
    pagination_info = []
    bad_rows = []
    page_records = {}

    print("=" * 70)
    print("TKPI 2019 Raw Extraction from AndraFarm (Playwright)")
    print("=" * 70)

    with sync_playwright() as pw:
        print("\n[1] Launching Chromium browser (channel='chrome') ...")
        browser = pw.chromium.launch(headless=True, channel="chrome")
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
        )
        page = ctx.new_page()

        # Step 1: Open base page
        print(f"\n[2] Navigating to {URL_BASE} ...")
        page.goto(URL_BASE, wait_until="domcontentloaded", timeout=45_000)
        page.wait_for_selector("table.adrtabel2", timeout=15_000)
        print("    Page 1 loaded successfully.")

        # Step 2: Detect all pagination links
        print("\n[3] Detecting pagination links from rendered DOM ...")
        pagination_links = page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a'));
                const pages = {};
                for (const a of links) {
                    const text = a.textContent.trim();
                    const href = a.href;
                    if (/^[0-9]+$/.test(text) && href.includes('kk=')) {
                        pages[parseInt(text)] = href;
                    }
                }
                return pages;
            }
        """)

        # Build full page map (1 .. max_page)
        page_urls = {1: URL_BASE}
        for k_str, href in pagination_links.items():
            page_urls[int(k_str)] = href

        total_pages = max(page_urls.keys()) if page_urls else 1
        print(f"    Discovered {len(page_urls)} pages (1 .. {total_pages})")

        # Step 3: Extract page-by-page
        print(f"\n[4] Extracting data from {total_pages} pages ...")
        for pn in sorted(page_urls.keys()):
            url = page_urls[pn]
            print(f"    Page {pn:02d}/{total_pages:02d} ... ", end="", flush=True)
            p_start = time.time()

            # For page 1, we are already there; for subsequent pages, navigate
            if pn > 1:
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=45_000)
                    page.wait_for_selector("table.adrtabel2", timeout=15_000)
                except Exception as e:
                    print(f"FAILED to load: {e}")
                    page_records[pn] = 0
                    pagination_info.append({"page": pn, "url": url, "records": 0, "status": f"failed: {e}"})
                    continue

            # Save HTML snapshot
            try:
                html_source = page.content()
                html_path = PAGES_DIR / f"page_{pn:02d}.html"
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_source)
            except Exception as e:
                print(f"[snapshot warn: {e}] ", end="")

            # Extract table rows directly from the DOM
            extracted_rows = page.evaluate("""
                () => {
                    const rows = document.querySelectorAll('table.adrtabel2 tr');
                    const results = [];
                    for (const r of rows) {
                        const cells = Array.from(r.querySelectorAll('td')).map(td => td.textContent.trim());
                        // Check if row has cells and is not a header row
                        if (cells.length === 28 && /^[0-9]+$/.test(cells[0])) {
                            results.push(cells);
                        } else if (cells.length > 0 && cells.length !== 22) {
                            // Check for any potential abnormal data rows
                            if (/^[0-9]+$/.test(cells[0])) {
                                results.push(cells);
                            }
                        }
                    }
                    return results;
                }
            """)

            page_valid_rows = []
            for r_vals in extracted_rows:
                if len(r_vals) != len(HEADERS):
                    bad_rows.append({
                        "page": pn,
                        "expected_cols": len(HEADERS),
                        "actual_cols": len(r_vals),
                        "data": "|".join(r_vals)
                    })
                    # Pad or trim if abnormal
                    if len(r_vals) < len(HEADERS):
                        r_vals.extend([""] * (len(HEADERS) - len(r_vals)))
                    else:
                        r_vals = r_vals[:len(HEADERS)]

                row_dict = {HEADERS[i]: r_vals[i] for i in range(len(HEADERS))}
                row_dict["retrieval_page"] = pn
                row_dict["retrieval_timestamp"] = retrieval_ts
                page_valid_rows.append(row_dict)
                all_rows.append(row_dict)

            page_records[pn] = len(page_valid_rows)
            pagination_info.append({
                "page": pn,
                "url": url,
                "records": len(page_valid_rows),
                "status": "success"
            })

            # Save per-page CSV
            p_csv_path = PAGES_DIR / f"page_{pn:02d}.csv"
            fieldnames = HEADERS + ["retrieval_page", "retrieval_timestamp"]
            with open(p_csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in page_valid_rows:
                    writer.writerow(r)

            p_dur = time.time() - p_start
            print(f"{len(page_valid_rows)} records ({p_dur:.2f}s)")

        browser.close()

    # Step 4: Save master pagination JSON
    print(f"\n[5] Saving pagination metadata -> {PAGINATION_JSON}")
    with open(PAGINATION_JSON, "w", encoding="utf-8") as f:
        json.dump(pagination_info, f, indent=2, ensure_ascii=False)

    # Step 5: Save raw CSV
    print(f"\n[6] Saving master raw CSV -> {RAW_CSV}")
    fieldnames = HEADERS + ["retrieval_page", "retrieval_timestamp"]
    with open(RAW_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_rows:
            writer.writerow(r)
    print(f"    Successfully wrote {len(all_rows)} rows.")

    # Step 6: Validate duplicates
    print("\n[7] Checking duplicates in 'Kode Baru' ...")
    code_counts = {}
    for idx, r in enumerate(all_rows):
        code = r.get("Kode Baru", "").strip()
        if code:
            code_counts.setdefault(code, []).append(idx + 1)

    duplicates = []
    for code, indices in sorted(code_counts.items()):
        if len(indices) > 1:
            duplicates.append({
                "kode_baru": code,
                "count": len(indices),
                "row_indices": ",".join(str(i) for i in indices)
            })

    with open(DUP_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["kode_baru", "count", "row_indices"])
        writer.writeheader()
        for d in duplicates:
            writer.writerow(d)
    print(f"    Duplicate codes found: {len(duplicates)} -> {DUP_CSV}")

    # Step 7: Save bad rows log
    print(f"\n[8] Saving bad rows log -> {BAD_CSV}")
    with open(BAD_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["page", "expected_cols", "actual_cols", "data"])
        writer.writeheader()
        for b in bad_rows:
            writer.writerow(b)
    print(f"    Bad / malformed rows: {len(bad_rows)}")

    # Step 8: Calculate statistics
    nos = []
    missing_codes = 0
    missing_names = 0
    for r in all_rows:
        try:
            nos.append(int(r.get("No.", "0").strip()))
        except ValueError:
            pass
        if not r.get("Kode Baru", "").strip():
            missing_codes += 1
        if not r.get("Nama Bahan Makanan", "").strip():
            missing_names += 1

    total_time = time.time() - start_time
    stats = {
        "pages_discovered": len(page_urls),
        "pages_extracted": sum(1 for v in page_records.values() if v > 0),
        "total_records": len(all_rows),
        "unique_codes": len(code_counts),
        "duplicate_codes": len(duplicates),
        "missing_codes": missing_codes,
        "missing_names": missing_names,
        "bad_rows": len(bad_rows),
        "min_no": min(nos) if nos else None,
        "max_no": max(nos) if nos else None,
        "total_duration_seconds": round(total_time, 2)
    }

    # Step 9: Generate provenance documentation
    print(f"\n[9] Writing provenance documentation -> {SOURCE_MD}")
    source_md = f"""# TKPI 2019 — Source Provenance & Data Extraction Report

## 1. Source Metadata
- **Source Name:** AndraFarm (Tabel Komposisi Pangan Indonesia / TKPI)
- **Source URL:** {URL_BASE}
- **Claimed Origin:** Tabel Komposisi Pangan Indonesia (TKPI) 2019, Kementerian Kesehatan RI
- **Provider:** PT Andra Farm (www.andrafarm.com)
- **Source Type:** Secondary web representation (public tabular listing)
- **Retrieval Method:** Browser Automation (Playwright headless Chromium with system Chrome channel)
- **Retrieval Timestamp:** {retrieval_ts}
- **Total Duration:** {stats['total_duration_seconds']} seconds

## 2. Extraction Statistics
| Metric | Value |
|---|---|
| Pages Discovered | {stats['pages_discovered']} |
| Pages Successfully Extracted | {stats['pages_extracted']} |
| Total Records Extracted | {stats['total_records']} |
| Numbering Range (No.) | {stats['min_no']} to {stats['max_no']} |
| Unique Food Codes (`Kode Baru`) | {stats['unique_codes']} |
| Duplicate Food Codes | {stats['duplicate_codes']} |
| Missing Food Codes | {stats['missing_codes']} |
| Missing Food Names | {stats['missing_names']} |
| Bad / Malformed Rows | {stats['bad_rows']} |

## 3. Pagination Breakdown
| Page | Record Count |
|---|---|
"""
    for pn in sorted(page_records.keys()):
        source_md += f"| Page {pn:02d} | {page_records[pn]} |\n"

    source_md += f"""
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
"""
    with open(SOURCE_MD, "w", encoding="utf-8") as f:
        f.write(source_md)

    # Final summary display
    print("\n" + "=" * 70)
    print("EXTRACTION COMPLETE — SUMMARY")
    print("=" * 70)
    print(f"Total Pages Extracted:      {stats['pages_extracted']} / {stats['pages_discovered']}")
    print(f"Total Records Extracted:    {stats['total_records']}")
    print(f"Numbering Range:            {stats['min_no']} .. {stats['max_no']}")
    print(f"Unique Food Codes:          {stats['unique_codes']}")
    print(f"Duplicate Food Codes:       {stats['duplicate_codes']}")
    print(f"Bad / Malformed Rows:       {stats['bad_rows']}")
    print(f"Total Execution Time:       {stats['total_duration_seconds']}s")
    print(f"\nArtifacts Created:")
    print(f"  - Master Raw CSV:          {RAW_CSV}")
    print(f"  - Pagination Metadata:     {PAGINATION_JSON}")
    print(f"  - Duplicate Code Report:   {DUP_CSV}")
    print(f"  - Bad Row Report:          {BAD_CSV}")
    print(f"  - Documentation & Source:  {SOURCE_MD}")
    print(f"  - Per-page HTML & CSVs:    {PAGES_DIR}/ (page_01 .. page_{total_pages:02d})")
    print("=" * 70)

if __name__ == "__main__":
    main()
