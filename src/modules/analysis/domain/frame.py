

import datetime
import uuid
from dataclasses import dataclass


@dataclass
class FrameProps:
    id: str | None
    track_id: str | None
    receiver_id: str
    timestamp: datetime
    
class Frame:
    def __init__(self, props: FrameProps):
        id =''
        if props.id:
            id = props.id
        else:
            id = str(uuid.uuid4())
        self.track_id = props.track_id
        self.receiver_id = props.receiver_id
        self.timestamp = props.timestamp
        self.id = id
        