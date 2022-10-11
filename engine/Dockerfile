FROM ubuntu:20.04
WORKDIR /opt/social_net
COPY ./sql.py /opt/social_net
COPY ./wait_for_mysql.sh /opt/social_net
RUN apt -y update
RUN apt -y install apt-utils
RUN apt -y install python3.8 python3-pip mysql-client libmysqlclient-dev
RUN apt -y upgrade
RUN pip3 install mysql-connector-python-rf
RUN pip3 install mysql-connector-python
