import unittest
from urllib.parse import quote

from showergel.users import User
import arrow

from . import ShowergelTestCase, DBSession

class TestUsers(ShowergelTestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        session = DBSession()
        session.query(User).delete()

    def test_user_creation(self):
        resp = self.app.get('/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {"users": []})

        resp = self.app.put_json('/users',
            {"username": "tester", "password": "verysecret"})
        self.assertEqual(resp.status_code, 200)
        resp = self.app.put_json('/users',
            {"username": "someone êlse", "password": ""},
            expect_errors=True)
        self.assertEqual(resp.status_code, 400)
        resp = self.app.put('/users',
            "{malformed:json}",
            expect_errors=True,
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 400)
        resp = self.app.put_json('/users',
            {"username": "someone êlse", "password": "with pass"})
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get('/users')
        self.assertEqual(resp.status_code, 200)
        users = resp.json['users']
        self.assertEqual(len(users), 2)
        self.assertEqual(arrow.utcnow().date(), arrow.get(users[0]["created_at"]).date())
        self.assertEqual(arrow.utcnow().date(), arrow.get(users[0]["modified_at"]).date())

        # Don't crash when POSTing wrong
        resp = self.app.post('/login', expect_errors=True)
        self.assertEqual(resp.status_code, 404)
        resp = self.app.post('/login',
            "{malformed:json}",
            expect_errors=True,
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 404)

        resp = self.app.post_json('/login',
            {"user": "tester", "password": "lost"},
            expect_errors=True)
        self.assertEqual(resp.status_code, 404)
        resp = self.app.post_json('/login',
            {"user": "unkown", "password": "verysecret"},
            expect_errors=True)
        self.assertEqual(resp.status_code, 404)
        resp = self.app.post_json('/login',
            {"user": "tester", "password": "verysecret"})
        self.assertEqual(resp.status_code, 200)

        resp = self.app.post_json('/users/tester', {"password": "newsecret"})
        self.assertEqual(resp.status_code, 200)
        resp = self.app.post_json('/login',
            {"user": "tester", "password": "newsecret"})
        self.assertEqual(resp.status_code, 200)

        resp = self.app.delete(quote('/users/someone êlse'))
        self.assertEqual(resp.status_code, 200)

        resp = self.app.post_json('/login',
            {"user": "someone êlse", "password": "with pass"},
            expect_errors=True)
        self.assertEqual(resp.status_code, 404)

if __name__ == '__main__':
    unittest.main(failfast=True)
