from modules.receiver.services.receiver.enable import EnableReceiverService


class EnableReceiverController:
    def __init__(self, enable_receiver_service: EnableReceiverService):
        self.enable_receiver_service = enable_receiver_service

    def handle(self, request: dict):
        receiver_id = request.get("receiver_id")
        receiver = self.enable_receiver_service.execute(receiver_id)
        if not receiver:
            return {"error": "not found"}, 404
        return {"status": "enabled"}