import os
import asyncio
from dotenv import load_dotenv

from telegram_bot import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

from port_sc.port_scanner import scan_ports
from notifier.email_notifier import send_email_report
from threat_handler.threat_manager import ThreatManager
from utils.html_report import format_threat_summary_html, format_report_table_html

# 🔐 Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " Hello! I’m your *Smart Port Scanner Bot*.\nUse `/scan <IP>` to begin scanning ",
        parse_mode='Markdown'
    )

# /scan command
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❗ Please provide a target IP or domain.\nUsage: `/scan 192.168.1.1`",
            parse_mode='Markdown'
        )
        return

    target = context.args[0]
    await update.message.reply_text(
        f"🔍 Starting scan for `{target}`...\nSit tight, this may take a few minutes.",
        parse_mode='Markdown'
    )

    # Configure scan
    ports_to_scan = list(range(1, 1025))
    threat_manager = ThreatManager()

    # Run scan (in thread to avoid blocking)
    loop = asyncio.get_event_loop()
    open_ports = await loop.run_in_executor(None, scan_ports, target, ports_to_scan, threat_manager)

    # Prepare reports
    threat_summary_html = format_threat_summary_html(threat_manager.summarize())
    full_report_html = format_report_table_html(threat_manager.get_full_scan_results())

    if open_ports:
        ports_str = ", ".join(map(str, open_ports))
        await update.message.reply_text(
            f"✅ *Scan Complete for* `{target}`\n\n"
            f"*Open Ports:* `{ports_str}`\n"
            f"📧 Sending email report shortly...",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"✅ *Scan Complete for* `{target}`\n\n"
            f"No open ports found.\n📧 Email report still being sent.",
            parse_mode='Markdown'
        )

    # Send report via email
    await loop.run_in_executor(None, send_email_report, f"Scan Report for {target}", full_report_html + "<br><br>" + threat_summary_html)

# Bot entry point
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))

    app.run_polling()

if __name__ == "__main__":
    main()
