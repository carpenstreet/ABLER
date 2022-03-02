import os
import sys

from ._tracker import Tracker, DummyTracker, AggregateTracker


def _remote_tracker():
    from ._mixpanel import MixpanelTracker
    from ._sentry import SentryTracker

    return AggregateTracker(MixpanelTracker(), SentryTracker())


tracker: Tracker = (
    DummyTracker()
    if (
        os.environ.get("DISABLE_TRACK")
        or "--background" in sys.argv
        or "-b" in sys.argv
    )
    else _remote_tracker()
)
