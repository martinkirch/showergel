import unittest
from . import ShowergelTestCase

class TestUsers(ShowergelTestCase):

    def test_user_creation(self):
        resp = self.app.get('/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {"users": []})

        resp = self.app.put_json('/users', {"username": "tester", "password": "verysecret"})
        self.assertEqual(resp.status_code, 200)
        resp = self.app.put_json('/users', {"username": "someone êlse", "password": ""}, expect_errors=True)
        self.assertEqual(resp.status_code, 400)
        resp = self.app.put_json('/users', {"username": "someone êlse", "password": "with pass"})
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get('/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json['users']), 2)

        resp = self.app.post_json('/login', {"username": "tester", "password": "lost"}, expect_errors=True)
        self.assertEqual(resp.status_code, 404)
        resp = self.app.post_json('/login', {"username": "unkown", "password": "verysecret"}, expect_errors=True)
        self.assertEqual(resp.status_code, 404)
        resp = self.app.post_json('/login', {"username": "tester", "password": "verysecret"})
        self.assertEqual(resp.status_code, 200)

        resp = self.app.delete('/users', {"username": "tester"})
        self.assertEqual(resp.status_code, 200)

        resp = self.app.post_json('/login', {"username": "tester", "password": "verysecret"}, expect_errors=True)
        self.assertEqual(resp.status_code, 404)

if __name__ == '__main__':
    unittest.main(failfast=True)
