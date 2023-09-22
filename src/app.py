import logging

import sentry_sdk
from flask import Flask, Response
from sentry_sdk.integrations.flask import FlaskIntegration

from auth import get_access_token
from calendar_processing import raw_events_to_calendar
from credentials_hashing import get_credentials_hash
from main_api import get_raw_events

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
def get_calendar():
    token = get_access_token(app.config["ISU_USERNAME"], app.config["ISU_PASSWORD"])
    events = get_raw_events(token)
    calendar = raw_events_to_calendar(events)
    return Response("\n".join(map(str.strip, calendar)), content_type="text/calendar")


sentry_sdk.capture_message(f"my-itmo-ru-to-ical started for {app.config['ISU_USERNAME']}, hash {_creds_hash}")
