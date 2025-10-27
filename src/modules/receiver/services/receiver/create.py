from modules.receiver.domain.ports.repository.receiver import \
    ReceiverRepositoryAbstract
from modules.receiver.domain.receiver import Receiver, ReceiverProps


class CreateReceiverService:
    def __init__(self, receiver_repository: ReceiverRepositoryAbstract):
        self.receiver_repository = receiver_repository

    def execute(self, props: ReceiverProps) -> None:
        receiver = Receiver(props)
        self.receiver_repository.create(receiver)