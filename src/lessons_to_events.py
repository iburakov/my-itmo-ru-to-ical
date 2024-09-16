from datetime import datetime, timedelta
from hashlib import md5
from uuid import UUID

from dateutil.parser import isoparse
from ics import Event

_lesson_type_to_tag_map = {
    "Лекции": "Лек",
    "Практические занятия": "Прак",
    "Лабораторные занятия": "Лаб",
    "Занятия спортом": "Спорт",
}

_raw_lesson_key_names = {
    "group": "Группа",
    "teacher_name": "Преподаватель",
    "teacher_fio": "Преподаватель",
    "zoom_url": "Ссылка на Zoom",
    "zoom_password": "Пароль Zoom",
    "zoom_info": "Доп. информация для Zoom",
    "note": "Примечание",
}


def _lesson_type_to_tag(t: str):
    return _lesson_type_to_tag_map.get(t, t)


def _raw_lesson_to_description(raw_lesson: dict):
    lines = []
    for key, name in _raw_lesson_key_names.items():
        if raw_lesson.get(key):
            lines.append(f"{name}: {raw_lesson[key]}")

    _msk_formatted_datetime = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")
    lines.append(f"Обновлено: {_msk_formatted_datetime} MSK")
    return "\n".join(lines)


def _raw_lesson_to_location(raw_lesson: dict):
    elements = []
    for key in "room", "building":
        if raw_lesson.get(key):
            elements.append(raw_lesson[key])

    result = ", ".join(elements)

    if raw_lesson.get("zoom_url"):
        result = f"Zoom / {result}" if result else "Zoom"

    return result if result else None


def _raw_lesson_to_uuid(raw_lesson: dict):
    elements = [
        raw_lesson["date"],
        raw_lesson["time_start"],
        raw_lesson["subject"],
    ]
    result = ", ".join(elements)
    md5_of_lesson = md5(result.encode("utf-8")).hexdigest()
    result_uuid = str(UUID(hex=md5_of_lesson))
    return result_uuid


def raw_lesson_to_event(raw_lesson: dict) -> Event:
    begin = isoparse(f"{raw_lesson['date']}T{raw_lesson['time_start']}:00+03:00")
    end = isoparse(f"{raw_lesson['date']}T{raw_lesson['time_end']}:00+03:00")
    # If there is a mistake in event
    if begin > end:
        begin, end = end, begin
    event = Event(
        name=f"[{_lesson_type_to_tag(raw_lesson['type'])}] {raw_lesson['subject']}",
        begin=begin,
        end=end,
        description=_raw_lesson_to_description(raw_lesson),
        location=_raw_lesson_to_location(raw_lesson),
        uid=_raw_lesson_to_uuid(raw_lesson),
    )
    if raw_lesson["zoom_url"]:
        event.url = raw_lesson["zoom_url"]

    return event
