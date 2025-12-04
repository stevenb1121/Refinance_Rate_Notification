import asyncio
import re
from playwright.async_api import async_playwright
from email.message import EmailMessage
import smtplib
import config

# -----------------------
# SMS sender
# -----------------------
def send_sms(body):
    msg = EmailMessage()
    msg["From"] = config.FROM_EMAIL
    msg["To"] = config.TO_SMS
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(config.FROM_EMAIL, config.APP_PASSWORD)
        smtp.send_message(msg)

# -----------------------
# Scraper function
# -----------------------
async def scrape_refinance_rates():
    url = "https://www.redfcu.org/personal/loans/mortgages/refinance/"
    rates = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)

        # Get all iframes with class rfcu-iframe__iframe
        iframe_elements = await page.query_selector_all("iframe.rfcu-iframe__iframe")

        if not iframe_elements:
            print("No iframes found")
            await browser.close()
            return []

        # Iterate through each iframe
        for iframe_elem in iframe_elements:
            iframe = await iframe_elem.content_frame()
            if not iframe:
                continue

            # Wait for rate panels inside iframe
            try:
                await iframe.wait_for_selector("div.panel.innerContainer", timeout=5000)
            except:
                continue

            rate_blocks = await iframe.query_selector_all("div.panel.innerContainer")

            # Extract loan type for this iframe
            loan_type_elem = await iframe.query_selector("div.widgetHeaderTitle")
            loan_type = await loan_type_elem.inner_text() if loan_type_elem else "Loan"

            # Extract rates
            for block in rate_blocks:
                try:
                    term_elem = await block.query_selector("div.innerHeadingTitle_small")
                    term = await term_elem.inner_text() if term_elem else "Unknown"

                    rate_elem = await block.query_selector("a.ng-binding")
                    rate_str = await rate_elem.inner_text() if rate_elem else "0"
                    rate = float(rate_str.rstrip("%"))

                    rates.append({
                        "loan_type": loan_type,
                        "term": term,
                        "rate_str": rate_str,
                        "rate": rate
                    })
                except Exception:
                    continue

        await browser.close()
    return rates

# -----------------------
# Main
# -----------------------
async def main():
    rates = await scrape_refinance_rates()
    if not rates:
        print("No rates found")
        return

    # Build table
    body_lines = []
    body_lines.append("Refi Rates:")

    for rate in rates:
        loan_type = rate['loan_type'].replace("- Refi", "").strip()
        term = rate['term']
        # Extract just the number of years from the term
        match = re.search(r'(\d+)', term)
        term_number = match.group(1) if match else term
        
        # Skip exactly 5 year loans
        if term_number == "5":
            continue
        body_lines.append(f"{loan_type} {term}yr {rate['rate_str']}")

    body_text = "\n".join(body_lines)
    print(body_text)  # For testing
    # Uncomment the next line to send SMS after testing
    send_sms(body_text)

# Run the async main
if __name__ == "__main__":
    asyncio.run(main())
