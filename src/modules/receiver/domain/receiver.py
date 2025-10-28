import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReceiverProps:
    url: str
    name: str
    id: str | None = None
    enabled: bool | None = True
    is_running: bool | None = False
    last_started_at: datetime | None = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime | None = field(default_factory=datetime.utcnow)
    created_at: datetime | None = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = field(default_factory=datetime.utcnow)


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
        self.enabled = props.enabled or False
        self.is_running = props.is_running or True
        self.last_started_at = props.last_started_at
        self.last_heartbeat = props.last_heartbeat
        self.created_at = props.created_at or datetime.utcnow()
        self.updated_at = props.updated_at or datetime.utcnow()