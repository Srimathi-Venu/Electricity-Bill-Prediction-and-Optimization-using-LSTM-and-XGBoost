from db import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        meter_id VARCHAR(50) UNIQUE,
        phone VARCHAR(15),
        email VARCHAR(100) UNIQUE,
        password VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Energy Usage Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS energy_usage (
        id INT AUTO_INCREMENT PRIMARY KEY,
        meter_id VARCHAR(50),
        timestamp DATETIME,
        consumption_kwh FLOAT,
        temperature_c FLOAT,
        humidity_percent FLOAT,
        wind_speed_kmh FLOAT,
        avg_past_consumption FLOAT,
        anomaly_label VARCHAR(20),
        peak_flag TINYINT(1),
        INDEX (meter_id),
        INDEX (timestamp)
    )
    """)

    # Forecast Results
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usage_forecast_results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        meter_id VARCHAR(50),
        forecast_type VARCHAR(20),
        forecast_timestamp DATETIME,
        predicted_units FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Bill Predictions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bill_prediction_results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        meter_id VARCHAR(50),
        predicted_units FLOAT,
        predicted_bill FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Recommendations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS energy_recommendations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        meter_id VARCHAR(50),
        recommendation_type VARCHAR(50),
        recommendation_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Alert Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alert_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        meter_id VARCHAR(50),
        alert_type VARCHAR(50),
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All tables verified/created successfully!")

if __name__ == "__main__":
    create_tables()
