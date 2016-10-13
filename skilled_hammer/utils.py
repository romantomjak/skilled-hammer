import hashlib
import hmac
import subprocess
import string
import random

import git


def valid_github_http_headers(request):
    if 'HTTP_X_GITHUB_DELIVERY' not in request.headers:
        return False

    if 'HTTP_USER_AGENT' not in request.headers or request.headers['HTTP_USER_AGENT'][:16] != 'GitHub-Hookshot/':
        return False

    if 'HTTP_X_GITHUB_EVENT' not in request.headers or request.headers['HTTP_X_GITHUB_EVENT'] != 'push':
        return False

    if 'HTTP_X_GITHUB_SIGNATURE' not in request.headers:
        return False
    else:
        from main import app
        hmac_digest = hmac.new(bytes(app.config['HAMMER_SECRET'], 'utf-8'), request.data, hashlib.sha1).hexdigest()
        if hmac_digest != request.headers['HTTP_X_GITHUB_SIGNATURE']:
            return False

    return True


def pull(directory, command):
    try:
        repo = git.Repo(directory)
        info = repo.remotes.origin.pull()[0]

        if info.flags & info.ERROR:
            print("Git pull failed: {0}".format(info.note))
        elif info.flags & info.REJECTED:
            print("Could not merge after git pull: {0}".format(info.note))
        elif info.flags & info.HEAD_UPTODATE:
            print("Head is already up to date")
        else:
            subprocess.call(command, shell=True, cwd=directory)
    except Exception as e:
        print(e)


def random_secret():
    return ''.join([random.choice(string.printable) for _ in range(0, 20)])
