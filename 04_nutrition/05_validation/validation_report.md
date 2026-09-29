# NutriVision Nutrition Database - Validation Report

**Generated:** 2026-09-28

---

## Summary

| Metric | Count |
|--------|-------|
| Total Vision Class Entries (all datasets) | 103 |
| Unique Vision Labels | 103 |
| EXACT match | 22 |
| VALID_FORM_MATCH | 6 |
| AMBIGUOUS | 31 |
| NO_VALID_MATCH | 0 |
| **Final Database Records** | **28** |
| Review Needed Records | 75 |

## Errors (0)

No errors found.

## Warnings (0)

No warnings found.

## Acceptance Criteria

- [x] All required columns present
- [x] All numeric columns readable
- [x] No duplicate food_id
- [x] No duplicate canonical food+form
- [x] All final records have source
- [x] All final records have source URL
- [x] All final records have source_record_id
- [x] All final records have basis
- [x] All final EXACT or VALID_FORM_MATCH
- [x] No guessed nutrition values
- [x] No negative values
- [x] NULL preserved (not converted to 0)
- [x] Food-form verified
- [x] Provenance complete
- [x] Validator runs without ERROR

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
