import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt

# -------------------------------
# 1. Load hourly data
# -------------------------------
df = pd.read_csv("forecast_hourly_data.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

# For simplicity – take ONE meter (can extend later)
df = df[df['meter_id'] == 'SMT_1001']
df = df.sort_values('timestamp')

values = df['consumption_kwh'].values.reshape(-1, 1)

# -------------------------------
# 2. Scaling
# -------------------------------
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(values)

# -------------------------------
# 3. Create sequences (24 hours → next hour)
# -------------------------------
X, y = [], []
window_size = 1


for i in range(window_size, len(scaled_data)):
    X.append(scaled_data[i-window_size:i])
    y.append(scaled_data[i])

X = np.array(X)
y = np.array(y)

print("Sequence shape:", X.shape)

# -------------------------------
# 4. Train-test split
# -------------------------------
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# -------------------------------
# 5. LSTM model
# -------------------------------
model = Sequential()
model.add(LSTM(50, activation='tanh', input_shape=(X_train.shape[1], 1)))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mse')

# -------------------------------
# 6. Train model
# -------------------------------
history = model.fit(
    X_train, y_train,
    epochs=10,
    batch_size=32,
    validation_split=0.1,
    verbose=1
)

# -------------------------------
# 7. Plot loss
# -------------------------------
plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='validation')
plt.legend()
plt.title("LSTM Training Loss")
plt.show()

# -------------------------------
# 8. Save model
# -------------------------------
model.save("lstm_consumption_model.h5")
print("💾 LSTM model saved as lstm_consumption_model.h5")
