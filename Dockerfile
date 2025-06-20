FROM python:3.10

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    python3-dev \
    libboost-all-dev \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    ffmpeg \
    libsm6 \
    libgl1-mesa-glx \
    pkg-config

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["streamlit", "run", "app.py"] 