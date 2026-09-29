# Sistem-Cerdas — NutriVision Datasets & Nutrition Pipeline

Repositori ini berisi dataset visi komputer (computer vision) dan data komposisi nutrisi pangan Indonesia untuk sistem cerdas deteksi dan estimasi gizi makanan.

---

## Struktur Direktori

```
├── .gitignore
├── README.md
├── 00_sources/                     # Inventarisasi dan laporan sumber dataset
│   ├── DOWNLOAD_REPORT.md
│   └── vision_dataset_inventory.csv
├── 01_food_ingredients_roboflow/   # Dataset bahan pangan (Roboflow YOLOv8)
│   └── SOURCE.txt
├── 02_foodseg103/                  # FoodSeg103 benchmark semantic segmentation
│   └── SOURCE.txt
├── 03_indonesian_food/             # Dataset deteksi makanan Indonesia (Roboflow)
│   └── SOURCE.txt
└── 04_nutrition/                   # Pipeline dan basis data komposisi gizi pangan
    ├── 01_TKPI_Kemenkes/           # TKPI 2020 resmi dari Kementerian Kesehatan RI (PDF)
    │   └── SOURCE.txt
    ├── 01_raw_sources/             # Hasil ekstraksi raw publik (TKPI 2019 AndraFarm)
    │   ├── tkpi_2019_raw.csv       # 1.148 record nutrisi lengkap (28 parameter gizi)
    │   ├── tkpi_2019_pagination.json
    │   └── pages/                  # Snapshot HTML & CSV per halaman (29 halaman)
    ├── 02_Bapanas/                 # Komposisi pangan segar Bapanas (64 komoditas)
    ├── 03_mapping/                 # Pemetaan bahan makanan ke database nutrisi
    ├── 04_final/                   # Dataset final siap integrasi sistem
    ├── 05_validation/              # Laporan validasi duplikasi & struktur baris
    ├── 06_documentation/           # Dokumentasi sumber dan metodologi
    ├── scrape_tkpi_andrafarm.py    # Skrip browser automation (Playwright)
    ├── build_nutrition_db.py       # Pembangun database nutrisi
    ├── build_all.py                # Pipeline integrasi
    └── audit_vision_datasets.py    # Audit dataset visi
```

---

## Dataset Komposisi Nutrisi (04_nutrition)

1. **TKPI 2019 Raw (AndraFarm):**
   - 1.148 record bahan makanan Indonesia
   - 28 parameter nutrisi (Energi, Protein, Lemak, Karbohidrat, Serat, Kalsium, Besi, Vitamin, BDD, dll.)
   - Diekstrak menggunakan Playwright Browser Automation dari 29 halaman pagination publik tanpa mengubah nilai nutrisi (raw).

2. **TKPI 2020 Resmi Kemenkes:**
   - Buku resmi Kementerian Kesehatan Republik Indonesia (*Tabel Komposisi Pangan Indonesia 2020*).

3. **Bapanas (Tabel Komposisi Pangan Segar Indonesia):**
   - 64 file komoditas pangan segar hasil uji laboratorium Badan Pangan Nasional.

---

## Lisensi & Atribusi

- Data nutrisi bersumber dari Kementerian Kesehatan RI dan Badan Pangan Nasional.
- Dataset visi bersumber dari Roboflow Universe dan FoodSeg103 (Supervisely / Dataset Ninja).
