FROM nvidia/cuda:11.4.0-cudnn8-runtime-ubuntu20.04


WORKDIR /app
RUN apt-get -y update

RUN apt-get -y install software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get -y update
RUN apt-get -y install python3.8
RUN apt-get -y install python3-pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY commonlib/ ./commonlib
COPY config/ ./config
COPY service_group/ ./service_group
COPY aiServer ./aiServer
COPY proto/ ./proto

ENV INFERENCE_CONFIG_FILE_NAME=default.linux.json5

CMD [ "python3", "./aiServer/main.py" ]

