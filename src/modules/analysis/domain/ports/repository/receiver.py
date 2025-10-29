from abc import ABC, abstractmethod
from typing import List

from modules.analysis.domain.receiver import Receiver


class ReceiverRepositoryAbstract(ABC):
    @abstractmethod
    def get_all(self) -> List[Receiver]:
        ...

    @abstractmethod
    def get_enabled(self) -> List[Receiver]:
        ...

    @abstractmethod
    def get_by_id(self, receiver_id: int) -> Receiver:
        ...

    @abstractmethod
    def create(self, props: Receiver) -> Receiver:
        ...

    @abstractmethod
    def update(self, receiver: Receiver) -> None:
        ...

    @abstractmethod
    def try_acquire(self, receiver_id: int, owner_id: str) -> bool:
        ...

    @abstractmethod
    def release(self, receiver_id: int) -> None:
        ...

    @abstractmethod
    def update_heartbeat(self, receiver_id: int) -> None:
        ...

    @abstractmethod
    def get_stale(self, max_age_seconds: int) -> List[Receiver]:
        ...