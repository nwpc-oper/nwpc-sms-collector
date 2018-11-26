FROM python:3

LABEL maintainer="perillaroc@gmail.com"

RUN set -ex \
    && apt update \
    && apt install unzip

COPY . /srv/nwpc-system-collector/

RUN set -ex \
    && cd /srv/nwpc-system-collector/nwpc-sms-collector/docker/base \
    && unzip sms-client.zip \
    && cd sms-client \
    && make linux \
    && cp ./bin/cdp /srv/cdp \
    && cd /srv \
    && cd ./nwpc-system-collector/vendor/nwpc-workflow-model \
    && pip install . \
    && cd /srv \
    && rm -rf /srv/nwpc-system-collector/nwpc-sms-collector/docker \
    && cp -r /srv/nwpc-system-collector/nwpc-sms-collector . \
    && rm -rf /srv/nwpc-system-collector \
    && cd /srv/nwpc-sms-collector \
    && pip install .

WORKDIR /srv/nwpc-sms-collector

ENTRYPOINT ["python3"]
