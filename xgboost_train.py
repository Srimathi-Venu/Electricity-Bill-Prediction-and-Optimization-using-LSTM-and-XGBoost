import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
import joblib

# -------------------------------
# 1. Load data
# -------------------------------
df = pd.read_csv("forecast_hourly_data.csv")

df['timestamp'] = pd.to_datetime(df['timestamp'])

# -------------------------------
# 2. Feature engineering
# -------------------------------
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek

# ONLY lag_1 for now
df['lag_1'] = df.groupby('meter_id')['consumption_kwh'].shift(1)

df = df.dropna()  # now rows WILL remain

# -------------------------------
# 3. Features & target
# -------------------------------
X = df[['hour', 'day_of_week', 'lag_1']]
y = df['consumption_kwh']

# -------------------------------
# 4. Train-test split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

# -------------------------------
# 5. Model
# -------------------------------
model = XGBRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    objective='reg:squarederror'
)

model.fit(X_train, y_train)

# -------------------------------
# 6. Evaluation
# -------------------------------
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("✅ XGBoost Training Completed")
print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")

# -------------------------------
# 7. Save model
# -------------------------------
joblib.dump(model, "xgboost_consumption_model.pkl")
print("💾 Model saved")
