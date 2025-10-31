FROM python:3.10-slim

WORKDIR /app

# Instala dependências do sistema necessárias para compilar o ByteTrack e rodar OpenCV
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    bash \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copia o requirements primeiro (para aproveitar cache)
COPY requirements.txt /app/requirements.txt

# Cria a venv e instala o PyTorch antes do restante
RUN python -m venv /venv \
    && /bin/bash -c "source /venv/bin/activate && pip install --upgrade pip \
    && pip install --no-cache-dir torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 torchreid==0.2.5 --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir loguru cython pycocotools opencv-python \
    && pip install --no-cache-dir --no-build-isolation -r /app/requirements.txt \
    && pip install --no-cache-dir --no-build-isolation git+https://github.com/ifzhang/ByteTrack.git"

# Copia o restante do código
COPY . /app

# Script de start
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENV PYTHONPATH=/app/src

# Define PATH para usar a venv por padrão
ENV PATH="/venv/bin:$PATH"

# Comando padrão
CMD ["/app/start.sh"]