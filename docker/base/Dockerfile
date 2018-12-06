FROM nwpcc/sms

LABEL maintainer="perillaroc@gmail.com"

COPY nwpc-sms-collector /srv/nwpc-sms-collector/
COPY vendor /srv/vendor/

RUN set -ex \
    && cd /srv/vendor/nwpc-workflow-model \
    && pip install . \
    && cd /srv/nwpc-sms-collector \
    && pip install . \
    && cd /srv \
    && rm -rf vendor

WORKDIR /srv/nwpc-sms-collector/nwpc_sms_collector

ENTRYPOINT ["python3"]
