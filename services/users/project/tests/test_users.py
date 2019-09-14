import json
import unittest

from project.tests.base import BaseTestCase
from project.api.models import User
from project import db


def add_user(username, email):
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user


class TestUserService(BaseTestCase):
    """Tests for the Users Service."""

    def test_users(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """Ensure a new user can be added to db"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'tester@test.com'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('tester@test.com was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid Payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """If the JSON object does not have a username key"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({'email': 'tester@test.com'}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid Payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        """Ensure error is thrown if the email already exists"""
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'tester',
                    'email': 'tester@test.com'
                }),
                content_type="application/json",
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'tester',
                    'email': 'tester@test.com'
                }),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Sorry. That email already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        """Ensure get single user behaves correctly"""
        user = add_user('tester', 'tester@test.com')
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('tester', data['data']['username'])
            self.assertIn('tester@test.com', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided"""
        with self.client:
            response = self.client.get('/users/invalid')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist"""
        with self.client:
            response = self.client.get('/users/999999999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist.', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        """Ensure get all users behaves correctly"""
        add_user('user1', 'user1@test.com')
        add_user('user2', 'user2@test.com')
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('user1', data['data']['users'][0]['username'])
            self.assertIn('user1@test.com', data['data']['users'][0]['email'])
            self.assertIn('user2', data['data']['users'][1]['username'])
            self.assertIn('user2@test.com', data['data']['users'][1]['email'])
            self.assertIn('success', data['status'])

    def test_main_no_users(self):
        """When no users have been added to the database"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertIn(b'<p>No users!</p>', response.data)

    def test_main_with_users(self):
        """When users have been added to the database."""
        add_user('user1', 'user1@test.com')
        add_user('user2', 'user2@test.com')
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'user1', response.data)
            self.assertIn(b'user2', response.data)

    def test_main_add_users(self):
        """Enusre a new user can be added to the database via a POST request"""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(
                    username='user3',
                    email='user3@test.com'
                ),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'user3', response.data)


if __name__ == '__main__':
    unittest.main()
