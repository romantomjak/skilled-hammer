import os

from flask import Flask, request

from skilled_hammer import repositories
from skilled_hammer import exceptions
from skilled_hammer.utils import valid_github_http_headers, pull

app = Flask(__name__)
app.config.update({
    'HAMMER_SECRET': os.environ.get('HAMMER_SECRET', None),
    'HAMMER_VERSION': "1.0.0",
    'HAMMER_REPOSITORIES': repositories.load(),
})


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


if __name__ == "__main__":
    app.run(debug=True)
