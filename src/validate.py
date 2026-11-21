"""Part 2: validation as code. Raise once, listing every failure (notebook §1)."""
import sys
import pandas as pd


class ValidationError(Exception):
    pass


# Each rule needs a source. Put it in the comment.
RANGES = {
    # "Year Built": (1870, 2010),   # source: ...
}
ALLOWED = {
    # "Street": {"Grvl", "Pave"},   # source: data dictionary, Street (Nominal)
}


def check_schema(df: pd.DataFrame) -> list[str]:
    """Return a list of schema failures: missing or extra columns, wrong dtype families."""
    raise NotImplementedError


def check_ranges(df: pd.DataFrame) -> list[str]:
    """Return one message per column with values outside its range. NaN is not judged here."""
    raise NotImplementedError


def check_allowed(df: pd.DataFrame) -> list[str]:
    """Return one message per categorical column with values not in the dictionary."""
    raise NotImplementedError


def check_cross_column(df: pd.DataFrame) -> list[str]:
    """Return failures of rules that involve two or more columns."""
    raise NotImplementedError


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
