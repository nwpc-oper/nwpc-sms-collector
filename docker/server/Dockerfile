FROM nwpc/sms-collector:base

LABEL maintainer="perillaroc@gmail.com"

RUN set -ex \
    && cd /srv/nwpc-sms-collector \
    && pip install .[grpc]

WORKDIR /srv/nwpc-sms-collector/nwpc_sms_collector

ENTRYPOINT ["python3", "server/sms_collector_server.py"]

CMD ["--rpc-target=[::]:50051", \
    "--workers-num=5", \
    "--cdp-path=/srv/bin/cdp"]