import pandas as pd
import mysql.connector

# -------------------------------
# 1. MySQL connection
# -------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root@123",
    database="electricity_forecast_db"
)

# -------------------------------
# 2. Fetch last 30 days data
# -------------------------------
query = """
SELECT meter_id, timestamp, consumption_kwh
FROM energy_usage
WHERE timestamp >= NOW() - INTERVAL 30 DAY
ORDER BY meter_id, timestamp
"""

df = pd.read_sql(query, conn)

# -------------------------------
# 3. Timestamp conversion
# -------------------------------
df['timestamp'] = pd.to_datetime(df['timestamp'])

# =====================================================
# 4. HOURLY AGGREGATION (BASE DATA)
# =====================================================
df_hourly = (
    df
    .set_index('timestamp')
    .groupby('meter_id')
    .resample('h')['consumption_kwh']
    .sum()
    .reset_index()
)

print("✅ Hourly data ready")
print(df_hourly.head())

# =====================================================
# 5. DAILY AGGREGATION (DERIVED)
# =====================================================
df_daily = (
    df_hourly
    .groupby([
        'meter_id',
        df_hourly['timestamp'].dt.date
    ])['consumption_kwh']
    .sum()
    .reset_index()
    .rename(columns={'timestamp': 'date'})
)

print("✅ Daily data ready")
print(df_daily.head())

# =====================================================
# 6. WEEKLY AGGREGATION (DERIVED)
# =====================================================
df_hourly['week'] = df_hourly['timestamp'].dt.isocalendar().week
df_hourly['year'] = df_hourly['timestamp'].dt.year

df_weekly = (
    df_hourly
    .groupby(['meter_id', 'year', 'week'])['consumption_kwh']
    .sum()
    .reset_index()
)

print("✅ Weekly data ready")
print(df_weekly.head())

# =====================================================
# 7. SAVE FOR ML & ANALYSIS
# =====================================================
df_hourly.to_csv("forecast_hourly_data.csv", index=False)
df_daily.to_csv("forecast_daily_data.csv", index=False)
df_weekly.to_csv("forecast_weekly_data.csv", index=False)

print("📁 Files saved:")
print(" - forecast_hourly_data.csv")
print(" - forecast_daily_data.csv")
print(" - forecast_weekly_data.csv")

# -------------------------------
# 8. Close connection
# -------------------------------
conn.close()
