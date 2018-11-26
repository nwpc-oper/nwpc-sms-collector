# coding: utf-8
import datetime
import json

import click

from nwpc_sms_collector.sms_util import get_cdp_output
from nwpc_workflow_model.sms.sms_node import SmsNode


@click.group()
def cli():
    pass


@cli.command('variable')
@click.option('-o', '--owner', type=str, help='owner', required=True)
@click.option('-r', '--repo', type=str, help='repo', required=True)
@click.option("--sms-host", help="sms host", required=True)
@click.option("--sms-prog", help="sms prog", required=True)
@click.option('--sms-user', type=str, help='sms user', required=True)
@click.option('--sms-password', type=str, default='1', help='sms password')
@click.option('--node-path', type=str, help='node path', required=True)
@click.option("--cdp-path", help="cdp path", required=True)
def get_variable(owner, repo, sms_host, sms_prog, sms_user, sms_password, node_path, cdp_path):
    request_date_time = datetime.datetime.utcnow()
    request_time_string = request_date_time.strftime("%Y-%m-%d %H:%M:%S")

    command_string = "info -v {node_path};exit".format(node_path=node_path)
    return_code, cdp_output, cdp_error = get_cdp_output(
        cdp_path, sms_host, sms_prog, sms_user, sms_password, command_string)

    cdp_output = cdp_output.splitlines(keepends=True)
    node = SmsNode.create_from_cdp_info_output(cdp_output)

    current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).isoformat()  # 北京时间
    if node is None:
        result = {
            'app': 'sms_node_collector',
            'type': 'node_collector',
            'time': current_time,
            'error': 'variable-handler-error',
            'data': {
                'owner': owner,
                'repo': repo,
                'request': {
                    'command': 'variable',
                    'arguments': [],
                    'time': request_time_string
                },
                'response': {
                    'message': {
                        'output': cdp_output,
                        'error_output': cdp_error
                    },
                    'time': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
        print(json.dumps(result, indent=2))
    else:
        result = {
            'app': 'sms_node_collector',
            'type': 'node_collector',
            'time': current_time,
            'data': {
                'owner': owner,
                'repo': repo,
                'request': {
                    'command': 'variable',
                    'arguments': [],
                    'time': request_time_string
                },
                'response': {
                    'node': node.to_dict(),
                    'time': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
        print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    cli()
