from modules.receiver.services.receiver.stop import StopReceiverService


class StopReceiverController:
    def __init__(self, stop_receiver_service: StopReceiverService):
        self.stop_receiver_service = stop_receiver_service

    def handle(self, request: dict):
        receiver_id = request.get("receiver_id")
        stopped = self.stop_receiver_service.execute(receiver_id)
        return {"stopped": stopped}