import subprocess

import git
from flask import Flask, request

import config
import exceptions

app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def deploy():
    payload = request.get_json()
    url = payload['repository']['url']

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
    try:
        app.config.update({
            'HAMMER_VERSION': "1.0.0",
            'HAMMER_REPOSITORIES': config.load(),
        })
        app.run(debug=True)
    except exceptions.HammerException as e:
        print(e)
        exit(1)
