import hashlib
import hmac
import json
import unittest
import logging

from app import app

logging.disable(logging.CRITICAL)


class SkilledHammerTestCase(unittest.TestCase):

    def setUp(self):
        app.config.update({
            'TESTING': True,
            'HAMMER_REPOSITORIES': [
                {
                    'origin': 'https://github.com/r00m/vigilant-octo',
                    'directory': '/var/www/vigilant-octo.org',
                    'command': 'supervisorctl restart vigilant-octo',
                },
            ],
            'HAMMER_SECRET': 'hammer-test-secret-123'
        })
        self.app = app.test_client()

        self.CLIENT_HEADERS = {
            'X-Github-Delivery': 'unique id for this delivery',
            'User-Agent': 'GitHub-Hookshot/buildno',
            'X-Github-Event': 'push',
            'X-Hub-Signature': 'sha1=rand'
        }

    def sign(self, payload):
        signature = hmac.new(bytearray(app.config['HAMMER_SECRET'], 'utf-8'), json.dumps(payload).encode('utf-8'), hashlib.sha1)\
            .hexdigest()
        self.CLIENT_HEADERS['X-Hub-Signature'] = "sha1={0}".format(signature)

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
        invalid_headers = self.CLIENT_HEADERS
        invalid_headers.pop('X-Github-Delivery')
        response = self.app.post('/', headers=invalid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Invalid HTTP headers', str(response.data))

        invalid_headers = self.CLIENT_HEADERS
        invalid_headers.pop('User-Agent')
        response = self.app.post('/', headers=invalid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Invalid HTTP headers', str(response.data))

        invalid_headers = self.CLIENT_HEADERS
        invalid_headers.pop('X-Github-Event')
        response = self.app.post('/', headers=invalid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Invalid HTTP headers', str(response.data))

        invalid_headers = self.CLIENT_HEADERS
        invalid_headers.pop('X-Hub-Signature')
        response = self.app.post('/', headers=invalid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Invalid HTTP headers', str(response.data))

    def test_payload(self):
        payload = {
            'repository': {
                'url': 'https://github.com/baxterthehacker/public-repo'
            }
        }

        self.sign(payload)

        response = self.app.post('/', data=json.dumps(payload), headers=self.CLIENT_HEADERS, content_type='application/json')
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

        response = self.app.post('/', data=json.dumps(payload), headers=self.CLIENT_HEADERS, content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Unknown repository', str(response.data))


if __name__ == '__main__':
    unittest.main()
