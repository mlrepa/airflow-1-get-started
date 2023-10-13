FROM ghcr.io/mlflow/mlflow:v2.0.1

RUN apt-get update && \
    apt-get install -y apt-transport-https build-essential cmake curl gcc g++ git tree sudo unzip wget

ARG USER_ID="1000"
ENV USER_ID=${USER_ID}

RUN useradd -m user -u ${USER_ID} && \
    echo 'user:user' | chpasswd user && \
    echo "user ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/user && \
    chmod 0440 /etc/sudoers.d/user && \
    chown -R user /home

USER user

WORKDIR /home/user

CMD mlflow ui --host 0.0.0.0 --port 5000
