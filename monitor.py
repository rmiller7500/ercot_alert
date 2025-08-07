"""Background job that polls ERCOT real‑time prices every 5 minutes and sends email alerts."""
import os, logging
from datetime import datetime
from email.message import EmailMessage
import smtplib

from apscheduler.schedulers.background import BackgroundScheduler
from gridstatus import Ercot

# Configuration via environment variables
THRESHOLD = float(os.getenv("PRICE_THRESHOLD", "150"))  # $/MWh
SETTLEMENT_POINT = os.getenv("SETTLEMENT_POINT", "HB_HOUSTON")  # e.g. HB_HOUSTON, LZ_HOUSTON
RECIPIENTS = [e.strip() for e in os.getenv("ALERT_EMAILS", "").split(",") if e.strip()]

# SMTP setup
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

ercot = Ercot()  # Requires ERCOT API credentials in env variables or will fallback to HTML scrape

_cache = {"timestamp": None, "price": None}

def fetch_price():
    global _cache
    try:
        df = ercot.get_lmp(date="latest", settlement_point=SETTLEMENT_POINT)
        price = float(df.loc[0, "LMP"])
        ts = df.loc[0, "Time"]
        _cache = {"timestamp": ts.isoformat(), "price": price}
        if price >= THRESHOLD:
            send_alert(price, ts)
    except Exception as e:
        logging.exception("Error fetching price: %s", e)

def get_current_price():
    """Return cached price dict."""
    return _cache

def send_alert(price: float, ts: datetime):
    if not RECIPIENTS:
        logging.warning("No ALERT_EMAILS configured; skipping alert")
        return
    subject = f"ERCOT price alert: ${price:.2f}/MWh at {ts.strftime('%Y-%m-%d %H:%M')}"
    body = (
        f"Real‑time price at settlement point {SETTLEMENT_POINT} reached "
        f"${price:.2f}/MWh at {ts}.\n"
        f"Configured threshold: ${THRESHOLD}/MWh"
    )
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = ", ".join(RECIPIENTS)
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
        logging.info("Alert email sent to %s", RECIPIENTS)
    except Exception as e:
        logging.exception("Failed to send alert email: %s", e)

# start scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_price, "interval", minutes=5, next_run_time=datetime.utcnow())
scheduler.start()