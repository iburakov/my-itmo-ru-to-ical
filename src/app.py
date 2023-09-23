import logging
from asyncio import gather
from itertools import chain

import sentry_sdk
from aiohttp import ClientSession
from flask import Flask, Response
from sentry_sdk.integrations.flask import FlaskIntegration

from auth import get_access_token
from calendar_processing import build_calendar, calendar_to_ics_text
from credentials_hashing import get_credentials_hash
from lessons_to_events import raw_lesson_to_event, raw_pe_lesson_to_event
from main_api import get_raw_lessons, get_raw_pe_lessons

logging.basicConfig(level=logging.INFO)
logging.getLogger("werkzeug").handlers = []  # prevent duplicated logging output

app = Flask(__name__)
application = app  # for wsgi compliance

prefix = "ITMO_ICAL"
app.config.from_prefixed_env(prefix, loads=str)
assert "ISU_USERNAME" in app.config, f"{prefix}_ISU_USERNAME env var is required"
assert "ISU_PASSWORD" in app.config, f"{prefix}_ISU_PASSWORD env var is required"

_creds_hash = get_credentials_hash(app.config["ISU_USERNAME"], app.config["ISU_PASSWORD"])
_calendar_route = f"/calendar/{_creds_hash}"
app.logger.info(f"URL path for calendar: {_calendar_route}")

if app.config.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=app.config["SENTRY_DSN"],
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
    )


@app.route(_calendar_route)
async def get_calendar():
    async with ClientSession() as session:
        token = await get_access_token(session, app.config["ISU_USERNAME"], app.config["ISU_PASSWORD"])

        app.logger.info("Gathering lessons...")
        lessons, pe_lessons = await gather(
            get_raw_lessons(session, token),
            get_raw_pe_lessons(session, token),
        )

        app.logger.info("Building the calendar...")
        lesson_events = map(raw_lesson_to_event, lessons)
        pe_lesson_events = map(raw_pe_lesson_to_event, pe_lessons)
        calendar = build_calendar(chain(lesson_events, pe_lesson_events))
        calendar_text = calendar_to_ics_text(calendar)

        app.logger.info("Success, responding with calendar text...")
        return Response(calendar_text, content_type="text/calendar")


sentry_sdk.capture_message(f"my-itmo-ru-to-ical started for {app.config['ISU_USERNAME']}, hash {_creds_hash}")
