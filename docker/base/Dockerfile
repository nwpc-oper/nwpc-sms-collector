FROM nwpc/sms

LABEL maintainer="perillaroc@gmail.com"

COPY . /srv/nwpc-system-collector/

RUN set -ex \
    && cd /srv \
    && cd ./nwpc-system-collector/vendor/nwpc-workflow-model \
    && pip install . \
    && cd /srv \
    && rm -rf /srv/nwpc-system-collector/nwpc-sms-collector/docker \
    && cp -r /srv/nwpc-system-collector/nwpc-sms-collector . \
    && rm -rf /srv/nwpc-system-collector \
    && cd /srv/nwpc-sms-collector \
    && pip install .

WORKDIR /srv/nwpc-sms-collector/nwpc_sms_collector

ENTRYPOINT ["python3"]
