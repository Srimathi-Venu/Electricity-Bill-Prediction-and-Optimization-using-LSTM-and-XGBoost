import time
import random
from datetime import datetime
import mysql.connector

from bill_prediction import calculate_bill
from recommendation_engine import generate_recommendation
from results_persistence import (
    save_forecast_to_db,
    save_bill_prediction_to_db,
    save_recommendation_to_db,
    save_alert_log_to_db
)

# -------------------------------
# 1. MySQL connection (RAW DATA)
# -------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root@123",
    database="electricity_forecast_db"
)
cursor = conn.cursor()

# -------------------------------
# 2. Simulated meter IDs
# -------------------------------
meter_ids = ["SMT_1001", "SMT_1002", "SMT_1003", "SMT_1004"]

# -------------------------------
# 3. RAW energy usage insert query
# -------------------------------
usage_query = """
INSERT INTO energy_usage
(meter_id, timestamp, consumption_kwh, temperature_c,
 humidity_percent, wind_speed_kmh, avg_past_consumption, peak_flag)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

# -------------------------------
# 4. Data validation
# -------------------------------
def clean_data(consumption, temp, humidity, wind):
    if consumption <= 0:
        return False
    if not (0 <= temp <= 50):
        return False
    if not (0 <= humidity <= 100):
        return False
    if not (0 <= wind <= 25):
        return False
    return True

# -------------------------------
# 5. BUFFER
# -------------------------------
buffer = []

def generate_bulk_data(n=20):
    data = []
    for _ in range(n):
        consumption = round(random.uniform(1.0, 5.5), 2)
        temperature = round(random.uniform(20, 40), 2)
        humidity = round(random.uniform(30, 90), 2)
        wind_speed = round(random.uniform(0, 10), 2)
        avg_past = round(random.uniform(2, 4), 2)
        peak_flag = 1 if consumption > 4 else 0
        meter_id = random.choice(meter_ids)

        if not clean_data(consumption, temperature, humidity, wind_speed):
            continue

        data.append((
            meter_id,
            datetime.now(),
            consumption,
            temperature,
            humidity,
            wind_speed,
            avg_past,
            peak_flag
        ))
    return data

print("🔄 Real-time Energy System started (CTRL+C to stop)")

# -------------------------------
# 6. REAL-TIME LOOP
# -------------------------------
while True:

    # Buffer refill
    if len(buffer) < 5:
        buffer.extend(generate_bulk_data(20))
        print("⚙️ Buffer refilled")

    # Take 2 rows every cycle
    rows_to_insert = buffer[:2]
    buffer = buffer[2:]

    if rows_to_insert:
        cursor.executemany(usage_query, rows_to_insert)
        conn.commit()
        print(f"✅ Raw data inserted | Buffer left: {len(buffer)}")

        # -------------------------------
        # 7. PROCESS EACH ROW
        # -------------------------------
        for row in rows_to_insert:
            meter_id = row[0]
            consumption_kwh = row[2]
            timestamp = row[1]

            # 🔮 FORECAST (simple demo logic)
            predicted_units = round(consumption_kwh * random.uniform(1.1, 1.3), 2)

            save_forecast_to_db(
                meter_id=meter_id,
                forecast_type="hourly",
                forecast_time=timestamp,
                predicted_units=predicted_units
            )

            # 💰 BILL PREDICTION
            bill_amount = calculate_bill(predicted_units)
            save_bill_prediction_to_db(
                meter_id,
                predicted_units,
                bill_amount
            )

            # 💡 RECOMMENDATION
            recommendation_text = generate_recommendation(meter_id)

            save_recommendation_to_db(
                meter_id,
                recommendation_type="usage",
                recommendation_text=recommendation_text
            )

            # 🚨 ALERT LOG
            if bill_amount > 500:
                save_alert_log_to_db(
                    meter_id,
                    alert_type="HIGH_BILL",
                    message=f"Predicted bill ₹{bill_amount} exceeds limit"
                )

    else:
        print("⚠️ No data to insert")

    time.sleep(5)
