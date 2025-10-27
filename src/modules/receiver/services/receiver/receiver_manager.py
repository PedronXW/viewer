import socket
import threading

from modules.receiver.services.receiver.receiver_consumer import \
    ReceiverConsumer
from modules.receiver.services.receiver.receiver_watcher import ReceiverWatcher


class ReceiverManager:
    def __init__(self, app, repository):
        self.app = app
        self.repo = repository
        self.lock = threading.Lock()
        self.consumers = {}  # receiver_id -> thread
        self.owner_id = socket.gethostname()

        # start watcher
        self.watcher = ReceiverWatcher(app, repository)
        self.watcher.start()

    def start_enabled_receivers(self):
        with self.app.app_context():
            receivers = self.repo.get_enabled()
            for r in receivers:
                self.start_receiver(r)

    def start_receiver(self, receiver):
        with self.lock:
            if receiver.id in self.consumers:
                return False
            acquired = self.repo.try_acquire(receiver.id, self.owner_id)
            if not acquired:
                print(f"[Manager] receiver {receiver.id} already acquired elsewhere")
                return False
            consumer = ReceiverConsumer(self.app, self.repo, receiver)
            consumer.start()
            self.consumers[receiver.id] = consumer
            print(f"[Manager] started receiver {receiver.id}")
            return True

    def stop_receiver(self, receiver_id):
        with self.lock:
            consumer = self.consumers.pop(receiver_id, None)
            if consumer:
                consumer.stop()
                consumer.join(timeout=10)
                # repository.release will be called by consumer on normal stop; safe to force-release too:
                with self.app.app_context():
                    self.repo.release(receiver_id)
                print(f"[Manager] stopped receiver {receiver_id}")
                return True
            return False

    def stop_all(self):
        with self.lock:
            ids = list(self.consumers.keys())
        for rid in ids:
            self.stop_receiver(rid)
        self.watcher.stop()