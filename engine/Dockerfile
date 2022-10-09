FROM python:3
WORKDIR /opt/social_net
COPY ./sql.py /opt/social_net
WORKDIR /opt/social_net
RUN pip3 install mysql-connector-python-rf
RUN python3 sql.py
