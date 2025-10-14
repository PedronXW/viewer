#!/bin/bash
# Ativa a venv
source /venv/bin/activate

# Roda o Flask
flask --app app run --host=0.0.0.0 --port=8000 --debug