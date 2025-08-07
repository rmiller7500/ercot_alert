# ERCOT Real‑Time Price Monitor

A minimal FastAPI application that polls ERCOT real‑time Locational Marginal Prices (LMP) every 5 minutes and sends email alerts when the price at your chosen settlement point meets or exceeds a configurable threshold.

## Features
* Polls ERCOT every 5 minutes via the [`gridstatus`](https://github.com/gridstatus/gridstatus) library
* Caches the latest price and exposes it at `GET /price`
* Sends threshold‑based email alerts via SMTP
* Runs entirely server‑side—host it anywhere Python 3.11+ is available

## Quick Start
```bash
git clone <this‑repo> ercot_alert
cd ercot_alert
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your credentials and desired threshold
uvicorn main:app --host 0.0.0.0 --port 8000
```
The first poll and any alerts will show in your console logs.

## Environment Variables
See `.env.example` for all available settings. Only `PRICE_THRESHOLD`, `SETTLEMENT_POINT`, and email settings are strictly required for alerts.

## Deployment
* **Docker:** create a container from this directory and supply environment variables at runtime.
* **Systemd / Ubuntu:** run `uvicorn` under a systemd service to keep it active.
* **Heroku / Fly.io / Render:** add your environment variables in the dashboard and deploy as a generic Python service.

## Front‑End (Optional)
This repo focuses on server‑side monitoring. If you’d like a live dashboard, create a simple React/Vue/HTML page that polls `/price` and renders the latest values. The API is JSON, so integration is straightforward.

---

*Generated on 2025-08-07*