from db import get_connection

# ------------------ SAVE FORECAST ------------------
def save_forecast_to_db(meter_id, forecast_type, forecast_time, predicted_units):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO usage_forecast_results
        (meter_id, forecast_type, forecast_timestamp, predicted_units)
        VALUES (%s, %s, %s, %s)
    """, (meter_id, forecast_type, forecast_time, predicted_units))

    conn.commit()
    cursor.close()
    conn.close()


# ------------------ SAVE BILL PREDICTION ------------------
def save_bill_prediction_to_db(meter_id, predicted_units, predicted_bill):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO bill_prediction_results
        (meter_id, predicted_units, predicted_bill)
        VALUES (%s, %s, %s)
    """, (meter_id, predicted_units, predicted_bill))

    conn.commit()
    cursor.close()
    conn.close()


# ------------------ SAVE RECOMMENDATION ------------------
def save_recommendation_to_db(meter_id, recommendation_type, recommendation_text):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO energy_recommendations
        (meter_id, recommendation_type, recommendation_text)
        VALUES (%s, %s, %s)
    """, (meter_id, recommendation_type, recommendation_text))

    conn.commit()
    cursor.close()
    conn.close()


# ------------------ SAVE ALERT LOG ------------------
def save_alert_log_to_db(meter_id, alert_type, message):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alert_logs
        (meter_id, alert_type, message)
        VALUES (%s, %s, %s)
    """, (meter_id, alert_type, message))

    conn.commit()
    cursor.close()
    conn.close()
