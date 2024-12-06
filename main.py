# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from loguru import logger

from cf_logs_api import (
    get_sampled_logs_full,
    get_analysis_timeseries,
)
import utils.config as config
from utils.collections import deduplicate
from utils.datetime import for_datatime_minutes

logger.remove()
logger.add(sys.stderr, level=config.get("logging", "level", default="INFO"))


def create_data_path(data_dir: str):
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)

    gitignore = data_path / ".gitignore"

    if not gitignore.exists():
        gitignore.write_text("*")

    return data_path


def save_data_to_file(events: list[dict], file_path: Path, key):
    events = events.copy()

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as fp:
            saved_events = json.load(fp)
        logger.info(f"Loaded {len(saved_events)} data from {file_path}")
    else:
        saved_events = []

    events.extend(saved_events)
    events = deduplicate(events, key=key)
    events.sort(key=lambda x: datetime.fromisoformat(x["datetime"]))

    with open(file_path, "w", encoding="utf-8") as fp:
        json.dump(events, fp, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(events)} data to {file_path}")


def save_data(events: list[dict], dir_path: Path, key):
    dir_path.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc)
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)

    yesterday_events = [
        event for event in events if datetime.fromisoformat(event["datetime"]) < today
    ]
    if len(yesterday_events) > 0:
        save_data_to_file(
            yesterday_events, dir_path / f"{yesterday.strftime('%Y%m%d')}.json", key
        )

    today_events = [
        event for event in events if datetime.fromisoformat(event["datetime"]) >= today
    ]
    if len(today_events) > 0:
        save_data_to_file(
            today_events, dir_path / f"{today.strftime('%Y%m%d')}.json", key
        )


def main():
    data_path = create_data_path(config.get("sampling", "data_dir", default="data"))
    interval: int = config.get("sampling", "interval", default=1805)

    end_dt = datetime.now(timezone.utc).replace(microsecond=0)
    start_dt = end_dt - timedelta(seconds=interval)

    def _request_key(e: dict) -> str:
        e_hash_raw = [
            e[k]
            for k in [
                "datetime",
                "clientIP",
                "clientRequestHTTPMethodName",
                "clientRequestScheme",
                "clientRequestHTTPHost",
                "clientRequestPath",
                "clientRequestQuery",
            ]
        ]
        e_hash = sha256("_".join(e_hash_raw).encode("utf-8")).hexdigest()
        return e_hash

    requests = get_sampled_logs_full(start_dt=start_dt, end_dt=end_dt)
    save_data(requests, data_path / "requests", key=_request_key)

    timeseries = get_analysis_timeseries(start_dt=start_dt, end_dt=end_dt)
    ts_data = {
        str(int(dt.timestamp())): {
            "datetime": dt.isoformat(),
            "mitigatedByWAF": 0,
            "servedByCloudflare": 0,
            "servedByOrigin": 0,
        }
        for dt in for_datatime_minutes(start_dt, end_dt)
    }
    for t in timeseries["mitigatedByWAF"]:
        ts_data[str(int(datetime.fromisoformat(t["dimensions"]["ts"]).timestamp()))][
            "mitigatedByWAF"
        ] = t["count"]
    for t in timeseries["servedByCloudflare"]:
        ts_data[str(int(datetime.fromisoformat(t["dimensions"]["ts"]).timestamp()))][
            "servedByCloudflare"
        ] = t["count"]
    for t in timeseries["servedByOrigin"]:
        ts_data[str(int(datetime.fromisoformat(t["dimensions"]["ts"]).timestamp()))][
            "servedByOrigin"
        ] = t["count"]
    ts_data_list = sorted(ts_data.values(), key=lambda x: x["datetime"])
    save_data(ts_data_list, data_path / "timeseries", key=lambda e: e["datetime"])


if __name__ == "__main__":
    main()
