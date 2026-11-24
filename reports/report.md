# HW5 report

## 1 Provenance
## 2 Validation: failures on the raw file
| Check | Column | Failures | What I did |
|---|---|---|---|
| Value outside range | Garage Yr Blt | 1 | Set the value to missing. It was outside 1850 to 2010. |
| Code not in dictionary | MS Zoning | 29 | Changed to the dictionary codes (A, C, I). |
| Code not in dictionary | Bldg Type | 272 | Changed to the dictionary codes (2FmCon, Duplx, TwnhsI). TwnhsI is my inference. |
| Code not in dictionary | Neighborhood | 443 | Changed NAmes to Names. |
| Cross-column | Year Remod/Add before Year Built | 1 | Set the remodel year to missing. The true value is unknown. |
## 3 Sentinels and structural absence
| Column | Rows with "NA" |
|---|---|
| Alley | 2732 |
| Bsmt Qual | 79 |
| Bsmt Cond | 79 |
| Bsmt Exposure | 79 |
| BsmtFin Type 1 | 79 |
| BsmtFin Type 2 | 79 |
| Fireplace Qu | 1422 |
| Garage Type | 157 |
| Garage Finish | 157 |
| Garage Qual | 158 |
| Garage Cond | 158 |
| Pool QC | 2917 |
| Fence | 2358 |
| Misc Feature | 2824 |

| Column | Zeros | Sentinel |
|---|---|---|
| Garage Area | 157 | No. True zero. |
| Pool Area | 2917 | No. True zero. |
| Fireplaces | 1422 | No. True zero. |
| Total Bsmt SF | 79 | No. True zero. |
| Misc Val | 2827 | No. True zero. |

I treat "NA" as none only where a numeric column says the feature is absent (for example Garage Area is 0). Everywhere else I treat it as unknown and set it to missing.

## 4 Keys and duplicates

I tested two candidate keys. `Order` is unique in all 2930 rows. `PID` is also unique in all 2930 rows.

`Order` is the row number in the file. It identifies one row. `PID` is the parcel ID. It identifies one property. I chose `Order` as the key for one sale.

| Check | Count |
|---|---|
| Exact copies | 0 |
| Same key (`Order`) | 0 |
| Same key (`PID`) | 0 |

I built a lookup table with one row per Neighborhood and its full name from the dictionary. I joined it to the sales with `pd.merge(..., validate="many_to_one")`.

| Step | Rows |
|---|---|
| Sales before the join | 2930 |
| Sales after the join | 2930 |
| Unmatched Neighborhoods | 0 |

The row count did not change. Joins duplicate too. `validate=` raises an error if a key repeats, so the row count cannot change without me knowing.

## 5 Missingness mechanism
Missing: 490 of 2,930 houses (16.7)

| Compare | Value present | Value missing |
| --- | --- | --- |
| Mean Lot Area | 9,710 | 12,331 |
| Mean Year Built | 1,971 | 1,976 |
| Mean Gr Liv Area | 1,489 | 1,553 |
| Mean SalePrice | 180,100 | 184,263 |

Share missing by Lot Config: CulDSac 0.489, Corner 0.204, Inside 0.128.
Share missing by Lot Shape: Reg 0.071, IR1 0.332.

Mechanism: MAR.

Evidence: Clear difference on observed columns → not MCAR. Cul-de-sac lots are missing 49% of the time, inside lots 13%. Regular lots 7%, irregular (IR1) lots 33%. Argue MAR with domain knowledge.

What the data cannot tell me: MAR versus MNAR cannot be tested from the data. The evidence would sit in the values that are missing.

Column picked: Mas Vnr Area

Missing: 23 of 2,930 houses (0.8
)
| Compare | Value present | Value missing |
| --- | --- | --- |
| Mean Lot Area | 10,141 | 10,984 |
| Mean Year Built | 1,971 | 2,003 |
| Mean Gr Liv Area | 1,498 | 1,662 |
| Mean SalePrice | 180,380 | 233,349 |
Share missing by Sale Condition: Partial 0.045, Normal 0.005, Alloca 0.042.

Mechanism: MAR

Evidence: Clear difference on observed columns → not MCAR. Houses missing Mas Vnr Area are much newer (2003 against 1971) and cost more. Partial sales are missing nine times as often as Normal sales. Partial means the home was not complete at last assessment (data dictionary). Argue MAR with domain knowledge.

What the data cannot tell me: Only 23 houses are missing, so the shares are noisy. MAR versus MNAR cannot be tested from the data. The evidence would sit in the values that are missing.


Question: If Lot Frontage were MNAR, the missing value would be the reason it is missing. A cul-de-sac lot has a short, curved edge on the street, so its frontage is hard to measure, and the assessor may leave very small or odd values blank. Then the houses with the strangest frontage would be the ones missing, and the evidence would sit in those missing values, so no observed column could show it.

## 6 Imputation strategy and defense (at most 150 words)
| Strategy | std before | std after | corr with Lot Area before | corr with Lot Area after |
| --- | --- | --- | --- | --- |
| Median (68.0) | 23.4 | 21.3 | 0.49 | 0.36 |
| Iterative (uses other columns) | 23.4 | 22.8 | 0.49 | 0.57 |

![Lot Frontage, median fill](figures/lot_frontage_median.png)

![Lot Frontage, iterative fill](figures/lot_frontage_iterative.png)

The median fill creates a spike at 68, where 490 houses now share one value. The iterative fill spreads the filled values out, so the shape stays closer to the observed data.

I choose the iterative fill. In Part 5, Lot Frontage looked MAR. it is missing more often for cul-de-sac and irregular lots and for larger lots, and all of these are observed. Under MAR, the variables that predict missingness belong in the imputation model. The iterative fill uses Lot Area, living area, year built and quality, so the filled values depend on what predicts the gaps. The median fill ignores them. It gives all 490 houses the value 68, and it shrinks the std from 23.4 to 21.3. The iterative fill keeps the std at 22.8. Its cost is that the correlation with Lot Area rises from 0.49 to 0.57, because fills sit on the line with no noise. It also does not use Lot Config, which is categorical. If the data were MNAR, neither fill would fix it.
## 7 Leakage-safe evaluation
Features: the nine columns listed in the README. Only Lot Frontage has missing values (490).

| Variant | Fill | RMSE |
| --- | --- | --- |
| A | median Lot Frontage within SalePrice quintiles, full table | 0.1620 |
| B | iterative fill on the full table, before CV | 0.1621 |
| C | iterative fill inside a Pipeline | 0.1622 |

(2930, 9) 490
A 0.162
B 0.1621
C 0.1622

**Which gives correct values?** C. An imputer is a fitted model. It learns from training rows only. In C the imputer sits inside the pipeline, so cross-validation refits it per fold and the test fold never informs its own fill. A step that learns from data belongs inside the pipeline.

**Which leaks, and how?**
- A is target leakage: the fill uses the label. The filled value encodes the answer. Here the label is SalePrice.
- B is contamination: the fill uses test rows. The imputer was fitted on the full table before the split.
- A leak shows up as a score that is too good. A has the lowest RMSE, 0.1620.

**Which could not price an unsold house?** A. At prediction time, SalePrice is unknown. The quintile fill cannot exist.

**B versus C:** B is 0.1621 and C is 0.1622, a difference of about 0.0001. Contamination is small with a median and larger with KNN or iterative fills. In this case it is small. Only Lot Frontage has gaps, and the table has 2,930 rows.
## 8 What this data cannot tell you
