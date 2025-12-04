import requests
import smtplib
from email.message import EmailMessage
import config

def send_sms(body):
    msg = EmailMessage()
    msg["Subject"] = "Refinance Rate Alert"
    msg["From"] = config.FROM_EMAIL
    msg["To"] = config.TO_SMS
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(config.FROM_EMAIL, config.APP_PASSWORD)
        smtp.send_message(msg)

def main():
    url = "https://www.redfcu.org/wp-content/plugins/rcu-rates/api/v1/rates?product=refinance"
    data = requests.get(url).json()

    matching = [x for x in data if float(x["apr"]) < config.THRESHOLD]

    if matching:
        body_lines = [f"Refinance APR below {config.THRESHOLD}%!"]
        for m in matching:
            body_lines.append(f"{m['productName']} - {m['term']} - APR {m['apr']}%")

        send_sms("\n".join(body_lines))

if __name__ == "__main__":
    main()
