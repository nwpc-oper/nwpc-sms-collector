# coding=utf-8
import json
import gzip
import logging
from datetime import datetime

import click
import requests

from nwpc_sms_collector.sms_util import get_sms_status


default_sms_password = 1

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='[%Y-%m-%d %H:%M:%S]',
    level=logging.INFO)

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """
    DESCRIPTION
        Get sms suites' status.
    """
    pass


def collect_status(owner, repo, sms_host, sms_prog, sms_name, sms_user, sms_password, cdp_path,
                   disable_post, post_url, content_encoding, verbose):
    start_time = datetime.utcnow()
    logger.info('[{owner}/{repo}] Fetching sms status...'.format(owner=owner, repo=repo))
    result = get_sms_status(cdp_path,
                            owner, repo,
                            sms_host, sms_prog,
                            sms_name, sms_user, sms_password,
                            verbose)

    fetching_end_time = datetime.utcnow()
    logger.info('[{owner}/{repo}] Fetching sms status...Done. Used {cost}'.format(
        owner=owner, repo=repo, cost=fetching_end_time-start_time))

    post_data = {
        'message': json.dumps(result)
    }

    if verbose:
        if 'error' in result:
            logger.warning(result)
#         else:
#             click.echo("""result:
#     app: {app},
#     type: {type},
#     timestamp: {timestamp},
#     data: ...
# """.format(
#                 app=result['app'],
#                 type=result['type'],
#                 timestamp=result['timestamp']))

    if not disable_post:
        if len(post_url) == 0:
            logger.warning("Please set post url")
            return

        if verbose:
            logger.info("[{owner}/{repo}] Posting sms status...".format(owner=owner, repo=repo))

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
            posting_end_time = datetime.utcnow()
            logger.info("[{owner}/{repo}] Posting sms status...Done. Used {cost}".format(
                owner=owner, repo=repo, cost=posting_end_time-fetching_end_time))

    end_time = datetime.utcnow()
    if verbose:
        logger.info("[{owner}/{repo}] Collect sms status used {cost}".format(
            owner=owner, repo=repo, cost=end_time-fetching_end_time))


@cli.command('collect')
@click.option("-o", "--owner", help="owner name, default is same as sms server user name")
@click.option("-r", "--repo", help="repo name, default is same as sms server name")
@click.option("--sms-host", help="sms host", required=True)
@click.option("--sms-prog", help="sms prog", required=True)
@click.option("-n", "--sms-name", help="sms server name", required=True)
@click.option("-u", "--sms-user", help="sms server user name", required=True)
@click.option("-p", "--sms-password", default=default_sms_password,
              help="sms server password, default is {default_sms_password}".format(
                default_sms_password=default_sms_password))
@click.option("--cdp-path", help="cdp path", required=True)
@click.option("--disable-post", is_flag=True, default=False, help="disable post to agent.")
@click.option('--post-url', help='post URL')
@click.option('--gzip', 'content_encoding', flag_value='gzip', help='use gzip to post data.')
@click.option("--verbose", is_flag=True, default=False, help="show more outputs")
def collect_handler(owner, repo, sms_host, sms_prog, sms_name, sms_user, sms_password, cdp_path,
                    disable_post, post_url, content_encoding, verbose):
    collect_status(owner, repo, sms_host, sms_prog, sms_name, sms_user, sms_password, cdp_path,
                   disable_post, post_url, content_encoding, verbose)


@cli.command("show")
@click.option("-o", "--owner", help="owner name, default is same as sms server user name")
@click.option("-r", "--repo", help="repo name, default is same as sms server name")
@click.option("--sms-host", help="sms host", required=True)
@click.option("--sms-prog", help="sms prog", required=True)
@click.option("-n", "--sms-name", help="sms server name", required=True)
@click.option("-u", "--sms-user", help="sms server user name", required=True)
@click.option("-p", "--sms-password", help="sms server password, default is {default_sms_password}".format(
            default_sms_password=default_sms_password))
@click.option("--cdp-path", help="cdp path", required=True)
@click.option("--verbose", is_flag=True, default=False, help="show more outputs")
def show_handler(owner, repo, sms_host, sms_prog, sms_name, sms_user, sms_password, cdp_path, verbose):
    result = get_sms_status(
        cdp_path, owner, repo, sms_host, sms_prog, sms_name, sms_user, sms_password, verbose=verbose)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    cli()
