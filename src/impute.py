"""Part 6: at least two strategies for Lot Frontage, and their costs (notebook §5 pattern)."""
import sys
import pandas as pd


def cost_table(before: pd.Series, after: pd.Series, other: pd.Series) -> pd.Series:
    """std before/after, correlation with `other` before/after."""
    raise NotImplementedError


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])
    raise NotImplementedError
