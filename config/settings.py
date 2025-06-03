import os
from dotenv import load_dotenv
load_dotenv()
#email configuaration
email_sender= os.getenv("email_sender")
email_password = os.getenv("email_password")
email_receiver = os.getenv("email_reciever")
smtp_server = os.getenv("smtp_server")
smtp_port = 587
common_ports = list(range(1, 65536))
#vulnerability api configuration
vulners_api_key = os.getenv("vulners_api_key")