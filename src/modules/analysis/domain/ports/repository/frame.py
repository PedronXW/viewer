from abc import ABC, abstractmethod

from modules.analysis.domain.frame import Frame


class FrameRepositoryAbstract(ABC):
    @abstractmethod
    async def add(self, Frame: Frame) -> None:
        pass

    @abstractmethod
    async def remove(self, Frame: Frame) -> None:
        pass
    
    @abstractmethod
    async def get_by_id(self, Frame_id: str) -> Frame | None:
        pass