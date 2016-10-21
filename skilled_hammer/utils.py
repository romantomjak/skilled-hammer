import hashlib
import hmac
import os
import logging
import subprocess
import time
from threading import Thread

import git
import requests

logger = logging.getLogger(__name__)


def valid_http_headers(request):
    if 'User-Agent' not in request.headers:
        logger.error("'User-Agent' is missing from http headers")
        return False

    if 'GitHub' in request.headers['User-Agent']:
        logger.info("Validating GitHub Webhook")
        return valid_github_http_headers(request)

    if 'Bitbucket' in request.headers['User-Agent']:
        logger.info("Validating Bitbucket Webhook")
        return valid_bitbucket_http_headers(request)

    logger.warning("Unknown GIT hosting provider")

    return False


def valid_bitbucket_http_headers(request):
    if 'X-Event-Key' not in request.headers:
        logger.error("'X-Event-Key' is missing from headers")
        return False

    if request.headers['User-Agent'][:19] != 'Bitbucket-Webhooks/':
        logger.error("'User-Agent' has incorrect value ({0})".format(request.headers['User-Agent']))
        return False

    if 'X-Hook-UUID' not in request.headers:
        logger.error("'X-Hook-UUID' is missing from headers")
        return False

    if 'X-Request-UUID' not in request.headers:
        logger.error("'X-Request-UUID' is missing from headers")
        return False

    if 'X-Attempt-Number' not in request.headers:
        logger.error("'X-Attempt-Number' is missing from headers")
        return False

    return True


def valid_github_http_headers(request):
    if 'X-Github-Delivery' not in request.headers:
        logger.error("'X-Github-Delivery' is missing from headers")
        return False

    if request.headers['User-Agent'][:16] != 'GitHub-Hookshot/':
        logger.error("'User-Agent' has incorrect value ({0})".format(request.headers['User-Agent']))
        return False

    if 'X-Github-Event' not in request.headers or request.headers['X-Github-Event'] != 'push':
        logger.error("'X-Github-Event' is missing from headers or has incorrect value ({0})".format(request.headers['X-Github-Event']))
        return False

    if 'X-Hub-Signature' in request.headers:
        from app import app
        if not app.config['HAMMER_SECRET']:
            logger.error("Webhook was configured to use a Secret, but 'HAMMER_SECRET' environment variable was not set")
            return False
        hmac_digest = hmac.new(bytearray(app.config['HAMMER_SECRET'], 'utf-8'), request.data, hashlib.sha1).hexdigest()
        if hmac_digest != request.headers['X-Hub-Signature'][5:]:
            logger.error("'X-Hub-Signature' did not match '{0}'".format(hmac_digest))
            return False

    return True


def pull(directory):
    """
    Pulls latest changes with the user rights that owns the folder
    """
    try:
        st = os.stat(directory)
        logger.info("Pulling as {0}:{1}...".format(st.st_uid, st.st_gid))

        # order is important: after seteuid() call the effective UID isn't 0 anymore, so seteuid() will not be allowed
        os.setegid(st.st_uid)
        os.seteuid(st.st_gid)

        repo = git.Repo(directory)
        info = repo.remotes.origin.pull()[0]

        if info.flags & info.ERROR:
            logger.error("Pull failed: {0}".format(info.note))
            return False
        elif info.flags & info.REJECTED:
            logger.error("Could not merge after pull: {0}".format(info.note))
            return False
        elif info.flags & info.HEAD_UPTODATE:
            logger.info("Head is already up to date")
    except PermissionError:
        logger.error("Insufficient permissions to set uid/gid")
        return False
    finally:
        logger.info("Restoring root permissions")
        os.setegid(0)
        os.seteuid(0)

    return True


def run(command, directory, slack_webhook_url):
    """
    Run the specified command as the user that owns the directory
    """
    try:
        st = os.stat(directory)

        # order is important: after seteuid() call the effective UID isn't 0 anymore, so seteuid() will not be allowed
        os.setegid(st.st_uid)
        os.seteuid(st.st_gid)

        logger.info("Changing working directory to '{0}'".format(directory))
        logger.info("Spawning background command '{0}' as {1}:{2}...".format(command, st.st_uid, st.st_gid))

        def background():
            """
            I don't care how long it takes to run the command, but Bitbucket gets angry when it takes longer
            than 10 seconds. My npm build takes around 15 secs, so I'd get 3 Webhooks from Bitbucket, because
            it thinks each Webhook timedout.

            Easy way out is to return response immediately and start a background thread that
            does all of the heavy lifting.
            """
            start_time = time.time()
            output = subprocess.check_output(command, shell=True, cwd=directory, stderr=subprocess.STDOUT)
            completed_in = time.time() - start_time

            logger.info("Background command finished in {0:.2f} seconds".format(completed_in))

            if slack_webhook_url:
                slack_notification(slack_webhook_url, "Build took {0:.2f} seconds :rocket:".format(completed_in), output)

        Thread(target=background).start()
    except PermissionError:
        logger.error("Insufficient permissions to set uid/gid")
    except subprocess.CalledProcessError as e:
        logger.error("Error: {0}".format(e.output))
    finally:
        logger.info("Restoring root permissions")
        os.setegid(0)
        os.seteuid(0)


def slack_notification(webhook_url, message, output):
    """
    Post a message to slack channel
    """
    requests.post(webhook_url, json={
        "username": "Skilled Hammer",
        "text": message,
        "icon_emoji": ":bulb:",
        "mrkdwn": True,
        "attachments": [
            {
                "fallback": message,
                "color": "#E8E8E8",
                "title": "Console Output",
                "text": output
            },
        ]
    })
