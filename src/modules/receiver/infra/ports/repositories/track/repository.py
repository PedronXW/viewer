from modules.receiver.domain.ports.repository.track import \
    TrackRepositoryAbstract
from modules.receiver.domain.track import Track, TrackProps
from modules.receiver.infra.ports.repositories.database import db


class TrackModel(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.String(255), primary_key=True)
    track_id = db.Column(db.String(255), unique=True, nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class TrackRepository(TrackRepositoryAbstract):
    def add(self, track: Track) -> None:
        track_model = TrackModel(
            id=track.id,
            track_id=track.track_id,
            updated_at=track.updated_at,
            created_at=track.created_at
        )
        db.session.add(track_model)
        db.session.commit()
        
    async def get(self, track_id: str) -> Track | None:
        track_model = TrackModel.query.filter_by(track_id=track_id).first()
        if track_model:
            return Track(props=TrackProps(
                id=track_model.id,
                track_id=track_model.track_id,
                updated_at=track_model.updated_at,
                created_at=track_model.created_at
            ))
        return None