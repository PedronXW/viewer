from modules.receiver.services.receiver.disable import DisableReceiverService


class DisableReceiverController:
    def __init__(self, disable_receiver_service: DisableReceiverService):
        self.disable_receiver_service = disable_receiver_service

    def handle(self, request: dict):
        receiver_id = request.get("receiver_id")
        receiver = self.disable_receiver_service.execute(receiver_id)
        if not receiver:
            return {"error": "not found"}, 404
        return {"status": "disabled"}