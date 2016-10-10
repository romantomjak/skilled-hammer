import os
import subprocess

import git
from flask import Flask, request

from skilled_hammer import config, exceptions
from skilled_hammer.utils import valid_github_http_headers

app = Flask(__name__)

try:
    app.config.update({
        'HAMMER_SECRET': os.environ.get('HAMMER_SECRET', b''),
        'HAMMER_VERSION': "1.0.0",
        'HAMMER_REPOSITORIES': config.load(),
    })
except exceptions.HammerException as e:
    print(e)
    exit(1)


@app.route('/', methods=['POST'])
def deploy():
    if not valid_github_http_headers(request):
        raise exceptions.SuspiciousOperation("Invalid HTTP headers")

    payload = request.get_json()

    if not payload \
            or 'repository' not in payload \
            or 'url' not in payload['repository']:
        raise exceptions.SuspiciousOperation("Invalid payload")

    url = payload['repository']['url']

    if url not in app.config['HAMMER_REPOSITORIES']:
        raise exceptions.UnknownRepository("Unknown repository")

    for repo in app.config['HAMMER_REPOSITORIES']:
        if repo['origin'] == url:
            pull(repo['directory'], repo['command'])
            break

    return ""


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


if __name__ == "__main__":
    app.run(debug=True)
