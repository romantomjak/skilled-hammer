import subprocess

import git
from flask import Flask, request

app = Flask(__name__)

REPOS = [
    {
        'origin': 'https://github.com/r00m/vigilant-octo-eureka',
        'directory': '/var/www/stabule.lv/public_html/vigilant-octo-eureka',
        'command': 'echo "Hello World!" >> test.txt',
    }
]


@app.route('/', methods=['POST'])
def deploy():
    payload = request.get_json()
    url = payload['repository']['url']

    for repo in REPOS:
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
