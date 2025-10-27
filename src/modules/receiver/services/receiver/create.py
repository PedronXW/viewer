from src.modules.receiver.domain.ports.repository.receiver import \
    ReceiverRepositoryAbstract
from src.modules.receiver.domain.receiver import Receiver, ReceiverProps


class CreateReceiverService:
    def __init__(self, receiver_repository: ReceiverRepositoryAbstract):
        self.receiver_repository = receiver_repository

    async def execute(self, props: ReceiverProps) -> None:
        receiver = Receiver(props)
        await self.receiver_repository.add(receiver)