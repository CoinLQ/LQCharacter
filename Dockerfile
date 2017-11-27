FROM python:3.6
ENV PYTHONUNBUFFERED 1

LABEL maintainer="kangqiao <kangqiao610@gmail.com>"

ADD ./requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com \
    #&& pip install git+https://github.com/sshwsfc/xadmin.git \
    && pip install https://github.com/CoinLQ/xadmin/archive/master.zip \
    && pip install https://github.com/CoinLQ/db_file_storage/archive/master.zip \
    && pip install uwsgi -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com  \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 8001

WORKDIR /LQCharacter
