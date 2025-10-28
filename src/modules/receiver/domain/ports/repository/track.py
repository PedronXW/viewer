from abc import ABC, abstractmethod

from modules.receiver.domain.track import Track


class TrackRepositoryAbstract(ABC):
    @abstractmethod
    async def add(self, Track: Track) -> None:
        pass