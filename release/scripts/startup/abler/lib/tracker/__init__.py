import os
from dotenv import load_dotenv
from ._tracker import Tracker, DummyTracker, AggregateTracker


def _remote_tracker(mixpanel_token, sentry_dsn):
    from ._mixpanel import MixpanelTracker
    from ._sentry import SentryTracker

    return AggregateTracker(MixpanelTracker(mixpanel_token), SentryTracker(sentry_dsn))


load_dotenv(verbose=True)
sentry_dsn = os.getenv("SENTRY_DSN")
mixpanel_token = os.getenv("MIXPANEL_TOKEN")
if sentry_dsn or mixpanel_token:
    raise RuntimeError("You must set either SENTRY_DSN or MIXPANEL_TOKEN")

tracker: Tracker = (
    DummyTracker()
    if os.environ.get("DISABLE_TRACK")
    else _remote_tracker(mixpanel_token, sentry_dsn)
)
