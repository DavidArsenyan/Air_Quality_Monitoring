import pandas as pd
from sklearn.impute import KNNImputer

# Load the original aligned PM2.5 data
df = pd.read_csv("../data/aligned_sensors_data_pm25_only.csv", index_col=0, parse_dates=True)

print("Original shape:", df.shape)

# KNN Imputation (use 5 nearest sensors)
imputer = KNNImputer(n_neighbors=5, weights="distance")

df_imputed = pd.DataFrame(
    imputer.fit_transform(df),
    index=df.index,
    columns=df.columns
)
df_imputed = df_imputed.round(1)
print("After imputation:", df_imputed.shape)

df_imputed.to_csv("../data/aligned_sensors_pm25_filled_knn.csv")
