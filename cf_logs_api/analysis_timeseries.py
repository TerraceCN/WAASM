# -*- coding: utf-8 -*-

from datetime import datetime

from loguru import logger

from .base import cloudflare_zone_gql

ANALYSIS_TIMESERIES_GQL = """
query Viewer {
    viewer {
        zones(filter: { zoneTag: $zoneId }) {
            mitigatedByWAF: httpRequestsAdaptiveGroups(
                limit: $limit
                filter: {
                    datetime_geq: $startDt,
                    datetime_leq: $endDt,
                    requestSource: "eyeball",
                    securityAction_in: [
                        "block",
                        "challenge",
                        "jschallenge",
                        "managed_challenge"
                    ]
                }
                orderBy: [datetimeMinute_DESC]
            ) {
                count
                dimensions {
                    ts: datetimeMinute
                }
            }
            servedByCloudflare: httpRequestsAdaptiveGroups(
                limit: $limit
                filter: {
                    datetime_geq: $startDt,
                    datetime_leq: $endDt,
                    requestSource: "eyeball",
                    securityAction_notin: [
                        "block",
                        "challenge",
                        "jschallenge",
                        "managed_challenge"
                    ],
                    cacheStatus_notin: [
                        "miss",
                        "expired",
                        "bypass",
                        "dynamic"
                    ]
                }
                orderBy: [datetimeMinute_DESC]
            ) {
                count
                dimensions {
                    ts: datetimeMinute
                }
            }
            servedByOrigin: httpRequestsAdaptiveGroups(
                limit: $limit
                filter: {
                    datetime_geq: $startDt,
                    datetime_leq: $endDt,
                    requestSource: "eyeball",
                    cacheStatus_in: [
                        "miss",
                        "expired",
                        "bypass",
                        "dynamic"
                    ]
                }
                orderBy: [datetimeMinute_DESC]
            ) {
                count
                dimensions {
                    ts: datetimeMinute
                }
            }
        }
    }
}
"""


def get_analysis_timeseries(
    start_dt: datetime,
    end_dt: datetime,
    limit: int = 5000,
):
    start_dt = start_dt.replace(second=0, microsecond=0)
    end_dt = end_dt.replace(second=0, microsecond=0)

    logger.info(f"Getting analysis_timeseries ({start_dt} ~ {end_dt})")

    response = cloudflare_zone_gql(
        request_string=ANALYSIS_TIMESERIES_GQL,
        variable_values={
            "limit": limit,
            "startDt": start_dt.isoformat(),
            "endDt": end_dt.isoformat(),
        },
    )

    timeseries = response["viewer"]["zones"][0]

    waf = timeseries["mitigatedByWAF"]
    waf_sum = sum([x["count"] for x in waf])

    cf = timeseries["servedByCloudflare"]
    cf_sum = sum([x["count"] for x in cf])

    origin = timeseries["servedByOrigin"]
    origin_sum = sum([x["count"] for x in origin])

    logger.info(
        f"Getting analysis_timeseries finished, WAF: {waf_sum}, CF: {cf_sum}, Origin: {origin_sum}"
    )

    return timeseries
