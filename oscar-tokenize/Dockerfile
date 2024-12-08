FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
	curl git python3 python3-pip build-essential

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app
RUN git clone https://github.com/leo848/DEversAI.git .

WORKDIR /app/oscar-tokenize
RUN cargo build --release

CMD ["/bin/bash"]
