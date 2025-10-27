import threading
import time
import uuid

from flask import Flask, jsonify, request

from modules.receiver.domain.receiver import Receiver
from modules.receiver.infra.ports.queues.client import queue_url, sqs
from modules.receiver.infra.ports.repositories.database import db
from modules.receiver.infra.ports.repositories.receiver.repository import (
    ReceiverModel, ReceiverRepository)
from modules.receiver.services.receiver.receiver_manager import ReceiverManager

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@db:5432/mydatabase"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# repository + manager
repository = ReceiverRepository()
manager = ReceiverManager(app, repository)
# start enabled receivers at startup
manager.start_enabled_receivers()

# controllers (endpoints)
@app.route("/receivers", methods=["GET"])
def list_receivers():
    rows = ReceiverModel.query.all()
    def row_to_dict(r):
        return {
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
        }
    return jsonify([row_to_dict(r) for r in rows])

@app.route("/receivers", methods=["POST"])
def create_receiver():
    data = request.json or {}
    url = data.get("url")
    name = data.get("name")
    if not url:
        return jsonify({"error": "url required"}), 400
    r = ReceiverModel(id=str(uuid.uuid4()), name=name, url=url, enabled=True)
    db.session.add(r)
    db.session.commit()
    # auto-start
    
    domain_r = Receiver(r)
    manager.start_receiver(domain_r)
    return jsonify({"id": r.id}), 201

@app.route("/receivers/<int:receiver_id>/enable", methods=["POST"])
def enable_receiver(receiver_id):
    r = ReceiverModel.query.get(receiver_id)
    if not r:
        return jsonify({"error": "not found"}), 404
    r.enabled = True
    db.session.commit()
    manager.start_receiver(Receiver(r))
    return jsonify({"status": "enabled"})

@app.route("/receivers/<int:receiver_id>/disable", methods=["POST"])
def disable_receiver(receiver_id):
    r = ReceiverModel.query.get(receiver_id)
    if not r:
        return jsonify({"error": "not found"}), 404
    r.enabled = False
    db.session.commit()
    manager.stop_receiver(receiver_id)
    return jsonify({"status": "disabled"})

@app.route("/receivers/<int:receiver_id>/start", methods=["POST"])
def start_receiver_manual(receiver_id):
    r = ReceiverModel.query.get(receiver_id)
    if not r:
        return jsonify({"error": "not found"}), 404

    ok = manager.start_receiver(Receiver(r))
    return jsonify({"started": ok})

@app.route("/receivers/<int:receiver_id>/stop", methods=["POST"])
def stop_receiver_manual(receiver_id):
    ok = manager.stop_receiver(receiver_id)
    return jsonify({"stopped": ok})




def consumer_loop():
    print("[Consumer] Starting SQS consumer loop")
    while True:
        messages = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10
        )
        if "Messages" in messages:
            for msg in messages["Messages"]:
                print("Mensagem recebida:", msg["Body"])
                # Processa mensagem...
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=msg["ReceiptHandle"]
                )
        else:
            time.sleep(1)

# Inicializa thread do consumidor
threading.Thread(target=consumer_loop, daemon=True).start()