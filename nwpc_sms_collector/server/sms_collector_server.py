# coding: utf-8
from concurrent import futures
import time
import logging
import json

import click
import grpc

from nwpc_sms_collector.sms_status_collector import collect_status
from nwpc_sms_collector.sms_node_collector import collect_variable
from nwpc_sms_collector.server.proto import sms_collector_pb2_grpc, sms_collector_pb2

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='[%Y-%m-%d %H:%M:%S]',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class SmsCollectorService(sms_collector_pb2_grpc.SmsCollectorServicer):
    def __init__(self, cdp_path):
        self.cdp_path = cdp_path

    def CollectStatus(self, request, context):
        owner = request.owner
        repo = request.repo
        sms_host = request.sms_host
        sms_prog = request.sms_prog
        sms_name = request.sms_name
        sms_user = request.sms_user
        sms_password = request.sms_password
        post_url = request.post_url
        content_encoding = request.content_encoding
        disable_post = request.disable_post
        verbose = request.verbose

        logger.info('CollectStatus: {owner}/{repo}...'.format(owner=owner, repo=repo))
        collect_status(
            owner, repo, sms_host, sms_prog, sms_name, sms_user, sms_password, self.cdp_path,
            disable_post, post_url, content_encoding, verbose
        )
        logger.info('CollectStatus: {owner}/{repo}...done'.format(owner=owner, repo=repo))

        return sms_collector_pb2.Response(
            status="ok"
        )

    def CollectVariable(self, request, context):
        owner = request.owner
        repo = request.repo
        sms_host = request.sms_host
        sms_prog = request.sms_prog
        sms_user = request.sms_user
        sms_password = request.sms_password
        node_path = request.node_path
        verbose = request.verbose

        logger.info('CollectVariable: {owner}/{repo} {node_path}...'.format(
            owner=owner, repo=repo, node_path=node_path))
        result = collect_variable(
            self.cdp_path, owner, repo,
            sms_host, sms_prog, sms_user, sms_password, node_path, verbose
        )
        logger.info('CollectVariable: {owner}/{repo} {node_path}...done'.format(
            owner=owner, repo=repo, node_path=node_path))

        return sms_collector_pb2.Response(
            status="ok",
            result=json.dumps(result)
        )


@click.command()
@click.option('-t', '--rpc-target', help='rpc-target', default="[::]:50051")
@click.option('-n', '--workers-num', help='max workers number', default=5, type=int)
@click.option('--cdp-path', help="cdp path")
def serve(rpc_target, workers_num, cdp_path):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers_num))
    sms_collector_pb2_grpc.add_SmsCollectorServicer_to_server(
        SmsCollectorService(cdp_path), server)
    server.add_insecure_port('{rpc_target}'.format(rpc_target=rpc_target))
    logger.info('listening on {rpc_target}'.format(rpc_target=rpc_target))
    logger.info('starting server...')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logger.info('warm stop...')
        server.stop(0)
        logger.info('warm stop...done')


if __name__ == "__main__":
    serve()
