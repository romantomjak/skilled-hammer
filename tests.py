import json
import unittest

from skilled_hammer import exceptions
from main import app


class SkilledHammerTestCase(unittest.TestCase):

    def setUp(self):
        self.CLIENT_HEADERS = {
            'HTTP_X_GITHUB_DELIVERY': 'some hash',
            'HTTP_USER_AGENT': 'GitHub-Hookshot/buildno',
            'HTTP_X_GITHUB_EVENT': 'push',
            'HTTP_X_GITHUB_SIGNATURE': 'rand'
        }

        app.config.update({
            'TESTING': True,
            'HAMMER_VERSION': "1.0.0",
            'HAMMER_REPOSITORIES': [
                {
                    'origin': 'https://github.com/r00m/vigilant-octo',
                    'directory': '/var/www/vigilant-octo.org',
                    'command': 'supervisorctl restart vigilant-octo',
                }
            ],
        })
        self.app = app.test_client()

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
        with self.assertRaises(exceptions.SuspiciousOperation):
            response = self.app.post('/')
            self.assertEqual(response.status_code, 405)

    def test_github_headers(self):
        invalid_headers = self.CLIENT_HEADERS
        invalid_headers.pop('HTTP_X_GITHUB_DELIVERY')
        with self.assertRaises(exceptions.SuspiciousOperation):
            self.app.post('/', headers=invalid_headers)

        invalid_headers = self.CLIENT_HEADERS
        invalid_headers.pop('HTTP_USER_AGENT')
        with self.assertRaises(exceptions.SuspiciousOperation):
            self.app.post('/', headers=invalid_headers)

        invalid_headers = self.CLIENT_HEADERS
        invalid_headers.pop('HTTP_X_GITHUB_EVENT')
        with self.assertRaises(exceptions.SuspiciousOperation):
            self.app.post('/', headers=invalid_headers)

        invalid_headers = self.CLIENT_HEADERS
        invalid_headers.pop('HTTP_X_GITHUB_SIGNATURE')
        with self.assertRaises(exceptions.SuspiciousOperation):
            self.app.post('/', headers=invalid_headers)

    def test_payload(self):
        payload = {
            'repository': {
                'url': 'https://github.com/baxterthehacker/public-repo'
            }
        }
        with self.assertRaises(exceptions.UnknownRepository):
            self.app.post('/', data=json.dumps(payload), headers=self.CLIENT_HEADERS, content_type='application/json')

    def test_no_repositories(self):
        app.config.update({
            'HAMMER_REPOSITORIES': [],
        })

        payload = {
            'repository': {
                'url': 'https://github.com/baxterthehacker/public-repo'
            }
        }
        with self.assertRaises(exceptions.UnknownRepository):
            self.app.post('/', data=json.dumps(payload), headers=self.CLIENT_HEADERS, content_type='application/json')


if __name__ == '__main__':
    unittest.main()
