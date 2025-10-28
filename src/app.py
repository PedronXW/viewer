import threading

from flask import Flask, jsonify, request

from modules.analyzer.infra.adapters.queue.new_frame import \
    NewFrameQueueReceiver
from modules.receiver.domain.manager import ReceiverManager
from modules.receiver.infra.adapters.http.receiver.create import \
    CreateReceiverController
from modules.receiver.infra.adapters.http.receiver.disable import \
    DisableReceiverController
from modules.receiver.infra.adapters.http.receiver.enable import \
    EnableReceiverController
from modules.receiver.infra.adapters.http.receiver.list import \
    ListReceiversController
from modules.receiver.infra.adapters.http.receiver.start import \
    StartReceiverController
from modules.receiver.infra.adapters.http.receiver.stop import \
    StopReceiverController
from modules.receiver.infra.ports.repositories.database import db
from modules.receiver.infra.ports.repositories.receiver.repository import \
    ReceiverRepository
from modules.receiver.services.receiver.create import CreateReceiverService
from modules.receiver.services.receiver.disable import DisableReceiverService
from modules.receiver.services.receiver.enable import EnableReceiverService
from modules.receiver.services.receiver.list import ListReceiversService
from modules.receiver.services.receiver.start import StartReceiverService
from modules.receiver.services.receiver.stop import StopReceiverService

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@db:5432/mydatabase"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()
repository = ReceiverRepository()
manager = ReceiverManager(app, repository)
manager.start_enabled_receivers()


create_service = CreateReceiverService(repository)
list_service = ListReceiversService(repository)
enable_service = EnableReceiverService(repository, manager)
disable_service = DisableReceiverService(repository, manager)
start_service = StartReceiverService(repository, manager)
stop_service = StopReceiverService(repository, manager)

create_controller = CreateReceiverController(create_service)
list_controller = ListReceiversController(list_service)
enable_controller = EnableReceiverController(enable_service)
disable_controller = DisableReceiverController(disable_service)
start_controller = StartReceiverController(start_service)
stop_controller = StopReceiverController(stop_service)

@app.route("/receivers", methods=["GET"])
def list_receivers():
    result = list_controller.handle({})
    return jsonify(result)

@app.route("/receivers", methods=["POST"])
def create_receiver():
    data = request.json or {}
    create_controller.handle(data)
    return jsonify({"status": "created"}), 201

@app.route("/receivers/enable", methods=["POST"])
def enable_receiver():
    data = request.json or {}
    res = enable_controller.handle(data)
    if "error" in res:
        return jsonify(res), 404
    return jsonify(res)

@app.route("/receivers/disable", methods=["POST"])
def disable_receiver():
    data = request.json or {}
    res = disable_controller.handle(data)
    if "error" in res:
        return jsonify(res), 404
    return jsonify(res)

@app.route("/receivers/<receiver_id>/start", methods=["POST"])
def start_receiver(receiver_id):
    res = start_controller.handle({"receiver_id": receiver_id})
    if "error" in res:
        return jsonify(res), 404
    return jsonify(res)

@app.route("/receivers/<receiver_id>/stop", methods=["POST"])
def stop_receiver(receiver_id):
    res = stop_controller.handle({"receiver_id": receiver_id})
    return jsonify(res)


new_frame_receiver = NewFrameQueueReceiver()

threading.Thread(target=new_frame_receiver.receive, daemon=True).start()