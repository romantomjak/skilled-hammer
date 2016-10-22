import hashlib
import hmac
import json
import unittest
import logging

try:
    from unittest.mock import patch
except:
    from mock import patch # Python 2

from app import app

logging.disable(logging.CRITICAL)


class SkilledHammerTestCase(unittest.TestCase):

    def setUp(self):
        app.config.update({
            'TESTING': True,
            'HAMMER_REPOSITORIES': {
                'https://github.com/r00m/vigilant-octo': {
                    'name': 'vigilant-octo',
                    'origin': 'https://github.com/r00m/vigilant-octo',
                    'directory': '/var/www/vigilant-octo.org',
                    'command': 'supervisorctl restart vigilant-octo',
                },
                'https://bitbucket.org/bitbucket/bitbucket': {
                    'name': 'bitbucket',
                    'origin': 'https://bitbucket.org/bitbucket/bitbucket',
                    'directory': '/var/www/bitbucket.org',
                    'command': 'supervisorctl restart bitbucket',
                },
            },
            'HAMMER_SECRET': 'hammer-test-secret-123'
        })
        self.app = app.test_client()

        self.GITHUB_HEADERS = {
            'X-Github-Delivery': 'unique id for this delivery',
            'User-Agent': 'GitHub-Hookshot/buildno',
            'X-Github-Event': 'push',
            'X-Hub-Signature': 'sha1=rand'
        }

        self.BITBUCKET_HEADERS = {
            'X-Event-Key': 'event key that triggered the webhook',
            'User-Agent': 'Bitbucket-Webhooks/version',
            'X-Hook-UUID': 'the uuid of the webhook',
            'X-Request-UUID': 'the uuid of the request',
            'X-Attempt-Number': 'the number of times bitbucket attempts to send the payload',
        }

    def sign(self, payload):
        signature = hmac.new(bytearray(app.config['HAMMER_SECRET'], 'utf-8'), json.dumps(payload).encode('utf-8'), hashlib.sha1)\
            .hexdigest()
        self.GITHUB_HEADERS['X-Hub-Signature'] = "sha1={0}".format(signature)

    def test_only_post_allowed(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 405)

        response = self.app.head('/')
        self.assertEqual(response.status_code, 405)

        response = self.app.delete('/')
        self.assertEqual(response.status_code, 405)

        response = self.app.put('/')
        self.assertEqual(response.status_code, 405)

        response = self.app.patch('/')
        self.assertEqual(response.status_code, 405)

        # POST is treated differently as it will trigger other security checks
        response = self.app.post('/')
        self.assertEqual(response.status_code, 500)

    def test_github_headers(self):
        invalid_headers = self.GITHUB_HEADERS
        invalid_headers.pop('X-Github-Delivery')
        response = self.app.post('/', headers=invalid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Invalid HTTP headers', str(response.data))

        invalid_headers = self.GITHUB_HEADERS
        invalid_headers.pop('User-Agent')
        response = self.app.post('/', headers=invalid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Invalid HTTP headers', str(response.data))

        invalid_headers = self.GITHUB_HEADERS
        invalid_headers.pop('X-Github-Event')
        response = self.app.post('/', headers=invalid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Invalid HTTP headers', str(response.data))

        invalid_headers = self.GITHUB_HEADERS
        invalid_headers.pop('X-Hub-Signature')
        response = self.app.post('/', headers=invalid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Invalid HTTP headers', str(response.data))

    @patch('app.run')
    @patch('app.pull')
    def test_github_payload(self, mock_pull, mock_run):
        mock_pull.return_value = True
        mock_run.return_value = True

        payload = {
            'repository': {
                'url': 'https://github.com/r00m/vigilant-octo'
            }
        }

        self.sign(payload)

        response = self.app.post('/', data=json.dumps(payload), headers=self.GITHUB_HEADERS, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    @patch('app.run')
    @patch('app.pull')
    def test_bitbucket_payload(self, mock_pull, mock_run):
        mock_pull.return_value = True
        mock_run.return_value = True

        payload = {
            'repository': {
                'links': {
                    'html': {
                        'href': 'https://bitbucket.org/bitbucket/bitbucket'
                    }
                }
            }
        }

        response = self.app.post('/', data=json.dumps(payload), headers=self.BITBUCKET_HEADERS, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_unknown_repository(self):
        payload = {
            'repository': {
                'url': 'https://github.com/baxterthehacker/public-repo'
            }
        }

        self.sign(payload)

        response = self.app.post('/', data=json.dumps(payload), headers=self.GITHUB_HEADERS,
                                 content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Unknown repository', str(response.data))

    def test_no_repositories(self):
        app.config.update({
            'HAMMER_REPOSITORIES': [],
        })

        payload = {
            'repository': {
                'url': 'https://github.com/r00m/vigilant-octo'
            }
        }

        self.sign(payload)

        response = self.app.post('/', data=json.dumps(payload), headers=self.GITHUB_HEADERS, content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Unknown repository', str(response.data))


if __name__ == '__main__':
    unittest.main()
