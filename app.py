import os
import subprocess
import logging

from flask import Flask, request, jsonify

from skilled_hammer import repositories, exceptions, log
from skilled_hammer.utils import valid_http_headers, pull

app = Flask(__name__)
app.config.update({
    'DEBUG': os.environ.get('DEBUG', True),
    'HAMMER_VERSION': "1.0.0",
    'HAMMER_SECRET': os.environ.get('HAMMER_SECRET', False),
    'HAMMER_REPOSITORIES': repositories.load(),
})
log.setup()
logger = logging.getLogger(__name__)


@app.route('/', methods=['POST'])
def deploy():
    try:
        if not valid_http_headers(request):
            raise exceptions.SuspiciousOperation("Invalid HTTP headers")

        url = repositories.repo_url_from_payload(request.get_json())

        if url not in app.config['HAMMER_REPOSITORIES']:
            raise exceptions.UnknownRepository("Unknown repository")

        pull_succeeded = False

        for _, repo in app.config['HAMMER_REPOSITORIES'].items():
            if repo['origin'] == url:
                pull_succeeded = pull(repo['directory'])
                if pull_succeeded and 'command' in repo:
                    logger.info("Changing working directory to '{0}'".format(repo['directory']))
                    logger.info("Running command: {0}".format(repo['command']))
                    subprocess.call(repo['command'], shell=True, cwd=repo['directory'])
                break

        response = jsonify({'status': pull_succeeded})
        response.status_code = 200
    except exceptions.HammerException as e:
        logger.error(e)
        response = jsonify({'status': False, 'error': e.args[0]})
        response.status_code = 500

    return response


if __name__ == "__main__":
    app.run()
