# -*- coding: utf-8 -*-

from datetime import datetime

from loguru import logger

from .base import cloudflare_zone_gql

GET_SAMPLED_LOGS_GQL = """
query Viewer {
    viewer {
        zones(filter: { zoneTag: $zoneId }) {
            httpRequestsAdaptive(
                filter: { datetime_gt: $startDt, datetime_lt: $endDt }
                limit: $limit
                orderBy: [datetime_DESC]
            ) {
                cacheStatus
                clientASNDescription
                clientAsn
                clientCountryName
                clientDeviceType
                clientIP
                clientRequestHTTPHost
                clientRequestHTTPMethodName
                clientRequestHTTPProtocol
                clientRequestPath
                clientRequestQuery
                clientRequestScheme
                clientSSLProtocol
                datetime
                edgeResponseStatus
                httpApplicationVersion
                leakedCredentialCheckResult
                requestSource
                securityAction
                securitySource
                userAgent
                userAgentBrowser
                userAgentOS
            }
        }
    }
}
"""


def get_sampled_logs(
    start_dt: datetime,
    end_dt: datetime,
    limit: int = 10,
):
    response = cloudflare_zone_gql(
        request_string=GET_SAMPLED_LOGS_GQL,
        variable_values={
            "startDt": start_dt.isoformat(),
            "endDt": end_dt.isoformat(),
            "limit": limit,
        },
    )

    requests = response["viewer"]["zones"][0]["httpRequestsAdaptive"]

    logger.debug(
        f"Getting sampled_logs ({start_dt} ~ {end_dt}), length: {len(requests)}"
    )
    return requests


def get_sampled_logs_full(
    start_dt: datetime,
    end_dt: datetime,
):
    _end_dt = end_dt

    requests: list[dict] = []

    logger.info(f"Getting sampled_logs ({start_dt} ~ {_end_dt})")

    while True:
        if start_dt >= _end_dt:
            break

        _requests = get_sampled_logs(
            start_dt=start_dt,
            end_dt=_end_dt,
            limit=100,
        )
        requests.extend(_requests)

        if len(_requests) == 0 or len(_requests) < 100:
            break

        _end_dt = datetime.fromisoformat(_requests[-1]["datetime"])

    logger.info(f"Getting sampled_logs finished, length: {len(requests)}")

    return requests
