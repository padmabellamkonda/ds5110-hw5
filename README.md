# HW5: Ames Housing quality audit

## How to run

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make all
```

## Provenance (Part 1)

| Item | Value |
| --- | --- |
| Source URL | https://jse.amstat.org/v19n3/decock/AmesHousing.txt |
| Downloaded on | 2026-11-21 |
| Citation | De Cock, D. (2011). Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project. Journal of Statistics Education, 19(3). |
| Data dictionary | https://jse.amstat.org/v19n3/decock/DataDocumentation.txt |
| Terms of use |Free to be used in teaching if cited (https://jse.amstat.org/jse_users.htm) |
| Rows, columns on arrival | 2,930 rows, 82 columns |


## Features used in Part 7

Nine numeric columns:
- Lot Frontage: the column with missing values that Part 6 fills.
- Lot Area, Gr Liv Area, 1st Flr SF: size of the lot and the house.
- Year Built, Overall Qual, Overall Cond: age and condition.
- Full Bath, Fireplaces: amenities.

I chose columns that affect price. Only Lot Frontage has missing values (490). I also wanted it to be consistent with what I used in Part 6.


## AI assistance

Tool, what it was used for, which files.
