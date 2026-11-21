"""Part 7: variants A, B, C with the given model (notebook §6.1 to §6.3)."""
import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_score

NUMERIC_FEATURES: list[str] = []   # 8 to 15 columns, including "Lot Frontage"
CV = KFold(n_splits=5, shuffle=True, random_state=5110)


def rmse(estimator, X: pd.DataFrame, y: pd.Series) -> float:
    return -cross_val_score(estimator, X, y, cv=CV, scoring="neg_root_mean_squared_error").mean()


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])
    y = np.log(df["SalePrice"])
    raise NotImplementedError
