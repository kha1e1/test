FROM python:3.9-slim
WORKDIR /src/app
ENV TZ=Asia/Almaty

COPY requirements.txt /src/app
RUN pip install -r /src/app/requirements.txt
COPY . /src/app
