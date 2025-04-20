import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Email configuration
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Website URL
URL = "https://www.sodiwseries.com/en-gb/drivers/2017/peter-fabian-50265.html"

# Headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}

def send_email(age):
    subject = "Driver Age Update"
    body = f"The driver's age has changed to {age}!"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def check_driver_age():
    budapest_tz = pytz.timezone("Europe/Budapest")
    now = datetime.now(budapest_tz)
    logging.info(f"Checking age at {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    try:
        # Fetch the webpage with headers
        response = requests.get(URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the age element
        age_strong = soup.select_one("div#tmpl-detail-header-content-information strong:-soup-contains('Age')")
        if age_strong:
            # Get the parent div's text to include "Age : 20 years old"
            parent_div = age_strong.find_parent("div")
            if parent_div:
                div_text = parent_div.get_text(strip=True)
                logging.info(f"Raw div text: {div_text}")
                # Extract age from text like "Age:20yearsold" (after stripping)
                age_match = re.search(r"Age\s*:\s*(\d+)\s*years\s*old", div_text, re.IGNORECASE)
                if age_match:
                    age = int(age_match.group(1))
                    logging.info(f"Age found: {age}")
                    if age == 21:
                        send_email(age)
                        logging.info("Age is 21, email sent")
                        return True
                else:
                    logging.warning("Age number not found in text")
            else:
                logging.warning("Parent div not found")
        else:
            logging.warning("Age strong element not found")
            # Log nearby HTML for debugging
            body = soup.find("body")
            if body:
                logging.debug(f"Body excerpt: {body.prettify()[:500]}")
    except Exception as e:
        logging.error(f"Error checking age: {e}")
    return False

if __name__ == "__main__":
    check_driver_age()
