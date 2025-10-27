from modules.receiver.domain.ports.repository.receiver import \
    ReceiverRepositoryAbstract


class ListReceiversService:
    def __init__(self, receiver_repository: ReceiverRepositoryAbstract):
        self.receiver_repository = receiver_repository

    def execute(self):
        return self.receiver_repository.list_all()