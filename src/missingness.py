"""Part 5: evidence about the missingness mechanism (notebook §4.1 pattern)."""
import sys
import pandas as pd


def compare_groups(df: pd.DataFrame, col: str, observed_cols: list[str]) -> pd.DataFrame:
    """Compare rows with and without `col` on observed columns. Return a summary table."""
    #raise NotImplementedError


if __name__ == "__main__":
    #df = pd.read_csv(sys.argv[1])
    df = pd.read_csv(sys.argv[1], keep_default_na=False, na_values=[""])
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    print(missing)
    print((missing / len(df) * 100).round(1))
    #raise NotImplementedError
    # Lot Frontage: compare houses with and without a value
    cols = ["Lot Area", "Year Built", "SalePrice", "Gr Liv Area"]
    df["lot_missing"] = df["Lot Frontage"].isna()
    print(df.groupby(df["Lot Frontage"].isna())[cols].mean().round(0))
    print(df.groupby(df["Lot Config"])["lot_missing"].mean().round(3))
    print(df.groupby(df["Lot Shape"])["lot_missing"].mean().round(3))

    # Mas Vnr Area: compare houses with and without a value
    df["mas_missing"] = df["Mas Vnr Area"].isna()
    print(df.groupby(df["Mas Vnr Area"].isna())[cols].mean().round(0))
    print(df.groupby(df["Sale Condition"])["mas_missing"].mean().round(3))