import os
import re
import time

import bpy
import sentry_sdk

from ._tracker import Tracker


class SentryTracker(Tracker):
    def __init__(self, sentry_dsn: str):
        super().__init__()
        sentry_sdk.init(
            sentry_dsn,
            release=make_release_version(),
        )
        print("Sentry Initialized")

    def _enqueue_event(self, event_name: str):
        sentry_sdk.add_breadcrumb(
            category="event", message=event_name, timestamp=time.time()
        )

    def _enqueue_email_update(self, email: str):
        sentry_sdk.set_user({"email": email})


def make_release_version():
    """
    release/v0.0.1 형태의 경우 -> abler.release@0.0.1+hash 형태로 출력.
    기타 -> abler.devel@hash 형태로 출력.
    참고: https://docs.sentry.io/platforms/python/configuration/releases/
    """

    package = "abler.devel"
    # NOTE: 커밋되지 않은 변경사항이 있는 경우 "branch_name (modified)" 로 출력됨
    branch = bpy.app.build_branch.decode("utf-8", "replace")
    version = bpy.app.build_hash.decode("ascii")

    if m := re.match(r"release/v(\d+)\.(\d+)\.(\d+)", branch):
        package = "abler.release"
        version = f"{m[1]}.{m[2]}.{m[3]}+{version}"

    return package + "@" + version
