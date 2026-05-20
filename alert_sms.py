from twilio.rest import Client
import mysql.connector

# -------------------------------
# 1. Twilio credentials
# -------------------------------
ACCOUNT_SID = "AC40d4dc8530f98d7d2a6553abef9cf9f8"
AUTH_TOKEN = "320f3b12bdd7be74d6ef472c9bea41d1"
MESSAGING_SERVICE_SID = "MGdbe622788a198a9d9926385bb439daaa"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# -------------------------------
# 2. Fetch phone number from DB
# -------------------------------
def get_user_phone(user_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@123",
        database="electricity_forecast_db"
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT phone FROM users WHERE user_id = %s", (user_id,)
    )
    phone = cursor.fetchone()[0]
    conn.close()
    return phone

# -------------------------------
# 3. Send SMS function
# -------------------------------
def send_sms_alert(to_number, message):
    msg = client.messages.create(
        messaging_service_sid=MESSAGING_SERVICE_SID,
        body=message,
        to=to_number
    )
    print("✅ SMS sent. SID:", msg.sid)

# -------------------------------
# 4. MAIN LOGIC
# -------------------------------
if __name__ == "__main__":
    predicted_units = 180
    bill_amount = 540
    user_id = 1

    if bill_amount > 500:
        phone = get_user_phone(user_id)

        alert_message = f"""
⚠️ Electricity Bill Alert
🔋 Predicted Units: {predicted_units} kWh
💰 Estimated Bill: ₹{bill_amount}
👉 Reduce peak hour usage
"""

        send_sms_alert(phone, alert_message)
