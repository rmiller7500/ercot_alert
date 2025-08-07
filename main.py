import os
from fastapi import FastAPI
from monitor import get_current_price, THRESHOLD, SETTLEMENT_POINT

app = FastAPI(title="ERCOT Price Monitor")

@app.get("/")
def root():
    return {"message": "ERCOT Price Monitor is running.",
            "threshold": THRESHOLD,
            "settlement_point": SETTLEMENT_POINT}

@app.get("/price")
def price():
    """Return the most recently cached price and timestamp."""
    return get_current_price()