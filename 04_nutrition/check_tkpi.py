"""Check TKPI listing page structure."""
import requests, re

url = 'https://www.andrafarm.com/_andra.php?_i=daftar-tkpi'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
resp = requests.get(url, timeout=60, headers=headers)
resp.encoding = 'utf-8'
html = resp.text
print(f'HTML length: {len(html)}')

# Search for key patterns
for kw in ['Kode Baru','Nama Bahan','No.','Energi','Protein','Air (g)','pagination','halaman','next','prev','page=','hal=']:
    idx = html.find(kw)
    if idx >= 0:
        snippet = html[max(0,idx-150):idx+300]
        print(f'\n=== FOUND "{kw}" at pos {idx} ===')
        print(snippet)

# Look for links with page numbers
pages = re.findall(r'href=["\']([^"\']*(?:hal|page|tkpi)[^"\']*)["\']', html, re.IGNORECASE)
print(f'\nPagination links found: {len(pages)}')
for p in pages[:20]:
    print(f'  {p}')

# Look for table rows with data 
trs = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
print(f'\nTotal <tr> tags: {len(trs)}')
# Check for rows that look like nutrition data (contain numbers)
data_rows = 0
for tr in trs:
    tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL)
    if len(tds) >= 5:
        text = ' '.join(td.strip()[:30] for td in tds[:5])
        if re.search(r'\d', text):
            data_rows += 1
            if data_rows <= 3:
                print(f'\n  Data row {data_rows} ({len(tds)} cols): {text}')
print(f'\nData-like rows: {data_rows}')
