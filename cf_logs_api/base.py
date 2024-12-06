# -*- coding: utf-8 -*-

from typing import Any, Optional

from gql import gql, Client
from gql.transport.httpx import HTTPXTransport
from loguru import logger

import utils.config as config


def cloudflare_zone_gql(
    request_string: str,
    variable_values: dict[str, Any],
    zone_id: Optional[str] = None,
    api_key: Optional[str] = None,
    proxy: Optional[str] = None,
    timeout: Optional[int] = None,
):
    if zone_id is None:
        zone_id: str = config.get("cloudflare", "zone_id", required=True)
    if api_key is None:
        api_key: str = config.get("cloudflare", "api_key")

    variable_values = variable_values.copy()
    variable_values.update({"zoneId": zone_id})

    proxy = proxy or config.get("request", "proxy_url")
    if proxy.strip() == "":
        proxy = None

    if timeout is None:
        timeout = config.get("request", "timeout", default=30)

    client = Client(
        transport=HTTPXTransport(
            url="https://api.cloudflare.com/client/v4/graphql",
            headers={"Authorization": f"Bearer {api_key}"},
            proxy=proxy,
            timeout=timeout,
        ),
    )
    response = client.execute(gql(request_string), variable_values=variable_values)
    logger.debug(
        f"Cloudflare GraphQL request: {request_string!r}, variable_values: {variable_values!r}, response: {response!r}"
    )
    return response
