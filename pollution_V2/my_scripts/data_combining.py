import os
import pandas as pd

# Folder containing daily sensor CSVs
data_folder = "../data/daily_data"

# Minimum number of days required per sensor
min_days = 120

# Step 1: Read all CSVs and store PM2.5 sensors only
sensor_dfs = {}
for file in os.listdir(data_folder):
    if file.endswith(".csv") and file.startswith("sensor_"):
        sensor_id = int(file.split("_")[1].split(".")[0])
        df = pd.read_csv(os.path.join(data_folder, file))

        # ---- FILTER: KEEP ONLY PM2.5 ----
        if "parameter" not in df.columns:
            continue  # skip weird files

        if df["parameter"].iloc[0].lower() != "pm25":
            continue  # skip UM003, PM10, etc.

        df["datetime_from_local"] = pd.to_datetime(df["datetime_from_local"])
        df["datetime_to_local"] = pd.to_datetime(df["datetime_to_local"])
        df["sensor_id"] = sensor_id
        sensor_dfs[sensor_id] = df

print(f"PM2.5 sensors found: {len(sensor_dfs)}")

# Step 2: Compute per-sensor coverage
coverage_stats = {}
for sensor_id, df in sensor_dfs.items():
    days = (df["datetime_to_local"].max() - df["datetime_from_local"].min()).days
    coverage_stats[sensor_id] = days

coverage_df = pd.DataFrame.from_dict(coverage_stats, orient='index', columns=['coverage_days'])
print("Per-sensor coverage statistics:")
print(coverage_df.describe())

# Step 3: Keep sensors with enough data
valid_sensors = coverage_df[coverage_df['coverage_days'] >= min_days].index.tolist()
print(f"Sensors with at least {min_days} days of PM2.5 data: {len(valid_sensors)}")

# Step 4: Build wide-format DataFrame
all_data = []
for sensor_id in valid_sensors:
    df = sensor_dfs[sensor_id][["datetime_from_local", "value"]].copy()
    df.rename(columns={"value": f"sensor_{sensor_id}"}, inplace=True)
    all_data.append(df.set_index("datetime_from_local"))

from functools import reduce
wide_df = reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how='outer'), all_data)

# Sort by date
wide_df.sort_index(inplace=True)

print("Wide-format DataFrame ready for modeling:")
print(wide_df.head())

wide_df.to_csv("../data/aligned_sensors_data_pm25_only.csv")
