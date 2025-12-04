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

def parse_sources_from_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    results = []

    iframe_blocks = soup.find_all("iframe", class_="rfcu-iframe__iframe")
    for block in iframe_blocks:
        try:
            src = block["src"]
            results.append(src)
        except Exception:
            continue

    return results

def parse_rates_from_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    results = []

    loan_type_elem = soup.find("div", class_="widgetHeaderTitle")
    loan_type = loan_type_elem.get_text(strip=True) if loan_type_elem else "Loan"

    rate_blocks = soup.find_all("div", class_="panel innerContainer")
    for block in rate_blocks:
        try:
            term = block.find("div", class_="innerHeadingTitle_small").get_text(strip=True)
            rate_str = block.find("a", class_="ng-binding").get_text(strip=True)
            rate = float(rate_str.rstrip("%"))
            results.append({
                "loan_type": loan_type,
                "term": term,
                "rate_str": rate_str,
                "rate": rate
            })
        except Exception:
            continue

    return results

def main():
    url = "https://www.redfcu.org/personal/loans/mortgages/refinance/"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Error fetching page:", resp.status_code)
        return

    srcs = parse_sources_from_html(resp.text)
    if not srcs:
        print("No sources found — check your HTML selectors.")
        return

    rates = []
    for src in srcs:
        iframe_resp = requests.get(src)
        if iframe_resp.status_code == 200:
            rates.extend(parse_rates_from_html(iframe_resp.text))

    if not rates:
        print("No rates found in iframe content.")
        return

    # Build table
    body_lines = []
    header = f"{'Loan Type':<20} | {'Term':<15} | {'APR':<6}"
    separator = "-" * len(header)
    body_lines.append(header)
    body_lines.append(separator)

    for rate in rates:
        body_lines.append(f"{rate['loan_type']:<20} | {rate['term']:<15} | {rate['rate']:<6.3f}")

    body_text = "\n".join(body_lines)
    print(body_text)  # For testing
    # Uncomment to send SMS after testing
    # send_sms(body_text)

if __name__ == "__main__":
    main()
