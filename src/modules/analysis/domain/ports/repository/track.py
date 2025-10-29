from abc import ABC, abstractmethod

from modules.analysis.domain.track import Track


class TrackRepositoryAbstract(ABC):
    @abstractmethod
    async def add(self, Track: Track) -> None:
        pass
    
    @abstractmethod
    async def get(self, track_id: str) -> Track | None:
        pass