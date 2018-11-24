# coding=utf-8
import json
import gzip
import logging

import click
import requests

from nwpc_sms_collector.sms_util import get_sms_whole_status


default_sms_password = 1


@click.group()
def cli():
    """
    DESCRIPTION
        Get sms suites' status.
    """
    pass


@cli.command('collect')
@click.option("-o", "--owner", help="owner name, default is same as sms server user name")
@click.option("-r", "--repo", help="repo name, default is same as sms server name")
@click.option("-n", "--sms-name", help="sms server name", required=True)
@click.option("-u", "--sms-user", help="sms server user name", required=True)
@click.option("-p", "--sms-password", default=default_sms_password,
              help="sms server password, default is {default_sms_password}".format(
                default_sms_password=default_sms_password))
@click.option("--disable-post", is_flag=True, default=False, help="disable post to agent.")
@click.option('--post-url', help='post URL')
@click.option('--gzip', 'content_encoding', flag_value='gzip', help='use gzip to post data.')
@click.option("--verbose", is_flag=True, default=False, help="show more outputs")
def collect_handler(owner, repo, sms_name, sms_user, sms_password,
                    disable_post, post_url, content_encoding, verbose):
    click.echo('Getting sms status for {owner}/{repo}'.format(owner=owner, repo=repo))
    result = get_sms_whole_status(owner, repo, sms_name, sms_user, sms_password, verbose)
    click.echo('Getting sms status for {owner}/{repo}...Done'.format(owner=owner, repo=repo))

    post_data = {
        'message': json.dumps(result)
    }

    if verbose:
        if 'error' in result:
            click.echo(result)
        else:
            click.echo("""result:
    app: {app},
    type: {type},
    timestamp: {timestamp},
    data: ...
""".format(
                app=result['app'],
                type=result['type'],
                timestamp=result['timestamp']))

    if not disable_post:
        if len(post_url) == 0:
            click.echo("Please set post url")
            return

        if verbose:
            click.echo("Posting sms status for {owner}/{repo}...".format(owner=owner, repo=repo))

        url = post_url.format(
            owner=owner,
            repo=repo
        )

        if content_encoding == 'gzip':
            gzipped_data = gzip.compress(bytes(json.dumps(post_data), 'utf-8'))

            requests.post(post_url, data=gzipped_data, headers={
                'content-encoding': 'gzip'
            })
        else:
            requests.post(url, data=post_data)

        if verbose:
            click.echo("Posting sms status for {owner}/{repo}...done".format(owner=owner, repo=repo))


@cli.command("show")
@click.option("-o", "--owner", help="owner name, default is same as sms server user name")
@click.option("-r", "--repo", help="repo name, default is same as sms server name")
@click.option("-n", "--sms-name", help="sms server name", required=True)
@click.option("-u", "--sms-user", help="sms server user name", required=True)
@click.option("-p", "--sms-password", help="sms server password, default is {default_sms_password}".format(
            default_sms_password=default_sms_password))
def show_handler(owner, repo, sms_name, sms_user, sms_password, verbose):
    result = get_sms_whole_status(owner, repo, sms_name, sms_user, sms_password, verbose=False)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    cli()
