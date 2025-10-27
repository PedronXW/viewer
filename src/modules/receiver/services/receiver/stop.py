from modules.receiver.domain.ports.repository.receiver import \
    ReceiverRepositoryAbstract


class StopReceiverService:
    def __init__(self, receiver_repository: ReceiverRepositoryAbstract, manager):
        self.receiver_repository = receiver_repository
        self.manager = manager

    def execute(self, receiver_id: str):
        stopped = self.manager.stop_receiver(receiver_id)
        return stopped