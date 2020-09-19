from datetime import datetime

from tools.db import db


def get_today_time():
    cursor = db.cursor()
    cursor.execute(
        "SELECT seconds FROM day_log WHERE day_field=:today", {
            "today": datetime.now().strftime("%Y-%m-%d")})
    seconds = cursor.fetchone()
    return seconds[0] if seconds else 0
