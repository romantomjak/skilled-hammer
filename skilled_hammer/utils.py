import hashlib
import hmac
import os
import string
import random
import logging

import git

logger = logging.getLogger(__name__)


def valid_github_http_headers(request):
    if 'X-Github-Delivery' not in request.headers:
        logger.error("'X-Github-Delivery' is missing from headers")
        return False

    if 'User-Agent' not in request.headers or request.headers['User-Agent'][:16] != 'GitHub-Hookshot/':
        logger.error("'User-Agent' is missing from headers or has incorrect value ({0})".format(request.headers['User-Agent']))
        return False

    if 'X-Github-Event' not in request.headers or request.headers['X-Github-Event'] != 'push':
        logger.error("'X-Github-Event' is missing from headers or has incorrect value ({0})".format(request.headers['X-Github-Event']))
        return False

    if 'X-Hub-Signature' not in request.headers:
        logger.error("'X-Hub-Signature' is missing from headers")
        return False
    else:
        from main import app
        hmac_digest = hmac.new(bytes(app.config['HAMMER_SECRET'], 'utf-8'), request.data, hashlib.sha1).hexdigest()
        if hmac_digest != request.headers['X-Hub-Signature'][5:]:
            logger.error("'X-Hub-Signature' did not match '{0}'".format(hmac_digest))
            return False

    return True


def pull(directory):
    try:
        # use correct permissions
        st = os.stat(directory)
        logger.info("Will try to pull() as {0}:{1}".format(st.st_uid, st.st_gid))

        os.seteuid(st.st_uid)
        os.setegid(st.st_gid)

        repo = git.Repo(directory)
        info = repo.remotes.origin.pull()[0]

        if info.flags & info.ERROR:
            logger.error("Git pull failed: {0}".format(info.note))
            return False
        elif info.flags & info.REJECTED:
            logger.error("Could not merge after git pull: {0}".format(info.note))
            return False
        elif info.flags & info.HEAD_UPTODATE:
            logger.error("Head is already up to date")
    except Exception as e:
        logger.error(e)
        return False
    finally:
        # restore root permissions
        logger.info("Restoring root permissions")
        os.seteuid(0)
        os.setegid(0)

    return True


def random_secret():
    return ''.join([random.choice(string.printable) for _ in range(0, 20)])
