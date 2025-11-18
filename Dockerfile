FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/local/bin:${PATH}"

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    unzip \
    build-essential \
    hmmer \
    ncbi-blast+ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Instalando DIAMOND (binário oficial) - versão estável aproximada
RUN DIAMOND_VERSION="2.1.8" && \
    wget -q -O diamond.tar.gz "https://github.com/bbuchfink/diamond/releases/download/v${DIAMOND_VERSION}/diamond-linux64.tar.gz" && \
    tar -xzf diamond.tar.gz && \
    if [ -f diamond ]; then \
        mv diamond /usr/local/bin/diamond; \
    elif ls diamond*/diamond 1>/dev/null 2>&1; then \
        mv diamond*/diamond /usr/local/bin/diamond; \
    else \
        echo "diamond binary not found after extraction"; exit 1; \
    fi && \
    chmod +x /usr/local/bin/diamond && \
    rm -rf diamond*

# eggNOG removed intentionally

WORKDIR /app

# Instalar dependências Python da aplicação
COPY requirements.txt /app/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt

# Copiar código da aplicação
COPY app /app/app

# Criar diretório para DBs (será montado como volume no Railway)
RUN mkdir -p /data/databases && chown -R root:root /data/databases

EXPOSE 8000

# Use PORT in runtime if provided, otherwise default 8000
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
