from send_alert_sms import send_sms_alert

def calculate_bill(units):
    bill = 0
    remaining_units = units

    if remaining_units > 0:
        slab = min(remaining_units, 100)
        bill += slab * 1.5
        remaining_units -= slab

    if remaining_units > 0:
        slab = min(remaining_units, 100)
        bill += slab * 3
        remaining_units -= slab

    if remaining_units > 0:
        slab = min(remaining_units, 300)
        bill += slab * 5
        remaining_units -= slab

    if remaining_units > 0:
        bill += remaining_units * 7

    return round(bill, 2)


if __name__ == "__main__":
    predicted_units = 180
    bill_amount = calculate_bill(predicted_units)

    print(f"🔮 Predicted Units : {predicted_units} kWh")
    print(f"💰 Estimated Bill : ₹{bill_amount}")

    # 🔔 ALERT CONDITION
    user_phone = "+91XXXXXXXXXX"   # login page la user kudukra number

    if bill_amount > 500:
        alert_msg = f"""
⚠️ Electricity Bill Alert!
Predicted Units: {predicted_units} kWh
Estimated Bill: ₹{bill_amount}

👉 Please reduce peak-hour usage.
"""
        send_sms_alert(user_phone, alert_msg)
