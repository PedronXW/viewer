FROM python:3.10-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    bash \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* 

# Copia apenas o requirements para cache de build
COPY requirements.txt /app/requirements.txt

# Cria a venv e instala as dependências
RUN python -m venv /venv \
    && /bin/bash -c "source /venv/bin/activate && pip install --upgrade pip && pip install -r /app/requirements.txt"

# Copia o restante do código
COPY . /app

# Script de start
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Define PATH para que binários da venv fiquem disponíveis
ENV PATH="/venv/bin:$PATH"

# Comando padrão
CMD ["/app/start.sh"]