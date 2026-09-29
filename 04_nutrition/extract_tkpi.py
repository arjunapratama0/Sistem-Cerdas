#!/usr/bin/env python3
r"""
TKPI 2019 Extractor — AndraFarm
================================
Extracts TKPI 2019 nutrition table from AndraFarm's public listing page.

The data is SERVER-RENDERED HTML (confirmed: table rows with 28 columns
are present in the HTTP response HTML source). This is NOT JavaScript-
rendered content — the table is fully in the HTML.

We use requests + BeautifulSoup. The page supports perhal= parameter
to control records per page. We request ALL 1148 records in one page
(perhal=1200) to avoid pagination issues, then validate.

EXECUTION: .venv\Scripts\python.exe -u 04_nutrition\extract_tkpi.py
"""

import requests, re, json, csv, os, sys, time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

BASE = Path(r"c:\Users\Juned\Documents\Nutisi\NutriVision-Datasets")
RAW  = BASE / "04_nutrition" / "01_raw_sources"
VAL  = BASE / "04_nutrition" / "05_validation"
DOC  = BASE / "04_nutrition" / "06_documentation"
PAGES= RAW / "pages"

for d in [RAW, VAL, DOC, PAGES]:
    d.mkdir(parents=True, exist_ok=True)

TODAY = datetime.now().strftime("%Y-%m-%d")
NOW   = datetime.now().isoformat()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
}

# ============================================================
# STEP 1: Discover pagination structure
# ============================================================
def discover_pagination():
    """Fetch page 1 (default 40/page) and discover pagination."""
    print("=" * 70)
    print(" STEP 1 — Discovering pagination")
    print("=" * 70)
    
    url = 'https://www.andrafarm.com/_andra.php?_i=daftar-tkpi'
    resp = requests.get(url, timeout=60, headers=HEADERS)
    resp.encoding = 'utf-8'
    html = resp.text
    
    # Find total data count
    m = re.search(r'dari\s*<b>(\d+)</b>\s*data', html)
    total = int(m.group(1)) if m else 0
    print(f"  Total data declared: {total}")
    
    # Find perhal options
    perhal_opts = re.findall(r'<option value="(\d+)"', html)
    print(f"  Per-halaman options: {perhal_opts}")
    
    # Find pagination links
    # Pattern: _andra.php?_i=daftar-tkpi&...&hal=N
    page_links = re.findall(r'hal=(\d+)', html)
    page_nums = sorted(set(int(p) for p in page_links))
    print(f"  Page numbers found: {page_nums}")
    
    # Calculate expected pages at 40/page
    import math
    expected_pages = math.ceil(total / 40)
    print(f"  Expected pages (40/page): {expected_pages}")
    
    pagination = {
        "total_records_declared": total,
        "per_page_default": 40,
        "per_page_options": [int(x) for x in perhal_opts],
        "expected_pages": expected_pages,
        "page_numbers_on_page1": page_nums,
        "base_url": "https://www.andrafarm.com/_andra.php?_i=daftar-tkpi",
        "pagination_param": "hal",
        "perhal_param": "perhal",
        "discovery_timestamp": NOW
    }
    
    # Save pagination info
    with open(RAW / "tkpi_2019_pagination.json", 'w', encoding='utf-8') as f:
        json.dump(pagination, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {RAW / 'tkpi_2019_pagination.json'}")
    
    return pagination, html

# ============================================================
# STEP 2: Extract table from HTML
# ============================================================
def extract_table_from_html(html, page_num):
    """Parse HTML and extract TKPI table rows."""
    soup = BeautifulSoup(html, 'lxml')
    
    # Find the main data table — it has class 'adrtabel2'
    tables = soup.find_all('table', class_='adrtabel2')
    if not tables:
        # Fallback: find table with 'No.' header
        tables = soup.find_all('table')
    
    target_table = None
    for table in tables:
        ths = table.find_all('th')
        th_text = ' '.join(th.get_text(strip=True) for th in ths)
        if 'No.' in th_text and 'Kode' in th_text:
            target_table = table
            break
    
    if not target_table:
        print(f"  WARNING: No TKPI table found on page {page_num}")
        return [], []
    
    # Extract headers from th elements
    header_rows = target_table.find_all('tr')
    headers = []
    
    # The header spans 3 rows. We need to reconstruct the full column names.
    # Instead of complex rowspan/colspan handling, we know the fixed structure:
    EXPECTED_HEADERS = [
        'No.', 'Kode Baru', 'Nama Bahan Makanan',
        'Air (g)', 'Energi (Kal)', 'Protein (g)', 'Lemak (g)',
        'Karbohidrat (g)', 'Serat (g)', 'Abu (g)',
        'Kalsium (mg)', 'Fosfor (mg)', 'Besi (mg)',
        'Natrium (mg)', 'Kalium (mg)', 'Tembaga (mg)', 'Seng (mg)',
        'Retinol (mcg)', 'Beta-karoten (mcg)', 'Karoten total (mcg)',
        'Thiamin (mg)', 'Riboflavin (mg)', 'Niasin (mg)', 'Vitamin C (mg)',
        'BDD (%)',
        'Mentah/Olahan', 'Kelompok Makanan', 'Sumber'
    ]
    
    # Extract data rows (rows with exactly 28 td elements)
    data_rows = []
    for tr in target_table.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) == 28:
            row = []
            for td in tds:
                # Get text, cleaning HTML tags
                text = td.get_text(strip=True)
                # Remove non-breaking spaces and normalize
                text = text.replace('\xa0', ' ').strip()
                row.append(text)
            data_rows.append(row)
    
    return EXPECTED_HEADERS, data_rows

# ============================================================
# STEP 3: Fetch all pages
# ============================================================
def fetch_all_pages(pagination):
    """Fetch all pages of TKPI data."""
    print("\n" + "=" * 70)
    print(" STEP 2/3 — Fetching pages")
    print("=" * 70)
    
    total = pagination["total_records_declared"]
    per_page = 40  # Use default pagination
    expected_pages = pagination["expected_pages"]
    
    all_rows = []
    all_headers = None
    page_stats = []
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    for page_num in range(1, expected_pages + 1):
        url = f'https://www.andrafarm.com/_andra.php?_i=daftar-tkpi&perhal={per_page}&hal={page_num}'
        
        retry = 0
        html = None
        while retry < 3:
            try:
                resp = session.get(url, timeout=90)
                resp.encoding = 'utf-8'
                html = resp.text
                break
            except Exception as e:
                retry += 1
                print(f"  Page {page_num}: retry {retry} ({e})")
                time.sleep(5)
        
        if html is None:
            print(f"  Page {page_num}: FAILED after 3 retries")
            page_stats.append({"page": page_num, "status": "FAILED", "rows": 0})
            continue
        
        # Save HTML snapshot
        with open(PAGES / f"page_{page_num:02d}.html", 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Extract table
        headers, rows = extract_table_from_html(html, page_num)
        
        if all_headers is None and headers:
            all_headers = headers
        
        # Add metadata columns
        timestamp = datetime.now().isoformat()
        for row in rows:
            row.append(str(page_num))
            row.append(timestamp)
        
        all_rows.extend(rows)
        page_stats.append({"page": page_num, "status": "OK", "rows": len(rows)})
        
        print(f"  Page {page_num:2d}/{expected_pages}: {len(rows)} rows extracted")
        
        # Save per-page CSV
        if rows:
            with open(PAGES / f"page_{page_num:02d}.csv", 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers + ['retrieval_page', 'retrieval_timestamp'])
                writer.writerows(rows)
        
        # Be polite — wait between requests
        if page_num < expected_pages:
            time.sleep(1.5)
    
    return all_headers, all_rows, page_stats

# ============================================================
# STEP 4: Save raw CSV
# ============================================================
def save_raw_csv(headers, rows):
    """Save all rows to raw CSV."""
    print("\n" + "=" * 70)
    print(" STEP 5 — Saving raw CSV")
    print("=" * 70)
    
    full_headers = headers + ['retrieval_page', 'retrieval_timestamp']
    
    with open(RAW / "tkpi_2019_raw.csv", 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(full_headers)
        writer.writerows(rows)
    
    print(f"  Saved: {RAW / 'tkpi_2019_raw.csv'}")
    print(f"  Total rows: {len(rows)}")
    print(f"  Columns: {len(full_headers)}")

# ============================================================
# STEP 5: Validation
# ============================================================
def validate(headers, rows, page_stats):
    """Validate extracted data."""
    print("\n" + "=" * 70)
    print(" STEP 4/7/8 — Validation")
    print("=" * 70)
    
    n_headers = len(headers) + 2  # +2 for metadata
    
    # Page stats
    ok_pages = sum(1 for p in page_stats if p["status"] == "OK")
    failed_pages = sum(1 for p in page_stats if p["status"] == "FAILED")
    total_pages = len(page_stats)
    
    print(f"  Total pages: {total_pages}")
    print(f"  OK pages:    {ok_pages}")
    print(f"  Failed pages: {failed_pages}")
    
    # Record counts
    print(f"  Total rows: {len(rows)}")
    
    # Check row lengths
    bad_rows = []
    for i, row in enumerate(rows):
        if len(row) != n_headers:
            bad_rows.append({
                "row_index": i,
                "expected_cols": n_headers,
                "actual_cols": len(row),
                "data_preview": str(row[:5])
            })
    
    print(f"  Bad rows (wrong col count): {len(bad_rows)}")
    
    # Save bad rows
    if bad_rows:
        with open(VAL / "tkpi_2019_bad_rows.csv", 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["row_index","expected_cols","actual_cols","data_preview"])
            writer.writeheader()
            writer.writerows(bad_rows)
    else:
        with open(VAL / "tkpi_2019_bad_rows.csv", 'w', encoding='utf-8', newline='') as f:
            f.write("row_index,expected_cols,actual_cols,data_preview\n")
    print(f"  Saved: {VAL / 'tkpi_2019_bad_rows.csv'}")
    
    # Check Kode Baru uniqueness
    kode_col = 1  # Column index for Kode Baru
    kodes = [row[kode_col] for row in rows if len(row) > kode_col]
    
    from collections import Counter
    kode_counts = Counter(kodes)
    duplicates = {k: v for k, v in kode_counts.items() if v > 1}
    
    print(f"  Unique Kode Baru: {len(kode_counts)}")
    print(f"  Duplicate Kode Baru: {len(duplicates)}")
    
    # Save duplicates
    dup_rows = []
    for kode, count in sorted(duplicates.items()):
        dup_rows.append({"kode_baru": kode, "count": count, "note": "duplicate code found"})
    
    with open(VAL / "tkpi_2019_duplicate_codes.csv", 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["kode_baru","count","note"])
        writer.writeheader()
        writer.writerows(dup_rows)
    print(f"  Saved: {VAL / 'tkpi_2019_duplicate_codes.csv'}")
    
    # Check missing Kode Baru and Nama
    nama_col = 2
    missing_kode = sum(1 for row in rows if len(row) > kode_col and (not row[kode_col] or row[kode_col].strip() == ''))
    missing_nama = sum(1 for row in rows if len(row) > nama_col and (not row[nama_col] or row[nama_col].strip() == ''))
    
    print(f"  Missing Kode Baru: {missing_kode}")
    print(f"  Missing Nama: {missing_nama}")
    
    # Min/Max No.
    no_col = 0
    nos = []
    for row in rows:
        if len(row) > no_col:
            try:
                nos.append(int(row[no_col]))
            except:
                pass
    if nos:
        print(f"  Min No.: {min(nos)}")
        print(f"  Max No.: {max(nos)}")
    
    # Records per page
    for ps in page_stats:
        if ps["rows"] > 0:
            pass  # Already printed
    
    return {
        "total_pages": total_pages,
        "ok_pages": ok_pages,
        "failed_pages": failed_pages,
        "total_rows": len(rows),
        "unique_kode": len(kode_counts),
        "duplicate_kode": len(duplicates),
        "missing_kode": missing_kode,
        "missing_nama": missing_nama,
        "bad_rows": len(bad_rows),
        "min_no": min(nos) if nos else None,
        "max_no": max(nos) if nos else None,
    }

# ============================================================
# STEP 6: Provenance
# ============================================================
def write_provenance(stats):
    """Write provenance document."""
    doc = f"""# TKPI 2019 — Source Provenance

## Source Information

| Field | Value |
|-------|-------|
| Source | AndraFarm |
| URL | https://www.andrafarm.com/_andra.php?_i=daftar-tkpi |
| Claimed Origin | TKPI 2019 (Tabel Komposisi Pangan Indonesia 2019) |
| Provider | AndraFarm |
| Source Type | Secondary web representation |
| Retrieval Method | HTTP requests + HTML parsing (data is server-rendered HTML, NOT JavaScript) |
| Retrieval Date | {TODAY} |
| Pages Extracted | {stats['ok_pages']} of {stats['total_pages']} |
| Records Extracted | {stats['total_rows']} |
| Unique Kode Baru | {stats['unique_kode']} |
| Duplicate Kode Baru | {stats['duplicate_kode']} |

## Important Notes

1. **AndraFarm is a secondary web representation**, NOT the official Kementerian
   Kesehatan repository. The data claims to be from TKPI 2019 but this cannot
   be independently verified against the primary source without comparing to
   the official PDF or dataset.

2. **Data extraction method**: The TKPI table on AndraFarm is server-rendered
   HTML (not JavaScript-rendered). The table data is present in the HTTP
   response HTML source and was extracted using requests + BeautifulSoup.
   Browser automation (Playwright) was attempted but unavailable due to
   infrastructure issues (CDN 404 for Playwright driver).

3. **Data integrity**: All values are preserved exactly as displayed on the
   source website. No numeric conversions, no imputations, no cleaning has
   been applied. Values like "3,8" (decimal comma), "-" (not tested/missing),
   and empty strings are kept as-is.

4. **Pagination**: The website shows 40 records per page with {stats['total_pages']} pages.
   Total declared: 1148 records.

## Files Produced

| File | Description |
|------|-------------|
| `tkpi_2019_raw.csv` | Complete raw extraction, {stats['total_rows']} records |
| `tkpi_2019_pagination.json` | Pagination structure discovery |
| `tkpi_2019_duplicate_codes.csv` | Duplicate Kode Baru analysis |
| `tkpi_2019_bad_rows.csv` | Rows with structural issues |
| `pages/page_*.html` | HTML snapshots per page |
| `pages/page_*.csv` | CSV snapshots per page |
"""
    
    with open(DOC / "tkpi_2019_source.md", 'w', encoding='utf-8') as f:
        f.write(doc)
    print(f"\n  Saved: {DOC / 'tkpi_2019_source.md'}")

# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 70)
    print("  TKPI 2019 Extractor — AndraFarm")
    print(f"  Date: {TODAY}")
    print("=" * 70)
    
    # Step 1: Discover pagination
    pagination, html_page1 = discover_pagination()
    
    # Step 2/3: Fetch all pages
    headers, all_rows, page_stats = fetch_all_pages(pagination)
    
    if not all_rows:
        print("\n  ERROR: No data extracted!")
        return
    
    # Step 5: Save raw CSV
    save_raw_csv(headers, all_rows)
    
    # Step 4/7/8: Validate
    stats = validate(headers, all_rows, page_stats)
    
    # Step 9: Provenance
    write_provenance(stats)
    
    # Final Summary
    print("\n" + "=" * 70)
    print(" FINAL SUMMARY")
    print("=" * 70)
    print(f"  Pages discovered:            {stats['total_pages']}")
    print(f"  Pages successfully extracted: {stats['ok_pages']}")
    print(f"  Pages failed:                {stats['failed_pages']}")
    print(f"  Total rows:                  {stats['total_rows']}")
    print(f"  Unique Kode Baru:            {stats['unique_kode']}")
    print(f"  Duplicate Kode Baru:         {stats['duplicate_kode']}")
    print(f"  Rows with missing code:      {stats['missing_kode']}")
    print(f"  Rows with missing name:      {stats['missing_nama']}")
    print(f"  Bad rows:                    {stats['bad_rows']}")
    
    # Show first 5 and last 5 records
    print(f"\n  === FIRST 5 RECORDS ===")
    print(f"  {'No.':<5} {'Kode':<8} {'Nama':<35} {'Air':<8} {'Energi':<8} {'Protein':<8}")
    print(f"  " + "-" * 75)
    for row in all_rows[:5]:
        print(f"  {row[0]:<5} {row[1]:<8} {row[2][:33]:<35} {row[3]:<8} {row[4]:<8} {row[5]:<8}")
    
    print(f"\n  === LAST 5 RECORDS ===")
    print(f"  {'No.':<5} {'Kode':<8} {'Nama':<35} {'Air':<8} {'Energi':<8} {'Protein':<8}")
    print(f"  " + "-" * 75)
    for row in all_rows[-5:]:
        print(f"  {row[0]:<5} {row[1]:<8} {row[2][:33]:<35} {row[3]:<8} {row[4]:<8} {row[5]:<8}")
    
    print(f"\n  === OUTPUT FILES ===")
    print(f"  1. {RAW / 'tkpi_2019_raw.csv'}")
    print(f"  2. {RAW / 'tkpi_2019_pagination.json'}")
    print(f"  3. {DOC / 'tkpi_2019_source.md'}")
    print(f"  4. {VAL / 'tkpi_2019_duplicate_codes.csv'}")
    print(f"  5. {VAL / 'tkpi_2019_bad_rows.csv'}")
    print(f"  6. {PAGES}/ (HTML + CSV snapshots)")


if __name__ == "__main__":
    main()
