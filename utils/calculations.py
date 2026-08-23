"""Calculations for Freshness Engine and Zero-Waste Metrics."""
from datetime import datetime, date, timedelta
from typing import Tuple

def calculate_expiry_date(added_date: date, shelf_life_days: int) -> date:
    """Calculate the estimated expiry date given added date and shelf life."""
    return added_date + timedelta(days=max(0, shelf_life_days))

def calculate_freshness(added_date_str: str, shelf_life_days: int) -> Tuple[str, int, str]:
    """
    Calculate freshness status, days remaining, and expiry date string.
    Status classifications:
      - <= 0 days: 'USE TODAY'
      - 1 to 2 days: 'USE SOON'
      - >= 3 days: 'FRESH'
    Returns: (freshness_status, days_remaining, expiry_date_str)
    """
    try:
        if isinstance(added_date_str, str):
            # parse date string (handles 'YYYY-MM-DD', 'YYYY-MM-DD HH:MM:SS', 'YYYY-MM-DDTHH:MM:SS')
            clean_date_str = added_date_str.split("T")[0].split(" ")[0].strip()
            added_dt = datetime.strptime(clean_date_str, "%Y-%m-%d").date()
        elif isinstance(added_date_str, (date, datetime)):
            added_dt = added_date_str if isinstance(added_date_str, date) else added_date_str.date()
        else:
            added_dt = date.today()
    except Exception:
        added_dt = date.today()


    expiry_dt = calculate_expiry_date(added_dt, shelf_life_days)
    today = date.today()
    days_remaining = (expiry_dt - today).days

    if days_remaining <= 0:
        status = "USE TODAY"
    elif days_remaining <= 2:
        status = "USE SOON"
    else:
        status = "FRESH"

    return status, days_remaining, expiry_dt.strftime("%Y-%m-%d")

def calculate_zero_waste_score(total_kitchen_items: int, fresh_items_count: int, expiring_items_count: int = 0) -> int:
    """
    Calculate zero waste utilization score from 0 to 100%.
    A kitchen with all fresh ingredients achieves 100% score.
    Expiring items reduce the score until cooked / rescued.
    """
    if total_kitchen_items <= 0:
        return 100
    ratio = max(0.0, min(1.0, fresh_items_count / max(1, total_kitchen_items)))
    score = int(round(ratio * 100))
    return max(10, min(100, score))

