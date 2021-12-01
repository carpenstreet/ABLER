from abc import *
import enum

import bpy


class EventKind(enum.Enum):
    login = "Login"
    login_fail = "Login Fail"
    login_auto = "Login Auto"
    render_quick = "Render Quick"
    import_blend = "Import *.blend"
    look_at_me = "Look At Me"


def accumulate(interval=0):
    """
    동시에 여러 번 실행되는 이벤트를 한 번만 트래킹하고 싶을 때 사용할 수 있는 데코레이터

    첫 호출 이후 다음 이벤트 루프(interval 주어진 경우는 해당 시간이 지나기 전)까지의 호출은 무시
    """

    def deco(f):
        accumulating = False

        def wrapper(*args, **kwargs):
            nonlocal accumulating

            if not accumulating:
                accumulating = True

                def unregister_timer_and_run():
                    nonlocal accumulating
                    f(*args, **kwargs)
                    bpy.app.timers.unregister(unregister_timer_and_run)
                    accumulating = False

                bpy.app.timers.register(
                    unregister_timer_and_run, first_interval=interval
                )

        return wrapper

    return deco


class Tracker(metaclass=ABCMeta):
    def __init__(self):
        self._agreed = True

    @abstractmethod
    def _enqueue_event(self, event_name: str):
        """
        Enqueue a user event to be tracked.

        Implementations must be asynchronous.
        """
        pass

    @abstractmethod
    def _enqueue_email_update(self, email: str):
        """
        Enqueue update of user email.

        Implementations must be asynchronous.
        """
        pass

    def _track(self, event_name: str) -> bool:
        if not self._agreed:
            return False

        try:
            self._enqueue_event(event_name)
            print(f"TRACKING: {event_name}")
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def login(self, email: str):
        if self._track(EventKind.login.value):
            self._enqueue_email_update(email)

    def login_fail(self):
        self._track(EventKind.login_fail.value)

    def login_auto(self):
        self._track(EventKind.login_auto.value)

    def render_quick(self):
        self._track(EventKind.render_quick.value)
      
    def import_blend(self):
        self._track(EventKind.import_blend.value)

    @accumulate()
    def look_at_me(self):
        self._track(EventKind.look_at_me.value)


class DummyTracker(Tracker):
    def __init__(self):
        super().__init__()
        self._agreed = False

    def _enqueue_event(self, event_name: str):
        pass

    def _enqueue_email_update(self, email: str):
        pass


class AggregateTracker(Tracker):
    def __init__(self, *trackers: Tracker):
        super().__init__()
        self.trackers = trackers

    def _enqueue_event(self, event_name: str):
        for t in self.trackers:
            t._enqueue_event(event_name)

    def _enqueue_email_update(self, email: str):
        for t in self.trackers:
            t._enqueue_email_update(email)
