import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TrackProps:
    id : str | None = None
    track_id: str | None = None
    created_at: datetime | None = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = field(default_factory=datetime.utcnow)

class Track:
    def __init__(self, props: TrackProps):
        id = ''
        if props.id:
            id = props.id
        else:
            id = str(uuid.uuid4())
        self.id = id
        self.track_id = props.track_id
        self.created_at = props.created_at or datetime.utcnow()
        self.updated_at = props.updated_at or datetime.utcnow()