from twilio.rest import Client

# 🔐 Twilio credentials (replace with your real ones)
ACCOUNT_SID = "AC40d4dc8530f98d7d2a6553abef9cf9f8"
AUTH_TOKEN = "320f3b12bdd7be74d6ef472c9bea41d1"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

TWILIO_NUMBER = "+19143525080"   # trial number
# user number will come dynamically

def send_sms_alert(user_phone, message):
    sms = client.messages.create(
        body=message,
        from_=TWILIO_NUMBER,
        to=user_phone
    )
    print("📨 SMS sent:", sms.sid)
