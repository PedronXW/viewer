from src.modules.receiver.domain.ports.repository.frame import \
    FrameRepositoryAbstract
from src.modules.receiver.domain.ports.storage import StorageAbstractClass


class GetFrameService:
    def __init__(self, frame_repository: FrameRepositoryAbstract,
                 storage_port: StorageAbstractClass):
        self.frame_repository = frame_repository
        self.storage_port = storage_port

    async def execute(self, frame_id: int) -> dict:
        frame = await self.frame_repository.get_by_id(frame_id)
        if not frame:
            raise ValueError("Frame not found")

        storage_data = await self.storage_port.get(identifier=str(frame.id))
        return {
            "frame": frame,
            "storage_data": storage_data
        }