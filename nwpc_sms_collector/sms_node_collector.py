# coding: utf-8
import datetime
import json
import subprocess

import click

from nwpc_workflow_model.sms.sms_node import SmsNode


def get_cdp_output(cdp_command_string):
    echo_pipe = subprocess.Popen(
        ['echo', cdp_command_string],
        stdout=subprocess.PIPE,
        encoding='utf-8'
    )
    cdp_pipe = subprocess.Popen(
        ['/cma/u/app/sms/bin/cdp'],
        stdin=echo_pipe.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8'
    )
    echo_pipe.stdout.close()
    (cdp_output, cdp_error) = cdp_pipe.communicate()
    return cdp_output, cdp_error


@click.group()
def cli():
    pass


@cli.command('variable')
@click.option('--owner', type=str, help='owner', required=True)
@click.option('--repo', type=str, help='repo', required=True)
@click.option('--sms-server', type=str, help='sms server', required=True)
@click.option('--sms-user', type=str, help='sms user', required=True)
@click.option('--sms-password', type=str, help='sms password')
@click.option('--node-path', type=str, help='node path', required=True)
def get_variable(owner, repo, sms_server, sms_user, sms_password, node_path):
    request_date_time = datetime.datetime.utcnow()
    request_time_string = request_date_time.strftime("%Y-%m-%d %H:%M:%S")

    command_string = "login {sms_server} {sms_user} {sms_password}; info -v {node_path};exit".format(
        sms_server=sms_server,
        sms_user=sms_user,
        sms_password=sms_password,
        node_path=node_path
    )
    (cdp_output, cdp_error) = get_cdp_output(command_string)

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
