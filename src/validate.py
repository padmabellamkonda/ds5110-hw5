"""Part 2: validation as code. Raise once, listing every failure (notebook §1)."""
import sys
import numpy as np
import pandas as pd


class ValidationError(Exception):
    pass


# Exact column set from the raw file header (82 columns), split by dtype family.
# PID and MS SubClass are codes, but they are stored as numbers in the file.
EXPECTED_NUMERIC = [
    "Order", "PID", "MS SubClass", "Lot Frontage", "Lot Area", "Overall Qual", "Overall Cond",
    "Year Built", "Year Remod/Add", "Mas Vnr Area", "BsmtFin SF 1", "BsmtFin SF 2",
    "Bsmt Unf SF", "Total Bsmt SF", "1st Flr SF", "2nd Flr SF", "Low Qual Fin SF",
    "Gr Liv Area", "Bsmt Full Bath", "Bsmt Half Bath", "Full Bath", "Half Bath",
    "Bedroom AbvGr", "Kitchen AbvGr", "TotRms AbvGrd", "Fireplaces", "Garage Yr Blt",
    "Garage Cars", "Garage Area", "Wood Deck SF", "Open Porch SF", "Enclosed Porch",
    "3Ssn Porch", "Screen Porch", "Pool Area", "Misc Val", "Mo Sold", "Yr Sold", "SalePrice",
]
EXPECTED_TEXT = [
    "MS Zoning", "Street", "Alley", "Lot Shape", "Land Contour", "Utilities", "Lot Config",
    "Land Slope", "Neighborhood", "Condition 1", "Condition 2", "Bldg Type", "House Style",
    "Roof Style", "Roof Matl", "Exterior 1st", "Exterior 2nd", "Mas Vnr Type", "Exter Qual",
    "Exter Cond", "Foundation", "Bsmt Qual", "Bsmt Cond", "Bsmt Exposure", "BsmtFin Type 1",
    "BsmtFin Type 2", "Heating", "Heating QC", "Central Air", "Electrical", "Kitchen Qual",
    "Functional", "Fireplace Qu", "Garage Type", "Garage Finish", "Garage Qual", "Garage Cond",
    "Paved Drive", "Pool QC", "Fence", "Misc Feature", "Sale Type", "Sale Condition",
]

# Each rule needs a source. Put it in the comment.
RANGES = {
    "Yr Sold": (2006, 2010),            # source: study period (2006 to 2010, HW5 PDF)
    "Mo Sold": (1, 12),                 # source: data dictionary, Mo Sold (1-12)
    "Overall Qual": (1, 10),            # source: data dictionary, 1 to 10 scale
    "Overall Cond": (1, 10),            # source: data dictionary, 1 to 10 scale
    "Year Built": (1850, 2010),         # source: study period (no sale after 2010); lower end is my assumption
    "Year Remod/Add": (1850, 2010),     # source: study period; same lower-end assumption
    "Garage Yr Blt": (1850, 2010),      # source: study period; same lower-end assumption
    "Lot Area": (1, None),              # source: physical limit, area must be positive (no upper limit)
    "Gr Liv Area": (1, None),           # source: physical limit, area must be positive (no upper limit)
    "SalePrice": (1, None),             # source: physical limit, a price must be positive (no upper limit)
}
ALLOWED = {
    "Street": {"Grvl", "Pave"},                               # source: data dictionary, Street
    "Central Air": {"N", "Y"},                                # source: data dictionary, Central Air
    "Land Slope": {"Gtl", "Mod", "Sev"},                      # source: data dictionary, Land Slope
    "Lot Shape": {"Reg", "IR1", "IR2", "IR3"},                # source: data dictionary, Lot Shape
    "Paved Drive": {"Y", "P", "N"},                           # source: data dictionary, Paved Drive
    "MS Zoning": {"A", "C", "FV", "I", "RH", "RL", "RP", "RM"},   # source: data dictionary, MS Zoning
    "Bldg Type": {"1Fam", "2FmCon", "Duplx", "TwnhsE", "TwnhsI"}, # source: data dictionary, Bldg Type
    "Neighborhood": {                                         # source: data dictionary, Neighborhood
        "Blmngtn", "Blueste", "BrDale", "BrkSide", "ClearCr", "CollgCr", "Crawfor",
        "Edwards", "Gilbert", "Greens", "GrnHill", "IDOTRR", "Landmrk", "MeadowV",
        "Mitchel", "Names", "NoRidge", "NPkVill", "NridgHt", "NWAmes", "OldTown",
        "SWISU", "Sawyer", "SawyerW", "Somerst", "StoneBr", "Timber", "Veenker"},
}


def check_schema(df: pd.DataFrame) -> list[str]:
    """Return a list of schema failures: missing or extra columns, wrong dtype families."""
    errors = []
    expected = EXPECTED_NUMERIC + EXPECTED_TEXT
    missing = [c for c in expected if c not in df.columns]
    extra = [c for c in df.columns if c not in expected]
    if missing:
        errors.append(f"missing columns: {missing}")
    if extra:
        errors.append(f"extra columns: {extra}")
    for col in EXPECTED_NUMERIC:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"{col}: expected numeric, got {df[col].dtype}")
    for col in EXPECTED_TEXT:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"{col}: expected text, got {df[col].dtype}")
    return errors


def check_ranges(df: pd.DataFrame) -> list[str]:
    """Return one message per column with values outside its range. NaN is not judged here."""
    errors = []
    for col, (lo, hi) in RANGES.items():
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue                                  # a wrong dtype is reported by check_schema
        x = df[col]
        present = x.notna()
        if hi is None:                                # no upper limit
            outside = x < lo
        else:
            outside = ~x.between(lo, hi)
        bad = present & outside
        if bad.any():
            if hi is None:
                errors.append(f"{col}: {bad.sum()} values below {lo}")
            else:
                errors.append(f"{col}: {bad.sum()} values outside [{lo}, {hi}]")
    return errors


def check_allowed(df: pd.DataFrame) -> list[str]:
    """Return one message per categorical column with values not in the dictionary."""
    errors = []
    for col, allowed in ALLOWED.items():
        if col not in df.columns:
            continue
        present = df[col].notna()
        bad = present & ~df[col].isin(allowed)
        if bad.any():
            codes = sorted(set(df.loc[bad, col]))
            errors.append(f"{col}: {bad.sum()} values not in dictionary, codes {codes}")
    return errors


def check_cross_column(df: pd.DataFrame) -> list[str]:
    """Return failures of rules that involve two or more columns."""
    errors = []
    needed = ["Year Remod/Add", "Year Built", "Yr Sold", "Garage Yr Blt"]
    if not all(pd.api.types.is_numeric_dtype(df[c]) for c in needed):
        return errors                                 # a wrong dtype is reported by check_schema
    n = lambda c: df[c]
    # rule 1: remodel year is not before year built (data dictionary: equals Year Built if no remodel)
    bad = n("Year Remod/Add") < n("Year Built")
    if bad.any():
        errors.append(f"Year Remod/Add before Year Built: {bad.sum()} rows")
    # Sale Condition "Partial" = home not complete at last assessment (data dictionary),
    # so a Partial sale can come before the build year. Rules 2 and 3 skip those rows.
    full = df["Sale Condition"] != "Partial"
    # rule 2: a finished house cannot be built after the year it sold
    bad = full & (n("Year Built") > n("Yr Sold"))
    if bad.any():
        errors.append(f"Year Built after Yr Sold: {bad.sum()} rows")
    # rule 3: a garage cannot be built after the year of sale (Partial sales skipped)
    bad = full & (n("Garage Yr Blt") > n("Yr Sold"))
    if bad.any():
        errors.append(f"Garage Yr Blt after Yr Sold: {bad.sum()} rows")
    return errors


def validate(df: pd.DataFrame) -> pd.DataFrame:
    errors = check_schema(df) + check_ranges(df) + check_allowed(df) + check_cross_column(df)
    if errors:
        raise ValidationError("\n".join(errors))
    return df


if __name__ == "__main__":
    path = sys.argv[1]
    raw = "--raw" in sys.argv
    df = pd.read_csv(path, sep="\t" if raw else ",", keep_default_na=False, na_values=[""])
    try:
        validate(df)
        print(f"PASS {path}")
    except ValidationError as e:
        print(f"FAIL {path}\n{e}")
        sys.exit(1)
