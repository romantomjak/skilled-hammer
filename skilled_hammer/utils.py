import hashlib
import hmac
import os
import string
import random

import git


def valid_github_http_headers(request):
    if 'X-Github-Delivery' not in request.headers:
        return False

    if 'User-Agent' not in request.headers or request.headers['User-Agent'][:16] != 'GitHub-Hookshot/':
        return False

    if 'X-Github-Event' not in request.headers or request.headers['X-Github-Event'] != 'push':
        return False

    if 'X-Hub-Signature' not in request.headers:
        return False
    else:
        from main import app
        hmac_digest = hmac.new(bytes(app.config['HAMMER_SECRET'], 'utf-8'), request.data, hashlib.sha1).hexdigest()
        if hmac_digest != request.headers['X-Hub-Signature'][5:]:
            return False

    return True


def pull(directory):
    try:
        # use correct permissions
        st = os.stat(directory)
        os.seteuid(st.st_uid)
        os.setegid(st.st_gid)

        repo = git.Repo(directory)
        info = repo.remotes.origin.pull()[0]

        if info.flags & info.ERROR:
            print("Git pull failed: {0}".format(info.note))
            return False
        elif info.flags & info.REJECTED:
            print("Could not merge after git pull: {0}".format(info.note))
            return False
        elif info.flags & info.HEAD_UPTODATE:
            print("Head is already up to date")
    except Exception as e:
        print(e)
        return False
    finally:
        # restore root permissions
        os.seteuid(0)
        os.setegid(0)

    return True


def random_secret():
    return ''.join([random.choice(string.printable) for _ in range(0, 20)])
