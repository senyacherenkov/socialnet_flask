FROM ubuntu:20.04

RUN apt -y update
RUN apt -y install -y --no-install-recommends \
    apt-utils \
    python3 \
    python3-pip \
    mysql-client \
    libmysqlclient-dev
RUN pip3 install mysql-connector-python   
RUN pip3 install flask

WORKDIR /opt/social_net
ADD . /opt/social_net

ENV FLASK_APP=__init__
ENV FLASK_ENV=development
ENV PYTHONPATH='.'
RUN flask run
