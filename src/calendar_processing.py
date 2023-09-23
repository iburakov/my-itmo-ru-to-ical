from __future__ import annotations

import logging
from typing import Iterable

from ics import Calendar, Event

logger = logging.getLogger(__name__)


def build_calendar(events: Iterable[Event]):
    calendar = Calendar()
    calendar.creator = "my-itmo-ru-to-ical"
    for event in events:
        calendar.events.add(event)
    logger.info(f"Built a calendar with {len(calendar.events)} events")
    return calendar


def calendar_to_ics_text(calendar: Calendar) -> str:
    return "\n".join(map(str.strip, calendar))
