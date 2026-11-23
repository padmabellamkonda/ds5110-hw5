"""Parts 3 and 4: decode true missing values, keep structural "none", check keys."""
import sys
import numpy as np
import pandas as pd

# Columns where the dictionary defines "NA" as "none", not "unknown".
NA_MEANS_NONE: list[str] = [
    "Alley", "Bsmt Qual", "Bsmt Cond", "Bsmt Exposure", "BsmtFin Type 1", "BsmtFin Type 2",
    "Fireplace Qu", "Garage Type", "Garage Finish", "Garage Qual", "Garage Cond",
    "Pool QC", "Fence", "Misc Feature",
]  # spelling checked against the raw file header

# For each "none" column, a numeric column that says whether the feature exists.
# "NA" is "none" only where the indicator is 0. Alley and Fence have no indicator.
INDICATOR = {
    "Bsmt Qual": "Total Bsmt SF", "Bsmt Cond": "Total Bsmt SF", "Bsmt Exposure": "Total Bsmt SF",
    "BsmtFin Type 1": "Total Bsmt SF", "BsmtFin Type 2": "Total Bsmt SF",
    "Fireplace Qu": "Fireplaces",
    "Garage Type": "Garage Area", "Garage Finish": "Garage Area",
    "Garage Qual": "Garage Area", "Garage Cond": "Garage Area",
    "Pool QC": "Pool Area", "Misc Feature": "Misc Val",
}

# Numeric columns. A true missing "NA" in any of them makes pandas read the column as text.
NUMERIC_COLS = [
    "Order", "PID", "MS SubClass", "Lot Frontage", "Lot Area", "Overall Qual", "Overall Cond",
    "Year Built", "Year Remod/Add", "Mas Vnr Area", "BsmtFin SF 1", "BsmtFin SF 2",
    "Bsmt Unf SF", "Total Bsmt SF", "1st Flr SF", "2nd Flr SF", "Low Qual Fin SF",
    "Gr Liv Area", "Bsmt Full Bath", "Bsmt Half Bath", "Full Bath", "Half Bath",
    "Bedroom AbvGr", "Kitchen AbvGr", "TotRms AbvGrd", "Fireplaces", "Garage Yr Blt",
    "Garage Cars", "Garage Area", "Wood Deck SF", "Open Porch SF", "Enclosed Porch",
    "3Ssn Porch", "Screen Porch", "Pool Area", "Misc Val", "Mo Sold", "Yr Sold", "SalePrice",
]

# Category codes in the data that differ from the dictionary.
# Fill only after `make validate` lists them. Each fix is printed, never silent.
CODE_FIXES: dict[str, dict[str, str]] = {
    "MS Zoning": {"A (agr)": "A", "C (all)": "C", "I (all)": "I"},   # dictionary: A, C, I
    "Bldg Type": {"2fmCon": "2FmCon", "Duplex": "Duplx", "Twnhs": "TwnhsI"},   # dictionary spellings; "Twnhs" -> inside unit by elimination, TwnhsE is separate
    "Neighborhood": {"NAmes": "Names"},   # dictionary spells North Ames "Names"
}

# Values outside a range that are impossible, set to NaN and printed. Fill after validate lists them.
SET_NAN_OUTSIDE: dict[str, tuple[float, float]] = {
    "Garage Yr Blt": (1850, 2010),   # 2207 is a future year; the true value is unknown
}

NEIGHBORHOODS = {   # source: data dictionary, Neighborhood
    "Blmngtn": "Bloomington Heights", "Blueste": "Bluestem", "BrDale": "Briardale",
    "BrkSide": "Brookside", "ClearCr": "Clear Creek", "CollgCr": "College Creek",
    "Crawfor": "Crawford", "Edwards": "Edwards", "Gilbert": "Gilbert", "Greens": "Greens",
    "GrnHill": "Green Hills", "IDOTRR": "Iowa DOT and Rail Road", "Landmrk": "Landmark",
    "MeadowV": "Meadow Village", "Mitchel": "Mitchell", "Names": "North Ames",
    "NoRidge": "Northridge", "NPkVill": "Northpark Villa", "NridgHt": "Northridge Heights",
    "NWAmes": "Northwest Ames", "OldTown": "Old Town",
    "SWISU": "South and West of Iowa State University", "Sawyer": "Sawyer",
    "SawyerW": "Sawyer West", "Somerst": "Somerset", "StoneBr": "Stone Brook",
    "Timber": "Timberland", "Veenker": "Veenker",
}


def load_raw(path: str) -> pd.DataFrame:
    """Load with keep_default_na=False so that "NA" and "None" survive as strings."""
    return pd.read_csv(path, sep="\t", keep_default_na=False, na_values=[""])


def decode_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Turn only true missing values into NaN. Return a new DataFrame."""
    df = df.copy()
    # "NA" means "none" only where the indicator column says the feature is absent (== 0).
    # Everywhere else an "NA" in these columns contradicts the dictionary: it is unknown, so NaN.
    for col in NA_MEANS_NONE:
        na = df[col] == "NA"
        if col in INDICATOR:
            none = na & (df[INDICATOR[col]] == 0)
        else:
            none = na   # Alley, Fence: no indicator column
        unknown = na & ~none
        df.loc[none, col] = "None"
        df.loc[unknown, col] = np.nan
        if unknown.any():
            print(f"{col}: {unknown.sum()} 'NA' values contradict the dictionary, set to NaN")
    # In this file every other missing value is already an empty cell, read as NaN by load_raw.
    for col in NUMERIC_COLS:
        assert pd.api.types.is_numeric_dtype(df[col]), f"{col} is not numeric"
    # Documented fixes, each one reported.
    for col, mapping in CODE_FIXES.items():
        n = df[col].isin(mapping.keys()).sum()
        print(f"CODE_FIXES {col}: {n} values recoded {mapping}")
        df[col] = df[col].replace(mapping)
    for col, (lo, hi) in SET_NAN_OUTSIDE.items():
        bad = df[col].notna() & ~df[col].between(lo, hi)
        print(f"SET_NAN_OUTSIDE {col}: {bad.sum()} values outside [{lo}, {hi}] set to NaN")
        df.loc[bad, col] = np.nan
    # Remodel year before build year is impossible (dictionary: remodel year equals build year if none).
    bad = df["Year Remod/Add"] < df["Year Built"]
    print(f"Year Remod/Add before Year Built: {bad.sum()} values set to NaN")
    df.loc[bad, "Year Remod/Add"] = np.nan
    return df


def check_keys(df: pd.DataFrame) -> None:
    """Assert key uniqueness; print exact and key duplicate counts; run the many_to_one join."""
    print("exact duplicate rows:", df.duplicated().sum())
    print("key duplicates, Order:", df.duplicated(subset="Order").sum())
    print("key duplicates, PID:  ", df.duplicated(subset="PID").sum())
    assert df.duplicated(subset="Order").sum() == 0, "Order is not a key"
    lookup = pd.DataFrame(list(NEIGHBORHOODS.items()), columns=["Neighborhood", "Neighborhood Name"])
    merged = pd.merge(df, lookup, on="Neighborhood", how="left", validate="many_to_one")
    print("rows before join:", len(df), " after join:", len(merged))
    assert len(merged) == len(df), "join changed the row count"
    print("rows with no full name:", merged["Neighborhood Name"].isna().sum())


if __name__ == "__main__":
    raw_path, out_path = sys.argv[1], sys.argv[2]
    df = decode_missing(load_raw(raw_path))
    check_keys(df)
    df.to_csv(out_path, index=False)
