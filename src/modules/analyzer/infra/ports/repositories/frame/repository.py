from modules.receiver.domain.frame import Frame, FrameProps
from modules.receiver.domain.ports.repository.frame import \
    FrameRepositoryAbstract
from modules.receiver.infra.ports.repositories.database import db


class FrameModel(db.Model):
    __tablename__ = 'frames'
    id = db.Column(db.String(255), primary_key=True)
    receiver_id = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

class FrameRepository(FrameRepositoryAbstract):
    async def add(self, frame: Frame) -> None:
        frame_model = FrameModel(
            id=frame.id,
            receiver_id=frame.receiver_id,
            timestamp=frame.timestamp
        )
        db.session.add(frame_model)
        db.session.commit()

    async def remove(self, frame: Frame) -> None:
        frame_model = FrameModel.query.get(frame.id)
        if frame_model:
            db.session.delete(frame_model)
            db.session.commit()
                 
    async def get_by_id(self, frame_id: str) -> Frame | None:
        frame_model = FrameModel.query.get(frame_id)
        if frame_model:
            return Frame(
                props=FrameProps(
                    id=frame_model.id,
                    receiver_id=frame_model.receiver_id,
                    timestamp=frame_model.timestamp
                )
            )
        return None