FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ncbi-blast+ \
    hmmer \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# EggNOG-mapper
RUN wget https://github.com/eggnogdb/eggnog-mapper/releases/download/2.1.12/emapper-2.1.12.tar.gz && \
    tar -xzf emapper-2.1.12.tar.gz && \
    mv emapper-2.1.12 /usr/local/eggnog && \
    ln -s /usr/local/eggnog/emapper.py /usr/local/bin/emapper.py

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# variável fornecida pelo Railway
ENV API_KEY=${API_KEY}

COPY app ./app
COPY data ./data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
