from src.modules.receiver.services.frame.get import GetFrameService


class GetFrameController:
    def __init__(self, get_frame_service: GetFrameService):
        self.get_frame_service = get_frame_service

    async def handle(self, request: dict) -> dict:
        frame_id = request.get("id")
        frame = await self.get_frame_service.execute(frame_id)
        return {"frame": frame}