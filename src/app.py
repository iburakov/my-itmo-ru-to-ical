import logging
from pathlib import Path

import sentry_sdk
from flask import Flask, Response
from sentry_sdk.integrations.flask import FlaskIntegration

from auth import get_access_token
from calendar_processing import get_raw_events, raw_events_to_calendar
from creds import get_creds_hash

logging.basicConfig(level=logging.INFO)
logging.getLogger("werkzeug").handlers = []  # to prevent duplicated logging output
app = Flask(__name__)
application = app  # for wsgi compliance

app.config.from_pyfile(Path("../config/config.py"))

_creds_hash = get_creds_hash(app.config["ISU_USERNAME"], app.config["ISU_PASSWORD"])
_calendar_route = f"/calendar/{_creds_hash}"
app.logger.info(f"URL path for calendar: {_calendar_route}")

if app.config["SENTRY_DSN"]:
    sentry_sdk.init(
        dsn=app.config["SENTRY_DSN"],
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
    )


@app.route(_calendar_route)
def get_calendar():
    token = get_access_token(app.config["ISU_USERNAME"], app.config["ISU_PASSWORD"])
    events = get_raw_events(token)
    calendar = raw_events_to_calendar(events)
    return Response("\n".join(map(str.strip, calendar)), content_type="text/calendar")


sentry_sdk.capture_message(f"my-itmo-ru-to-ical started for {app.config['ISU_USERNAME']}, hash {_creds_hash}")
