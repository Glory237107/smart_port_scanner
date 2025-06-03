from port_sc.port_scanner import scan_ports
from vulnerability.vuln_scan import  scan_vulnerabilities
from notifier.email_notifier import send_email
from config import settings

def full_scan(target_ip):
    open_ports = scan_ports(target_ip, settings.common_ports)
    if open_ports:
        report = scan_vulnerabilities(target_ip, open_ports)
        msg = f"SMART SCAN for {target_ip}\n\n"
        for port, details in report.items():
            service = details.get('service', 'Unknown')
            vulnerabilities = details.get('vulnerabilities', [])
            msg += f"Port {port}; Open; {service}\n"
            if vulnerabilities:
                msg += "Vulnerabilities:\n"
                for vuln in vulnerabilities:
                    msg += f"• {vuln}\n"
            msg += "\n"
    else:
        msg = f"No open ports found on {target_ip}. All is secure!"

    subject = f"Scan Report for {target_ip}"
    send_email(subject, msg)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 main.py <target_ip_or_domain>")
        sys.exit(1)

    target_ip = sys.argv[1]
    full_scan(target_ip)
