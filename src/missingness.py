"""Part 5: evidence about the missingness mechanism (notebook §4.1 pattern)."""
import sys
import pandas as pd


def compare_groups(df: pd.DataFrame, col: str, observed_cols: list[str]) -> pd.DataFrame:
    """Compare rows with and without `col` on observed columns. Return a summary table."""
    raise NotImplementedError


if __name__ == "__main__":
    #df = pd.read_csv(sys.argv[1])
    df = pd.read_csv(sys.argv[1], keep_default_na=False, na_values=[""])
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    print(missing)
    print((missing / len(df) * 100).round(1))
    #raise NotImplementedError
