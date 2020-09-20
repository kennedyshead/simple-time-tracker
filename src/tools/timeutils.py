from datetime import datetime, timedelta

from tools.db import db


def get_today_time():
    cursor = db.cursor()
    cursor.execute(
        "SELECT seconds FROM day_log WHERE day_field=:today", {
            "today": datetime.now().strftime("%Y-%m-%d")})
    seconds = cursor.fetchone()
    return seconds[0] if seconds else 0


def get_not_counted_days():
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, seconds FROM day_log WHERE counted=0 AND day_field<:today",
        {"today": datetime.now()}
    )
    days = cursor.fetchall()
    return days


def negative_handle(flex):
    if flex < 0:
        return "-%s" % str(timedelta(seconds=-flex))
    else:
        return str(timedelta(seconds=flex))
