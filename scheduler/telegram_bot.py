from telegram.ext import Updater, CommandHandler
from port_sc.port_scanner import scan_ports
from notifier.email_notifier import send_email_report
from threat_handler.threat_manager import ThreatManager
from utils.html_report import format_threat_summary_html, format_report_table_html
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def start(update, context):
    update.message.reply_text(" Hello! I’m your *Smart Port Scanner Bot*.\nUse `/scan <IP>` to begin scanning ", parse_mode='Markdown')

def scan(update, context):
    if not context.args:
        update.message.reply_text("❗ Please provide a target IP or domain.\nUsage: `/scan 192.168.1.1`", parse_mode='Markdown')
        return

    target = context.args[0]
    update.message.reply_text(f" Starting scan for `{target}`...\nSit tight, this may take a few minutes ", parse_mode='Markdown')

    # Define scan range and threat manager
    ports_to_scan = list(range(1, 1025))  # You can extend this as needed
    threat_manager = ThreatManager()

    # Perform scan
    open_ports = scan_ports(target, ports_to_scan, threat_manager=threat_manager)

    # Format summary and full HTML report
    threat_summary_html = format_threat_summary_html(threat_manager.summarize())
    full_report_html = format_report_table_html(threat_manager.get_full_scan_results())

    # Send quick summary in chat
    if open_ports:
        ports_str = ", ".join(map(str, open_ports))
        update.message.reply_text(
            f" *Scan Complete for* `{target}`\n\n"
            f" *Open Ports:* `{ports_str}`\n"
            f" Sending email report shortly...",
            parse_mode='Markdown'
        )
    else:
        update.message.reply_text(
            f" *Scan Complete for* `{target}`\n\n"
            f" No open ports found.\n"
            f" Email report still being sent.",
            parse_mode='Markdown'
        )

    # Send email report
    send_email_report(subject=f"Scan Report for {target}", html_body=full_report_html + "<br><br>" + threat_summary_html)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("scan", scan))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
