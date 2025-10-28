from datetime import datetime, timedelta

from modules.receiver.domain.ports.repository.receiver import \
    ReceiverRepositoryAbstract
from modules.receiver.domain.receiver import Receiver, ReceiverProps
from modules.receiver.infra.ports.repositories.database import db


class ReceiverModel(db.Model):
    __tablename__ = 'receivers'
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    is_running = db.Column(db.Boolean, default=False)
    last_started_at = db.Column(db.DateTime, nullable=True)
    last_heartbeat = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReceiverRepository(ReceiverRepositoryAbstract):
    def get_all(self):
        rows = ReceiverModel.query.all()
        return [Receiver(r) for r in rows]

    def get_enabled(self):
        rows = ReceiverModel.query.filter_by(enabled=True).all()
        return [Receiver(r) for r in rows]

    def get_by_id(self, receiver_id: int):
        r = ReceiverModel.query.get(receiver_id)
        return Receiver(r) if r else None

    def create(self, props: Receiver):
        r = ReceiverModel(
            id=props.id,
            name=props.name,
            url=props.url,
            enabled=props.enabled,
            is_running=props.is_running,
            last_started_at=props.last_started_at,
            last_heartbeat=props.last_heartbeat,
            created_at=props.created_at,
            updated_at=props.updated_at,
        )
        db.session.add(r)
        db.session.commit()
        return Receiver(r)

    def update(self, receiver: Receiver):
        r = ReceiverModel.query.get(receiver.id)
        if not r:
            return
        r.name = receiver.name
        r.url = receiver.url
        r.enabled = receiver.enabled
        r.is_running = receiver.is_running
        r.owner_id = receiver.owner_id
        r.updated_at = datetime.utcnow()
        db.session.commit()

    def try_acquire(self, receiver_id: int, owner_id: str) -> bool:
        """Marca o receiver como em execução, se ele estiver habilitado e livre."""
        r = ReceiverModel.query.get(receiver_id)
        if not r or not r.enabled or r.is_running:
            return False

        r.is_running = True
        r.owner_id = owner_id
        r.last_started_at = datetime.utcnow()
        r.last_heartbeat = datetime.utcnow()
        db.session.commit()
        return True

    def release(self, receiver_id: int):
        r = ReceiverModel.query.get(receiver_id)
        if not r:
            return
        r.is_running = False
        r.owner_id = None
        db.session.commit()

    def update_heartbeat(self, receiver_id: int):
        r = ReceiverModel.query.get(receiver_id)
        if not r:
            return
        r.last_heartbeat = datetime.utcnow()
        db.session.commit()

    def get_stale(self, max_age_seconds: int):
        cutoff = datetime.utcnow() - timedelta(seconds=max_age_seconds)
        rows = ReceiverModel.query.filter(
            ReceiverModel.is_running == True,
            ReceiverModel.last_heartbeat < cutoff
        ).all()
        return [Receiver(r) for r in rows]