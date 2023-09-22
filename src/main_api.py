from __future__ import annotations

from datetime import date

import requests


def _get_date_range_params() -> dict:
    """Produces start and end dates to request events of current academic term"""
    pivot = date.today().replace(month=8, day=1)
    this_year = date.today().year
    term_start_year = this_year - 1 if date.today() < pivot else this_year
    return dict(
        date_start=f"{term_start_year}-08-01",
        date_end=f"{term_start_year + 1}-07-31",
    )


def get_raw_events(auth_token: str) -> list[dict]:
    resp = requests.get(
        "https://my.itmo.ru/api/schedule/schedule/personal",
        params=_get_date_range_params(),
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    resp.raise_for_status()

    days = resp.json()["data"]
    raw_events = []
    for day in days:
        for lesson in day["lessons"]:
            raw_events.append(dict(date=day["date"], **lesson))

    return raw_events
