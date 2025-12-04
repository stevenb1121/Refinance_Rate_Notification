import smtplib
import os

# Read from environment variables (all caps)
FROM_EMAIL = os.environ["FROM_EMAIL"]
APP_PASSWORD = os.environ["APP_PASSWORD"]

def test_login():
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(FROM_EMAIL, APP_PASSWORD)
        print("✅ Gmail login successful!")
    except smtplib.SMTPAuthenticationError as e:
        print("❌ SMTP Authentication Error:", e)
    except Exception as e:
        print("❌ Other error:", e)

if __name__ == "__main__":
    test_login()
