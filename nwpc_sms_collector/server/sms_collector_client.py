# coding: utf-8
import grpc
import click

from nwpc_sms_collector.server.proto import sms_collector_pb2, sms_collector_pb2_grpc


@click.group()
def cli():
    pass


@cli.command()
@click.option('--rpc-target', help='rpc target')
@click.option("-o", "--owner", help="owner name, default is same as sms server user name")
@click.option("-r", "--repo", help="repo name, default is same as sms server name")
@click.option("--sms-host", help="sms host", required=True)
@click.option("--sms-prog", help="sms prog", required=True)
@click.option("--sms-name", help="sms server name", required=True)
@click.option("--sms-user", help="sms server user name", required=True)
@click.option("--sms-password", default='1',
              help="sms server password, default is {default_sms_password}".format(
                default_sms_password='1'))
@click.option("--disable-post", is_flag=True, default=False, help="disable post to agent.")
@click.option('--post-url', help='post URL')
@click.option('--gzip', 'content_encoding', flag_value='gzip', help='use gzip to post data.')
@click.option("--verbose", is_flag=True, default=False, help="show more outputs")
def status(rpc_target, owner, repo,
           sms_host, sms_prog, sms_name, sms_user, sms_password,
           disable_post, post_url, content_encoding, verbose):
    status_request = sms_collector_pb2.StatusRequest(
        owner=owner,
        repo=repo,
        sms_host=sms_host,
        sms_prog=sms_prog,
        sms_name=sms_name,
        sms_user=sms_user,
        sms_password=sms_password,
        disable_post=disable_post,
        post_url=post_url,
        content_encoding=content_encoding,
        verbose=verbose
    )

    with grpc.insecure_channel(rpc_target) as channel:
        stub = sms_collector_pb2_grpc.SmsCollectorStub(channel)
        response = stub.CollectStatus(status_request)
        print(response.status)

    return


@cli.command()
@click.option('--rpc-target', help='rpc target')
@click.option("-o", "--owner", help="owner name, default is same as sms server user name")
@click.option("-r", "--repo", help="repo name, default is same as sms server name")
@click.option("--sms-host", help="sms host", required=True)
@click.option("--sms-prog", help="sms prog", required=True)
@click.option("--sms-name", help="sms server name", required=True)
@click.option("--sms-user", help="sms server user name", required=True)
@click.option("--sms-password", default='1',
              help="sms server password, default is {default_sms_password}".format(
                default_sms_password='1'))
@click.option("--node-path", required=True, help="node path")
@click.option("--verbose", is_flag=True, default=False, help="show more outputs")
def variable(rpc_target, owner, repo,
             sms_host, sms_prog, sms_name, sms_user, sms_password,
             node_path, verbose):
    status_request = sms_collector_pb2.VariableRequest(
        owner=owner,
        repo=repo,
        sms_host=sms_host,
        sms_prog=sms_prog,
        sms_name=sms_name,
        sms_user=sms_user,
        sms_password=sms_password,
        node_path=node_path,
        verbose=verbose
    )

    with grpc.insecure_channel(rpc_target) as channel:
        stub = sms_collector_pb2_grpc.SmsCollectorStub(channel)
        response = stub.CollectVariable(status_request)
        print(response.result)

    return



if __name__ == "__main__":
    cli()
