"""Part 6: at least two strategies for Lot Frontage, and their costs (notebook §5 pattern)."""
import sys
import pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import matplotlib.pyplot as plt


def cost_table(before: pd.Series, after: pd.Series, other: pd.Series) -> pd.Series:
    """std before/after, correlation with `other` before/after."""
    return pd.Series({
        "std_before": before.std(), #skips missing ones
        "std_after": after.std(), 
        "corr_before": before.corr(other), # where both row exists (Lot Frontage and Lot Area)
        "corr_after": after.corr(other), 
    })


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1], keep_default_na=False, na_values=[""])
    lot = df["Lot Frontage"]
    median_filled = lot.fillna(lot.median()) # fills missing values with median of observed ones
    print("median fill")
    print(cost_table(lot, median_filled, df["Lot Area"]).round(3))
   
    features = ["Lot Frontage", "Lot Area", "Gr Liv Area", "Year Built", "Overall Qual",
                "Overall Cond", "1st Flr SF", "Full Bath", "Fireplaces"]
    filled = pd.DataFrame(IterativeImputer(random_state=0).fit_transform(df[features]), columns=features)
    iterative_filled = filled["Lot Frontage"]
    print("iterative fill")
    print(cost_table(lot, iterative_filled, df["Lot Area"]).round(3))


    median_filled.plot.hist(bins=40, title="Lot Frontage, median fill")
    plt.savefig("reports/figures/lot_frontage_median.png")
    plt.close()

    iterative_filled.plot.hist(bins=40, title="Lot Frontage, iterative fill")
    plt.savefig("reports/figures/lot_frontage_iterative.png")
    plt.close()