from src.modules.receiver.domain.ports.repository.receiver import \
    ReceiverRepositoryAbstract
from src.modules.receiver.domain.receiver import Receiver


class GetReceiverService:
    def __init__(self, receiver_repository: ReceiverRepositoryAbstract):
        self.receiver_repository = receiver_repository

    async def execute(self, receiver_id: int) -> Receiver | None:
        receiver = await self.receiver_repository.get_by_id(receiver_id)
        return receiver