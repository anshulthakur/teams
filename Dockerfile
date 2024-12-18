FROM python:3.12
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt .
RUN apt update
RUN apt install build-essential wget -y
RUN apt-get install build-essential python3-dev libldap2-dev libsasl2-dev -y
RUN pip3 install --no-cache-dir -r requirements.txt