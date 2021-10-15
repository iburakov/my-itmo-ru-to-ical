from datetime import datetime, timedelta
from typing import List

import requests
from dateutil.parser import isoparse
from flask import current_app
from ics import Event, Calendar

_event_type_to_tag_map = {
    "Лекции": "Лек",
    "Практические занятия": "Прак",
    "Зачет": "Зачет",
}

_raw_event_key_names = {
    "group": "Группа",
    "teacher_name": "Преподаватель",
    "zoom_url": "Ссылка на Zoom",
    "zoom_password": "Пароль Zoom",
    "zoom_info": "Доп. информация для Zoom",
    "note": "Примечание",
}

_CALENDAR_CREATOR_VALUE = "my-itmo-ru-to-ical"


def get_raw_events(auth_token: str) -> List[dict]:
    resp = requests.get(
        "https://my.itmo.ru/api/schedule/schedule/personal",
        params=dict(
            date_start=current_app.config["SCHEDULE_START_DATE"],
            date_end=current_app.config["SCHEDULE_END_DATE"],
        ),
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    resp.raise_for_status()
    days = resp.json()["data"]
    raw_events = []
    for day in days:
        for lesson in day["lessons"]:
            raw_events.append(dict(date=day["date"], **lesson))

    return raw_events


def _event_type_to_tag(t: str):
    return _event_type_to_tag_map.get(t, t)


def _raw_event_to_description(re: dict):
    lines = []
    for key, name in _raw_event_key_names.items():
        if re[key]:
            lines.append(f"{name}: {re[key]}")

    _msk_formatted_datetime = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")
    lines.append(f"Обновлено: {_msk_formatted_datetime} MSK")
    return "\n".join(lines)


def _raw_event_to_location(re: dict):
    elements = []
    for key in "room", "building":
        if re[key]:
            elements.append(re[key])

    result = ", ".join(elements)

    if re["zoom_url"]:
        result = f"Zoom / {result}" if result else "Zoom"

    return result if result else None


def raw_events_to_calendar(raw_events: List[dict]):
    calendar = Calendar()
    calendar.creator = _CALENDAR_CREATOR_VALUE
    for raw_event in raw_events:
        event = Event(
            name=f"[{_event_type_to_tag(raw_event['type'])}] {raw_event['subject']}",
            begin=isoparse(f"{raw_event['date']}T{raw_event['time_start']}:00+03:00"),
            end=isoparse(f"{raw_event['date']}T{raw_event['time_end']}:00+03:00"),
            description=_raw_event_to_description(raw_event),
            location=_raw_event_to_location(raw_event),
        )
        if raw_event["zoom_url"]:
            event.url = raw_event["zoom_url"]

        calendar.events.add(event)

    return calendar
