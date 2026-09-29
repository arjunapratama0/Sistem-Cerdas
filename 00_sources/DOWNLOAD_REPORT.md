# Laporan Unduhan Dataset NutriVision (DOWNLOAD_REPORT)

Tanggal: 27 September 2026

## Ringkasan Status Dataset

| Dataset | Source | Version | Format | License | File | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FOOD-INGREDIENTS dataset** | [Roboflow Universe](https://universe.roboflow.com/food-recipe-ingredient-images-0gnku/food-ingredients-dataset) | Latest Public | YOLOv8 | CC BY 4.0 | - | **Memerlukan Tindakan Manual** (Login Roboflow) |
| **FoodSeg103** | [LARC-CMU-SMU GitHub](https://github.com/LARC-CMU-SMU/FoodSeg103-Benchmark-v1) / [Dataset Ninja Mirror](https://datasetninja.com/food-seg-103) | Benchmark v1 | Semantic Segmentation (Supervisely format) | Apache 2.0 | `foodseg103-DatasetNinja.tar` | **Berhasil Diunduh** (Mirror Aktif) |
| **Deteksi Makanan Indonesia** | [Roboflow Universe](https://universe.roboflow.com/aku-yolo/deteksi-makanan-indonesia-spmyy) | Latest Public | YOLOv8 | CC BY 4.0 | - | **Memerlukan Tindakan Manual** (Login Roboflow) |
| **TKPI Kemenkes 2020** | [Repository Kemkes](https://repository.kemkes.go.id/book/668) | 2020 | PDF | Hak Cipta Kemenkes RI (Open Access) | `TKPI_2020.pdf` | **Berhasil Diunduh** |
| **Tabel Komposisi Pangan Segar Indonesia (TKPSI)** | [Badan Pangan Nasional](https://badanpangan.go.id/tabel-komposisi-pangan-segar-indonesia) | Edisi Resmi | Excel (`.xlsx`) | Data Publik Resmi Bapanas | `Tabel_Komposisi_Pangan_Segar_Indonesia.xlsx` (+ 64 file komoditas) | **Berhasil Diunduh** |

---

## Rincian File yang Berhasil Diunduh

### 1. Total File Diunduh
- **Total Arsip / Master File Utama:** 3 Dataset (1 File Tar Dataset Visi Komputer, 1 Dokumen PDF Resmi, 1 Master Workbook Excel + 64 File Excel Komoditas Resmi + 1 Webpage Snapshot)
- **Total Ukuran Data Terunduh:** ~1.24 GB (1,330,342,456 bytes)

### 2. Ukuran dan Folder Penyimpanan Masing-Masing File

#### A. FoodSeg103
- **Folder Penyimpanan:** `02_foodseg103/`
- **File:** `foodseg103-DatasetNinja.tar`
- **Ukuran:** 1,323,345,920 bytes (~1.23 GB)
- **Metadata:** `02_foodseg103/SOURCE.txt`
- **Catatan Sumber:** Server resmi SMU (`research.larc.smu.edu.sg/downloads/datarepo/FoodSeg103.zip`) mengembalikan status `502 Bad Gateway`. Berdasarkan instruksi, unduhan dialihkan ke public mirror resmi Dataset Ninja yang dirilis oleh Supervisely (`dropbox.com/scl/fi/nikp3qykx02qefhjwjrm4/foodseg103-DatasetNinja.tar`). File berisi arsip data penuh (train/test images, masks, dan anotasi).

#### B. TKPI Kemenkes 2020
- **Folder Penyimpanan:** `04_nutrition/01_TKPI_Kemenkes/`
- **File:** `TKPI_2020.pdf`
- **Ukuran:** 6,270,131 bytes (~5.98 MB)
- **Metadata:** `04_nutrition/01_TKPI_Kemenkes/SOURCE.txt`
- **Catatan Sumber:** Diunduh langsung dari dokumen asli terbitan Kementerian Kesehatan RI tahun 2020 (140 halaman lengkap tanpa konversi/modifikasi).

#### C. Bapanas (Tabel Komposisi Pangan Segar Indonesia)
- **Folder Penyimpanan:** `04_nutrition/02_Bapanas/`
- **File Master Workbook:** `Tabel_Komposisi_Pangan_Segar_Indonesia.xlsx` (465,904 bytes)
- **File Komoditas Individual:** 64 file `.xlsx` (masing-masing ~21.9 KB, total ~1.4 MB), meliputi:
  - `Beras.xlsx`, `Beras_Ketan.xlsx`, `Jagung_Segar.xlsx`, `Jagung_Pipil.xlsx`, `Kentang.xlsx`, `Singkong.xlsx`, `Ubi_Jalar.xlsx`, `Talas.xlsx`, `Sagu.xlsx`, `Ikan_Lele.xlsx`, `Ikan_Bandeng.xlsx`, `Ikan_Mujair.xlsx`, `Ikan_Tongkol.xlsx`, `Ikan_Kembung.xlsx`, `Ikan_Tuna.xlsx`, `Udang.xlsx`, `Cumi.xlsx`, `Daging_Ayam.xlsx`, `Daging_Ayam_Kampung.xlsx`, `Daging_Sapi.xlsx`, `Telur_Ayam.xlsx`, `Telur_Ayam_Kampung.xlsx`, `Telur_Puyuh.xlsx`, `Susu_Sapi_Segar.xlsx`, `Tomat.xlsx`, `Bayam.xlsx`, `Kangkung.xlsx`, `Kacang_Panjang.xlsx`, `Wortel.xlsx`, `Sawi_Hijau.xlsx`, `Terong.xlsx`, `Buncis.xlsx`, `Tauge.xlsx`, `Daun_Ketela_Pohon.xlsx`, `Pakcoy.xlsx`, `Labu_Siam.xlsx`, `Kubis.xlsx`, `Mentimun.xlsx`, `Sawi_Putih.xlsx`, `Selada.xlsx`, `Jamur_Tiram.xlsx`, `Kembang_Kol.xlsx`, `Bawang_Merah.xlsx`, `Bawang_Putih.xlsx`, `Cabe_Merah.xlsx`, `Cabe_Rawit.xlsx`, `Kacang_Kedelai.xlsx`, `Kacang_Tanah.xlsx`, `Jeruk.xlsx`, `Pisang.xlsx`, `Apel.xlsx`, `Pepaya.xlsx`, `Semangka.xlsx`, `Salak.xlsx`, `Mangga.xlsx`, `Nanas_Madu.xlsx`, `Buah_Naga.xlsx`, `Jambu_Biji.xlsx`, `Melon.xlsx`, `Anggur_Merah.xlsx`, `Minyak_Goreng.xlsx`, `Minyak_Kelapa.xlsx`, `Kelapa.xlsx`, `Tepung_Terigu.xlsx`.
- **File Snapshot Web:** `page.html` (260,501 bytes)
- **Metadata:** `04_nutrition/02_Bapanas/SOURCE.txt`
- **Catatan Sumber:** Bapanas merilis data uji laboratorium ini melalui portal interaktif resmi dengan tombol unduh bawaan SheetJS. Seluruh 64 komoditas diekspor menggunakan fungsi resmi tersebut dan digabungkan pula menjadi satu buku kerja Excel lengkap tanpa mengubah isi data.

---

## Dataset yang Belum Terunduh & Alasan

### 1. DATASET 1: FOOD INGREDIENTS ROBOFLOW
- **Folder Tujuan:** `01_food_ingredients_roboflow/`
- **URL Sumber:** https://universe.roboflow.com/food-recipe-ingredient-images-0gnku/food-ingredients-dataset
- **Alasan:** Roboflow Universe mewajibkan otentikasi pengguna (*Sign In*) dan/atau `api_key` untuk mengunduh arsip dataset asli berformat YOLOv8. Permintaan langsung tanpa login diblokir dengan respon: `{"error":{"message":"This method requires your API key.","type":"OAuthException"}}`.
- **Status Sesuai Aturan 11:** Berhenti pada langkah ini agar pengguna dapat melakukan login manual.

### 2. DATASET 3: INDONESIAN FOOD (DETEKSI MAKANAN INDONESIA)
- **Folder Tujuan:** `03_indonesian_food/`
- **URL Sumber:** https://universe.roboflow.com/aku-yolo/deteksi-makanan-indonesia-spmyy
- **Alasan:** Sama seperti Dataset 1, Roboflow Universe mewajibkan otentikasi (*Sign In*) untuk ekspor/unduhan dataset format YOLOv8.
- **Status Sesuai Aturan 11:** Berhenti pada langkah ini agar pengguna dapat melakukan login manual.

---

## Langkah Manual yang Perlu Dilakukan Pengguna

Untuk menyelesaikan unduhan kedua dataset Roboflow:

### Untuk Dataset 1 (Food Ingredients):
1. Buka browser dan kunjungi link:
   👉 **[Food Ingredients Roboflow](https://universe.roboflow.com/food-recipe-ingredient-images-0gnku/food-ingredients-dataset)**
2. Klik tombol **Sign In** (di kanan atas) menggunakan akun Google / GitHub / Roboflow Anda.
3. Setelah login, klik tombol **"Download Dataset"**.
4. Pada modal pilihan ekspor:
   - Pilih format: **YOLOv8**
   - Pilih opsi: **"download zip to computer"**
5. Klik **Continue / Download**.
6. Simpan / pindahkan file `.zip` hasil unduhan ke folder proyek:
   📂 `c:\Users\Juned\Documents\Nutisi\NutriVision-Datasets\01_food_ingredients_roboflow\`
7. *(Opsional sesuai instruksi)* Ekstrak isi file `.zip` ke subfolder:
   📂 `c:\Users\Juned\Documents\Nutisi\NutriVision-Datasets\01_food_ingredients_roboflow\extracted\`

---

### Untuk Dataset 3 (Deteksi Makanan Indonesia):
1. Buka browser dan kunjungi link:
   👉 **[Deteksi Makanan Indonesia Roboflow](https://universe.roboflow.com/aku-yolo/deteksi-makanan-indonesia-spmyy)**
2. Pastikan Anda sudah login di Roboflow.
3. Klik tombol **"Download Dataset"**.
4. Pada modal pilihan ekspor:
   - Pilih format: **YOLOv8** (jika tersedia, atau format YOLO yang aktif)
   - Pilih opsi: **"download zip to computer"**
5. Klik **Continue / Download**.
6. Simpan / pindahkan file `.zip` hasil unduhan ke folder proyek:
   📂 `c:\Users\Juned\Documents\Nutisi\NutriVision-Datasets\03_indonesian_food\`
7. *(Opsional sesuai instruksi)* Ekstrak isi file `.zip` ke subfolder:
   📂 `c:\Users\Juned\Documents\Nutisi\NutriVision-Datasets\03_indonesian_food\extracted\`
