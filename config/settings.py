import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", "")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Smart Port Scanner")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True") == 'True'
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False") == 'True'
USE_CREDENTIALS = os.getenv("USE_CREDENTIALS", "True") == 'True'
VALIDATE_CERTS = os.getenv("VALIDATE_CERTS", "True") == 'True'
common_ports = list(range(1, 65536))
target_ip = os.getenv("target_ip", "127.0.0.1")
vulners_api_key = os.getenv("vulners_api_key", "")

