from port_sc.port_scanner import scan_ports
from vulnerability.vuln_scan import scan_vulnerabilities
from notifier.email_notifier import send_email
from utils.html_report import format_report_table_html
from config import settings
import os
from dotenv import load_dotenv
import tempfile
import webbrowser

load_dotenv()

def full_scan(target_ip):
    print(f"💡 Starting scan for {target_ip}...")

    open_ports = scan_ports(target_ip, settings.common_ports)
    print(f"🔍 Open ports found: {open_ports}")

    if open_ports:
        report = scan_vulnerabilities(target_ip, open_ports)
        print("📋 Vulnerability report generated.")

        # 💖 FORMAT INTO HTML TABLE
        html_report = format_report_table_html(report)

        # ✉️ Send report by email
        subject = f"Scan Report for {target_ip}"
        print("📨 Sending email report...")
        send_email(subject=subject, html_body=html_report)

        # 🖥️ Optional: View it in browser
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            f.write(html_report)
            webbrowser.open(f"file://{f.name}")

    else:
        msg = f"<h2>No open ports found on {target_ip}. All is secure! 🔒</h2>"
        subject = f"Scan Report for {target_ip}"
        send_email(subject=subject, html_body=msg)
        print("✅ No open ports found. Email sent.")


if __name__ == "__main__":
    ip = os.getenv("target_ip") or "192.168.88.146"
    full_scan(ip)
