# NutriVision - Source Index (Provenance)

**Generated:** 2026-09-28

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
| Retrieval Attempt | 2026-09-28 |
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
