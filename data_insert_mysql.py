import pandas as pd
from db import get_connection

def insert_data():
    conn = None
    try:
        # 1. Read CSV file
        df = pd.read_csv("smart_meter_data_with_peak_flag.csv")

        # 2. Match column names correctly
        # Original CSV Columns: Timestamp, Electricity_Consumed, Temperature, Humidity, Wind_Speed, Avg_Past_Consumption, Anomaly_Label, Peak_Flag
        column_mapping = {
            'Timestamp': 'timestamp',
            'Electricity_Consumed': 'consumption_kwh',
            'Temperature': 'temperature_c',
            'Humidity': 'humidity_percent',
            'Wind_Speed': 'wind_speed_kmh',
            'Avg_Past_Consumption': 'avg_past_consumption',
            'Anomaly_Label': 'anomaly_label',
            'Peak_Flag': 'peak_flag'
        }
        df.rename(columns=column_mapping, inplace=True)

        # 3. Add default values for missing columns
        if 'meter_id' not in df.columns:
            df['meter_id'] = 1  # Default meter_id
        
        # Ensure timestamp is in correct MySQL format
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # 4. Connect to MySQL (Railway)
        conn = get_connection()
        cursor = conn.cursor()

        # Print database name
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()[0]
        print(f"Connecting to database: {db_name}")

        # 5. Insert query matching user requirements
        query = """
        INSERT INTO energy_usage 
        (meter_id, timestamp, consumption_kwh, temperature_c, humidity_percent, 
         wind_speed_kmh, avg_past_consumption, anomaly_label, peak_flag) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # 6. Iterate and insert all rows
        print("Starting data insertion into Railway database...")
        for _, row in df.iterrows():
            data = (
                row['meter_id'],
                row['timestamp'],
                row['consumption_kwh'],
                row['temperature_c'],
                row['humidity_percent'],
                row['wind_speed_kmh'],
                row['avg_past_consumption'],
                row.get('anomaly_label', 'Normal'),
                row.get('peak_flag', 0)
            )
            cursor.execute(query, data)

        # 7. Commit the transaction
        conn.commit()
        print("✅ Data inserted into MySQL successfully!")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        if conn:
            conn.rollback()

    finally:
        # 8. Close connection
        if conn:
            cursor.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    insert_data()
