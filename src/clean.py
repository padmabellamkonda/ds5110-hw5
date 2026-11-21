"""Parts 3 and 4: decode true missing values, keep structural "none", check keys."""
import sys
import pandas as pd

# Columns where the dictionary defines "NA" as "none", not "unknown".
NA_MEANS_NONE: list[str] = []


def load_raw(path: str) -> pd.DataFrame:
    """Load with keep_default_na=False so that "NA" and "None" survive as strings."""
    raise NotImplementedError


def decode_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Turn only true missing values into NaN. Return a new DataFrame."""
    raise NotImplementedError


def check_keys(df: pd.DataFrame) -> None:
    """Assert key uniqueness; print exact and key duplicate counts; run the many_to_one join."""
    raise NotImplementedError


if __name__ == "__main__":
    raw_path, out_path = sys.argv[1], sys.argv[2]
    df = decode_missing(load_raw(raw_path))
    check_keys(df)
    df.to_csv(out_path, index=False)
