from src.modules.receiver.services.receiver.get import GetReceiverService


class GetReceiverController:
    def __init__(self, get_receiver_service: GetReceiverService):
        self.get_receiver_service = get_receiver_service

    def handle(self, request: dict) -> dict:
        receiver_id = request.get("id")
        receiver = self.get_receiver_service.execute(receiver_id)
        return {"receiver": receiver}