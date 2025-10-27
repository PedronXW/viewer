from modules.receiver.domain.frame import Frame, FrameProps
from modules.receiver.domain.ports.repository.frame import \
    FrameRepositoryAbstract
from modules.receiver.domain.ports.storage import StorageRepositoryAbstract


class CreateFrameService:
    def __init__(self, frame_repository: FrameRepositoryAbstract, storage_repository: StorageRepositoryAbstract):
        self.frame_repository = frame_repository
        self.storage_repository = storage_repository

    async def execute(self, props: FrameProps, frame_data:any) -> None:
        print(f"[CreateFrameService] Executing frame creation for receiver {props.receiver_id}")
        frame = Frame(props)
        print(f"[Frame] Creating frame {frame.id} for receiver {frame.receiver_id}")
        await self.storage_repository.save(frame_data, frame.id)
        await self.frame_repository.add(frame)
        print(f"[Frame] Saved frame {frame.id} for receiver {frame.receiver_id}")
        