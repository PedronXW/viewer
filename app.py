from flask import Flask, jsonify

from utils.initial import process_frames

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    process_frames()
    return jsonify({"message": "Arroz"}), 200