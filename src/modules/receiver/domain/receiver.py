import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReceiverProps:
    id: str | None
    url: str
    name: str
    enabled: bool
    is_running: bool
    last_started_at: datetime | None
    last_heartbeat: datetime | None
    created_at: datetime
    updated_at: datetime


class Receiver:
    def __init__(self, props: ReceiverProps):
        id = ''
        if props.id:
            id = props.id
        else:
            id = str(uuid.uuid4())
        self.id = id
        self.url = props.url
        self.name = props.name
        self.enabled = props.enabled
        self.is_running = props.is_running
        self.last_started_at = props.last_started_at
        self.last_heartbeat = props.last_heartbeat
        self.created_at = props.created_at
        self.updated_at = props.updated_at