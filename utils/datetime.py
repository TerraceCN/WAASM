# -*- coding: utf-8 -*-

from datetime import datetime, timedelta


def for_datatime_minutes(start_dt: datetime, end_dt: datetime):
    start_dt = start_dt.replace(second=0, microsecond=0)
    end_dt = end_dt.replace(second=0, microsecond=0)

    while start_dt <= end_dt:
        yield start_dt
        start_dt += timedelta(minutes=1)
