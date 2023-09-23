from __future__ import annotations

import logging
from datetime import date
from typing import Iterable

from aiohttp import ClientSession

logger = logging.getLogger(__name__)

_API_BASE_URL = "https://my.itmo.ru/api"


def _get_date_range_params() -> dict:
    """Produces start and end dates to request events of current academic term"""
    pivot = date.today().replace(month=8, day=1)
    this_year = date.today().year
    term_start_year = this_year - 1 if date.today() < pivot else this_year
    return dict(
        date_start=f"{term_start_year}-08-01",
        date_end=f"{term_start_year + 1}-07-31",
    )


async def _get_calendar(session: ClientSession, auth_token: str, path: str) -> dict:
    url = _API_BASE_URL + path
    params = _get_date_range_params()
    logger.info(f"Getting calendar from {url}, using params {params}")

    resp = await session.get(url, params=params, headers={"Authorization": f"Bearer {auth_token}"})
    resp.raise_for_status()
    return await resp.json()


async def get_raw_lessons(session: ClientSession, auth_token: str) -> Iterable[dict]:
    resp_json = await _get_calendar(session, auth_token, "/schedule/schedule/personal")
    days = resp_json["data"]
    return (dict(date=day["date"], **lesson) for day in days for lesson in day["lessons"])


async def get_raw_pe_lessons(session: ClientSession, auth_token: str) -> Iterable[dict]:
    resp_json = await _get_calendar(session, auth_token, "/sport/my_sport/calendar")
    days = resp_json["result"]
    return (dict(**lesson) for day in days for lesson in day["lessons"])
