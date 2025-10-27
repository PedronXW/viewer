import threading
import time


class ReceiverWatcher(threading.Thread):
    def __init__(self, app, repository, interval=30, max_age=90):
        super().__init__(daemon=True)
        self.app = app
        self.repository = repository
        self.interval = interval
        self.max_age = max_age
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        print("[Watcher] started")
        while not self._stop_event.is_set():
            with self.app.app_context():
                stale = self.repository.get_stale(self.max_age)
                for r in stale:
                    print(f"[Watcher] Releasing stale receiver {r.id}")
                    self.repository.release(r.id)
            time.sleep(self.interval)