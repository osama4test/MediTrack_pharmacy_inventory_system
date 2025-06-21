from datetime import datetime

def check_expiry(expiry_date_str):
    try:
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        today = datetime.today().date()
        days_remaining = (expiry_date - today).days

        if days_remaining < 0:
            return "❌ Expired", f"{abs(days_remaining)} days ago"
        elif days_remaining <= 30:
            return "⚠️ Near Expiry", f"{days_remaining} days left"
        else:
            return "✅ Valid", f"{days_remaining} days left"
    except:
        return "⚠️ Invalid Date", "-"
