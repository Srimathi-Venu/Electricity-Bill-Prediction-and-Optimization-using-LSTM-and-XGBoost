import mysql.connector
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from db import get_connection

# ------------------------------------------------
# Generate recommendation for ONE meter
# ------------------------------------------------
def generate_recommendation(meter_id):
    conn = get_connection()

    query = """
    SELECT consumption_kwh, peak_flag
    FROM energy_usage
    WHERE meter_id = %s
      AND timestamp >= NOW() - INTERVAL 7 DAY
    """

    df = pd.read_sql(query, conn, params=(meter_id,))
    conn.close()

    if df.empty:
        return "No sufficient data for recommendation"

    total_units = df['consumption_kwh'].sum()
    peak_units = df[df['peak_flag'] == 1]['consumption_kwh'].sum()

    peak_percent = (peak_units / total_units) * 100 if total_units > 0 else 0

    recommendations = []

    # Peak usage rule
    if peak_percent > 30:
        recommendations.append(
            "Shift AC / heater usage to off-peak hours"
        )

    # Slab warning
    if total_units > 200:
        recommendations.append(
            "Reduce high-load appliance usage to avoid slab crossing"
        )

    # Generic tip
    recommendations.append(
        "Using energy-efficient appliances can reduce bill by 10–20%"
    )

    return " | ".join(recommendations)
