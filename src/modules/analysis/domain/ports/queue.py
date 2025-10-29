from abc import ABC, abstractmethod


class QueueRepositoryAbstract(ABC):
    @abstractmethod
    async def publish(self, message: dict) -> None:
        pass