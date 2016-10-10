import os
import sys

from . import repositories


HAMMER_SECRET = os.environ.get('HAMMER_SECRET', None)
HAMMER_VERSION = "1.0.0"
HAMMER_REPOSITORIES = repositories.load()


if 'tests.py' in sys.argv:
    """
    Override values for test environment
    """
    TESTING = True
    HAMMER_SECRET = b'testkey123'
    HAMMER_REPOSITORIES = [
        {
            'origin': 'https://github.com/r00m/vigilant-octo',
            'directory': '/var/www/vigilant-octo.org',
            'command': 'supervisorctl restart vigilant-octo',
        },
    ]
