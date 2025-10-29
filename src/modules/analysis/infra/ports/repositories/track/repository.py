from modules.receiver.domain.ports.repository.track import \
    TrackRepositoryAbstract
from modules.receiver.domain.track import Track, TrackProps
from modules.receiver.infra.ports.repositories.database import db


class TrackModel(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.String(255), primary_key=True)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class TrackRepository(TrackRepositoryAbstract):
    async def add(self, track: Track) -> None:
        track_model = TrackModel(
            id=track.id,
            updated_at=track.updated_at,
            created_at=track.created_at
        )
        db.session.add(track_model)
        db.session.commit()