from port_sc.port_scanner import scan_ports
from vulnerability.vuln_scan import scan_vulnerabilities
from notifier.email_notifier import send_email
from utils.html_report import format_report_table_html
from threat_handler.threat_manager import ThreatManager
from config import settings
import os
import sys
from dotenv import load_dotenv
import tempfile
import webbrowser

# Load environment variables
load_dotenv()

def full_scan(target_ip):
    print(f"🔍 Starting comprehensive scan for {target_ip}...")
    print("=" * 60)

    # Initialize Threat Manager
    threat_manager = ThreatManager()
    print("🛡️ Threat detection system initialized")
    print("⚙️ Automatic blocking enabled for high-risk threats")
    print("-" * 60)

    # Phase 1: Port Scanning
    print("📡 PHASE 1: Port Scanning & Threat Detection")
    open_ports = scan_ports(target_ip, settings.common_ports, threat_manager)
    print(f"✅ Scan complete: {len(open_ports)} open ports found")

    if open_ports:
        # Phase 2: Vulnerability Scanning
        print("-" * 60)
        print("🧪 PHASE 2: Vulnerability Analysis & Threat Assessment")
        report = scan_vulnerabilities(target_ip, open_ports, threat_manager)
        print("✅ Vulnerability analysis complete")

        # Display Threat Summary
        print("-" * 60)
        print("📊 THREAT SUMMARY")
        summary = threat_manager.get_threat_summary()

        if summary['severity_counts']:
            total_threats = sum(summary['severity_counts'].values())
            print(f"🔥 Total threats detected: {total_threats}")
            for severity, count in summary['severity_counts'].items():
                emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
                print(f"   {emoji} {severity.title()} severity: {count}")

            print(f"🚫 IPs automatically blocked: {summary['blocked_ips']}")

            if summary['recent_threats']:
                print("🕵️ Most recent threats:")
                for threat in summary['recent_threats'][:3]:
                    ip, port, service, severity, timestamp = threat
                    emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
                    print(f"   {emoji} {ip}:{port} - {service} ({severity})")
        else:
            print("✅ No threats detected - system appears secure")

        # Phase 3: Report Generation
        print("-" * 60)
        print("📝 PHASE 3: Report Generation & Notification")
        html_report = format_report_table_html(report)

        threat_info = ""
        if summary['blocked_ips'] > 0:
            threat_info = f" - {summary['blocked_ips']} IPs BLOCKED"
        elif summary['severity_counts'].get('high', 0) > 0:
            threat_info = f" - {summary['severity_counts']['high']} HIGH THREATS"

        subject = f"Security Scan Report for {target_ip}{threat_info}"
        print("📧 Sending enhanced security report...")
        send_email(subject=subject, html_body=html_report)

        # Save and Open HTML Report
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            f.write(html_report)
            webbrowser.open(f"file://{f.name}")
            print(f"🌐 Report opened in browser: {f.name}")
    else:
        msg = f"<h2>No open ports found on {target_ip}. All is secure! 🔒</h2>"
        subject = f"Security Scan Report for {target_ip} - ALL SECURE"
        send_email(subject=subject, html_body=msg)
        print("✅ No open ports found. Security confirmation email sent.")

    print("=" * 60)
    print("✅ Scan completed successfully!")
    print("📌 TIP: Monitor threats in real-time with: sudo tail -f /var/log/syslog | grep smart_port_scanner")

    threat_manager.cleanup()


def interactive_mode():
    print("🧠 INTERACTIVE THREAT MANAGEMENT MODE")
    print("Commands: scan <ip>, status, unblock <ip>, monitor, quit")

    threat_manager = ThreatManager()

    while True:
        try:
            cmd = input("\n ThreatManager> ").strip().lower()

            if cmd.startswith('scan '):
                ip = cmd.split()[1]
                full_scan(ip)

            elif cmd == 'status':
                summary = threat_manager.get_threat_summary()
                print(f" Threat Summary: {summary}")

            elif cmd.startswith('unblock '):
                ip = cmd.split()[1]
                threat_manager.unblock_ip(ip)

            elif cmd == 'monitor':
                from threat_handler.threat_manager import ThreatMonitor
                monitor = ThreatMonitor(threat_manager)
                monitor.display_live_threats()

            elif cmd in ['quit', 'exit']:
                print("👋 Exiting threat management system")
                break

            else:
                print("❗ Unknown command. Use: scan, status, unblock, monitor, quit")

        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break

        except IndexError:
            print("❗ Invalid command format")

    threat_manager.cleanup()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive':
            interactive_mode()
            sys.exit(0)
        else:
            ip = sys.argv[1]
    else:
        ip = os.getenv("target_ip")

    if not ip:
        ip = "192.168.88.146"  # Default fallback IP

    full_scan(ip)
