FROM nvidia/cuda:12.0.1-base-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH=/opt/conda/bin:$PATH

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
COPY . /app

RUN apt-get update && apt-get install -y \
    python3.10 python3-pip python3-dev \
    git wget curl \
    libnvidia-compute-515 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

RUN pip install --upgrade pip && \
	pip install --no-cache-dir --upgrade -r /app/requirements.txt

CMD ["fastapi", "run", "main.py", "--port", "80"]

