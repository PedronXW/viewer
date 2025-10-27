from src.modules.receiver.domain.receiver import ReceiverProps
from src.modules.receiver.services.receiver.create import CreateReceiverService


class CreateReceiverController:
    def __init__(self, create_receiver_service: CreateReceiverService):
        self.create_receiver_service = create_receiver_service
        
    def handle(self, request: dict) -> None:
        props = ReceiverProps(**request)
        self.create_receiver_service.execute(props)