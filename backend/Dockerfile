FROM python:3.12

RUN apt-get update && apt-get install -y \
    gfortran \
    build-essential \
    liblapack-dev \
    libopenblas-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 10000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
