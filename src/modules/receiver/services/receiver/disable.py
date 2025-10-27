from modules.receiver.domain.ports.repository.receiver import \
    ReceiverRepositoryAbstract
from modules.receiver.domain.receiver import Receiver


class DisableReceiverService:
    def __init__(self, receiver_repository: ReceiverRepositoryAbstract, manager):
        self.receiver_repository = receiver_repository
        self.manager = manager

    def execute(self, receiver_id: str):
        receiver = self.receiver_repository.get_by_id(receiver_id)
        if not receiver:
            return None
        receiver.enabled = False
        self.receiver_repository.update(receiver)
        self.manager.stop_receiver(receiver.id)
        return receiver