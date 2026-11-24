"""Part 7: variants A, B, C with the given model (notebook §6.1 to §6.3)."""
import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.pipeline import make_pipeline

NUMERIC_FEATURES: list[str] = ["Lot Frontage", "Lot Area", "Gr Liv Area", "Year Built", "Overall Qual",
                               "Overall Cond", "1st Flr SF", "Full Bath", "Fireplaces"]   # 8 to 15 columns, including "Lot Frontage"
CV = KFold(n_splits=5, shuffle=True, random_state=5110)


def rmse(estimator, X: pd.DataFrame, y: pd.Series) -> float:
    return -cross_val_score(estimator, X, y, cv=CV, scoring="neg_root_mean_squared_error").mean()


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])
    y = np.log(df["SalePrice"])
    X = df[NUMERIC_FEATURES]
    print(X.shape, X.isna().sum().sum())
    #raise NotImplementedError

    edges = np.percentile(df["SalePrice"], [0, 20, 40, 60, 80, 100]) # price cutoffs for quintiles
    edges[0] = edges[0] - 1 # lowers first cutoff by 1. cheapest house ins inside first group, without it would leave first house out
    quintile = pd.cut(df["SalePrice"], edges)
    X_A = X.copy()
    X_A["Lot Frontage"] = df["Lot Frontage"].fillna(df.groupby(quintile)["Lot Frontage"].transform("median"))
    print("A", round(rmse(LinearRegression(), X_A, y), 4))

    # Variant B:
    X_B = pd.DataFrame(IterativeImputer(random_state=0).fit_transform(X), columns=NUMERIC_FEATURES)
    print("B", round(rmse(LinearRegression(), X_B, y), 4))

    # Variant C
    honest = make_pipeline(IterativeImputer(random_state=0), LinearRegression())
    print("C", round(rmse(honest, X, y), 4))
