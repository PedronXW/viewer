from modules.receiver.domain.frame import Frame, FrameProps
from modules.receiver.domain.ports.repository.frame import \
    FrameRepositoryAbstract
from modules.receiver.domain.ports.storage import StorageRepositoryAbstract


class CreateFrameService:
    def __init__(self, frame_repository: FrameRepositoryAbstract, storage_repository: StorageRepositoryAbstract):
        self.frame_repository = frame_repository
        self.storage_repository = storage_repository

    async def execute(self, props: FrameProps, frame_data:any) -> Frame:
        frame = Frame(props)
        await self.storage_repository.save(frame_data, frame.id)
        await self.frame_repository.add(frame)
        return frame
        