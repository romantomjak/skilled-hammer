import hashlib
import hmac
import os
import logging

import git

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
