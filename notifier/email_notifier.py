import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

def send_email(subject, message=None, html_body=None):
    msg = MIMEMultipart("alternative")
    msg['From'] = settings.MAIL_FROM_NAME + f" <{settings.MAIL_FROM}>"
    msg['To'] = settings.MAIL_FROM
    msg['Subject'] = subject

    if message:
        msg.attach(MIMEText(message, 'plain'))

    if html_body:
        msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT, timeout=10)
        if settings.MAIL_STARTTLS:
            server.starttls()
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
        return True
    except (smtplib.SMTPException, OSError) as e:
        print(f" Failed to send email: {e}")
        return False

def send_email_report(subject, html_body):
    return send_email(subject=subject, html_body=html_body)
