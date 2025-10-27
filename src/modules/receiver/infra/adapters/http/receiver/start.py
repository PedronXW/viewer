from modules.receiver.services.receiver.start import StartReceiverService


class StartReceiverController:
    def __init__(self, start_receiver_service: StartReceiverService):
        self.start_receiver_service = start_receiver_service

    def handle(self, request: dict):
        receiver_id = request.get("receiver_id")
        started = self.start_receiver_service.execute(receiver_id)
        if started is None:
            return {"error": "not found"}, 404
        return {"started": started}