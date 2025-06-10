import os
from dotenv import load_dotenv

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")
MAIL_PORT = int(os.getenv("MAIL_PORT"))
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS") == 'True'
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS") == 'True'
USE_CREDENTIALS = os.getenv("USE_CREDENTIALS") == 'True'
VALIDATE_CERTS = os.getenv("VALIDATE_CERTS") == 'True'
common_ports = list(range(1, 65536))
target_ip = os.getenv("target_ip")
#vulnerability api configuration
vulners_api_key = os.getenv("vulners_api_key")




