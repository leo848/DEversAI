FROM nvidia/cuda:12.0.1-base-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH=/opt/conda/bin:$PATH

RUN apt-get update && apt-get install -y \
    python3.10 python3-pip python3-dev \
    git wget curl \
    libnvidia-compute-515 \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

WORKDIR /workspace

RUN pip install --upgrade pip && \
    pip install \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
    pip install \
    diffusers transformers accelerate \
    Pillow alive-progress tensorboard \
    matplotlib pacmap scipy numpy \
    bracex


COPY . /workspace

CMD ["/bin/bash"]

