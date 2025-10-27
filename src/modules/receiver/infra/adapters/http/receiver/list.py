from modules.receiver.services.receiver.list import ListReceiversService


class ListReceiversController:
    def __init__(self, list_receiver_service: ListReceiversService):
        self.list_receiver_service = list_receiver_service

    def handle(self, request: dict):
        receivers = self.list_receiver_service.execute()
        result = []
        for r in receivers:
            result.append({
                "id": r.id,
                "name": r.name,
                "url": r.url,
                "enabled": r.enabled,
                "is_running": r.is_running,
                "owner_id": r.owner_id,
                "last_started_at": r.last_started_at.isoformat() if r.last_started_at else None,
                "last_heartbeat": r.last_heartbeat.isoformat() if r.last_heartbeat else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            })
        return result