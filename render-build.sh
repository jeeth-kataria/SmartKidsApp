#!/usr/bin/env bash
set -e

apt-get update && apt-get install -y \
    cmake \
    build-essential \
    python3-dev \
    libboost-all-dev \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libatlas-base-dev

pip install -r requirements.txt 