import os

# Numeric threshold for APR trigger
THRESHOLD = float(os.environ["THRESHOLD"])

# Sender email (Gmail)
FROM_EMAIL = os.environ["FROM_EMAIL"]

# Gmail App Password
APP_PASSWORD = os.environ["APP_PASSWORD"]

# Verizon SMS gateway address (5551234567@vtext.com)
TO_SMS = os.environ["VERIZON_SMS"]
