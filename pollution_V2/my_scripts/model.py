import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.losses import MeanSquaredError  # Needed for compilation clarity

# 1. PARAMETERS
SEQ_LENGTH = 7  # Past 7 days to predict next day
FUTURE_DAYS = 7  # Predict the next 30 days
DATA_PATH = "../data/aligned_sensors_pm25_filled_knn.csv"
FORECAST_OUTPUT_PATH = "../data/future_pm25_forecast.csv"

# 2. Load and Prepare Data
df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
df = df.round(1)

# Initialize scalers and scale data
scalers = {}
scaled_data = pd.DataFrame(index=df.index)

for col in df.columns:
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data[col] = scaler.fit_transform(df[[col]])
    scalers[col] = scaler


# 3. Prepare sequences for LSTM
def create_sequences(data, seq_length=7):
    """Creates sequences (X) and next-day target (y)."""
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data.iloc[i:i + seq_length].values)
        y.append(data.iloc[i + seq_length].values)
    return np.array(X), np.array(y)


X, y = create_sequences(scaled_data, seq_length=SEQ_LENGTH)

# 4. Use ALL data for Training
X_train, y_train = X, y
num_sensors = df.shape[1]

# 5. Build and Train LSTM model
print("Building and training new model...")

# Model Definition
model = Sequential()
model.add(LSTM(64, input_shape=(SEQ_LENGTH, num_sensors), return_sequences=False))
model.add(Dense(num_sensors))
model.compile(optimizer='adam', loss=MeanSquaredError())  # Use the explicit loss function class

# Training
history = model.fit(
    X_train,
    y_train,
    epochs=50,
    batch_size=16,
    verbose=0  
)

print("Model training complete (50 epochs).")

# 6. Generate Future Predictions
# Use the last SEQ_LENGTH days of the FULL original dataset as the starting point.
last_sequence = scaled_data.iloc[-SEQ_LENGTH:].values
future_predictions = []

for _ in range(FUTURE_DAYS):
    # Predict the next day (unrolled prediction)
    pred = model.predict(last_sequence[np.newaxis, :, :], verbose=0)[0]
    future_predictions.append(pred)

    # Slide the window forward: remove the oldest day, add the new prediction
    last_sequence = np.vstack([last_sequence[1:], pred])

# 7. Inverse Transform and Create Future DataFrame
future_predictions = np.array(future_predictions)
future_predictions_inv = np.zeros_like(future_predictions)

# Inverse transform predictions for each sensor using its respective scaler
for i, col in enumerate(df.columns):
    # Retrieve the scaler used for this column
    scaler = scalers[col]

    # Reshape the column's predictions and inverse transform
    future_predictions_inv[:, i] = scaler.inverse_transform(
        future_predictions[:, i].reshape(-1, 1)
    ).flatten()

future_predictions_inv = future_predictions_inv.round(1)

# 8. Create Future Dates and Save Forecast CSV
last_date = df.index[-1]
# Start dates 1 day after the last date in the historical data
future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=FUTURE_DAYS, freq='D')

future_df = pd.DataFrame(future_predictions_inv, columns=df.columns, index=future_dates)

future_df.to_csv("../data/new_forecast.csv")

print(f" Generated future PM2.5 data for {FUTURE_DAYS} days and saved to CSV.")
print("\nFuture DataFrame Head:")
print(future_df.head())
