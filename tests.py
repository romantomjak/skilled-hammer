import unittest

from skilled_hammer import app


class SkilledHammerTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
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

        # haha, already discovered first bug :D
        # response = self.app.post('/')
        # print(response)
        # self.assertEqual(response.status_code, 405)


if __name__ == '__main__':
    unittest.main()
