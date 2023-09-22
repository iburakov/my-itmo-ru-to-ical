from __future__ import annotations

from datetime import datetime, timedelta

from dateutil.parser import isoparse
from ics import Calendar, Event

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


def raw_events_to_calendar(raw_events: list[dict]):
    calendar = Calendar()
    calendar.creator = "my-itmo-ru-to-ical"
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
