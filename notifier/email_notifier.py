import smtplib
from email.mime.text import MIMEText
from config import settings

def send_email(subject, message):
    print("Sending email...")

    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = settings.email_sender
        msg["To"] = settings.email_receiver

        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        server.starttls()
        server.login(settings.email_sender, settings.email_password)
        server.send_message(msg)
        server.quit()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


       