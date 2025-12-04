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
        except Exception as e:
            # skip if any part missing / parse error
            continue

        results.append(src)

    return results

def parse_rates_from_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    results = []
    loan_type = soup.find("div", class_="widgetHeaderTitle")
    rate_blocks = soup.find_all("div", class_="panel innerContainer")

    for block in rate_blocks:
        try:
            term = block.find("div", class_="innerHeadingTitle_small").get_text(strip=True)
            rate_str = block.find("a", class_="ng-binging").get_text(strip=True)
            rate = float(rate_str.rstrip("%"))
        except Exception as e:
            # skip if any part missing / parse error
            continue

        results.append({
            loan_type: loan_type,
            term: term,
            rate_str: rate_str,
            rate: rate})

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
    for src in scrs:
        rates.append(parse_rates_from_html(requests.get(src).text))
    body_lines = []
    # Table header
header = f"{'Loan Type':<20} | {'Term':<10} | {'APR':<6}"
separator = "-" * len(header)
body_lines.append(header)
body_lines.append(separator)

# Table rows
for rate in rates:
    body_lines.append(f"{rate['loan_type']:<20} | {rate['term']:<10} | {rate['rate']:<6.3f}")

send_sms("\n".join(body_lines))

if __name__ == "__main__":
    main()
