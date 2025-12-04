import requests
from bs4 import BeautifulSoup
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

def parse_rates_from_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    results = []

    # Example: find all elements that look like rate entries.
    # You will need to adjust the selectors to match the live page HTML.
    rate_blocks = soup.find_all("div", class_="rate-table-row")  # <-- adjust this

    for block in rate_blocks:
        try:
            product_name = block.find("div", class_="rate-table-product").get_text(strip=True)
            term = block.find("div", class_="rate-table-term").get_text(strip=True)
            apr_str = block.find("div", class_="rate-table-apr").get_text(strip=True)
            apr = float(apr_str.rstrip("%"))
        except Exception:
            continue

        results.append({
            "productName": product_name,
            "term": term,
            "apr": apr,
        })

    return results

def main():
    url = "https://www.redfcu.org/personal/loans/mortgages/refinance/"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Error fetching page:", resp.status_code)
        return

    rates = parse_rates_from_html(resp.text)
    if not rates:
        print("No rates found — check your HTML selectors.")
        return

    # For testing, just print all rates instead of checking threshold
    print("Rates found:")
    for r in rates:
        print(f"{r['productName']} - {r['term']} - APR {r['apr']}%")

if __name__ == "__main__":
    main()
