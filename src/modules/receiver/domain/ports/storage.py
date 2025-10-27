

from abc import ABC, abstractmethod


class StorageRepositoryAbstract(ABC):
    @abstractmethod
    async def save(self, frame, frameId) -> None:
        pass

    @abstractmethod
    async def get(self, identifier: str) -> dict:
        pass