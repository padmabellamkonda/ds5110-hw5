"""Part 5: evidence about the missingness mechanism (notebook §4.1 pattern)."""
import sys
import pandas as pd


def compare_groups(df: pd.DataFrame, col: str, observed_cols: list[str]) -> pd.DataFrame:
    """Compare rows with and without `col` on observed columns. Return a summary table."""
    raise NotImplementedError


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])
    raise NotImplementedError
