import unittest
import json

from flask.testing import FlaskClient

from app import create_app, redis_client
from app.db.model import Identity
from tests.utils import get_register_email_code, set_user


class JsonFlaskClient(FlaskClient):
    def open(self, *args, **kwargs):
        kwargs['content_type'] = 'application/json'
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
        return super(JsonFlaskClient, self).open(*args, **kwargs).get_json()


class TestApp(unittest.TestCase):
    def setUp(self):
        app = create_app('testing')
        app.test_client_class = JsonFlaskClient
        self.context = app.app_context()
        self.context.push()
        self.client = app.test_client()
        Identity.init_identities()

    def tearDown(self):
        redis_client.flushdb()
        self.context.pop()

    def test_register(self):
        # input register module with inputting nothing
        data = self.client.post('/api/v1/user')
        assert data['code'] == 400
        assert data['payload']['message'] == 'Please input username'
        assert data['request'] == '/api/v1/user'

        # input fulfilled all params without available email code
        data = self.client.post('/api/v1/user', data={
            "username": "test_username",
            "password": "test_password",
            "password2": "test_password",
            "email": "hello20011@163.com",
            "code": "1234"
        })
        assert data['code'] == 400
        assert data['payload']['message'] == 'Email code expired'
        assert data['request'] == '/api/v1/user'

        # input fulfilled params
        code = get_register_email_code('hello20011@163.com')
        data = self.client.post('/api/v1/user', data={
            "username": "test_username",
            "password": "test_password",
            "password2": "test_password",
            "email": "hello20011@163.com",
            "code": code
        })
        assert data['code'] == 200
        assert data['payload']['message'] == 'Successfully registered'
        assert data['request'] == '/api/v1/user'

    def test_login(self):
        # test login module with inputting nothing
        data = self.client.post('/api/v1/auth/token')
        assert data['code'] == 400
        assert data['payload']['message'] == 'Please input username or email address'
        assert data['request'] == '/api/v1/auth/token'

        # input unregistered username and password
        data = self.client.post('/api/v1/auth/token', data={
            "username": "username",
            "password": "password"
        })
        assert data['code'] == 400
        assert data['payload']['message'] == 'Username or password is wrong'
        assert data['request'] == '/api/v1/auth/token'

        # input correct username and password
        set_user('Username_test', 'hello20011@163.com', 'Password')
        data = self.client.post('/api/v1/auth/token', data={
            "username": "Username_test",
            "password": "Password"
        })
        assert data['code'] == 200
        assert data['payload']['token'] is not None
        assert data['request'] == '/api/v1/auth/token'

        # input correct email and password
        data = self.client.post('/api/v1/auth/token', data={
            "username": "hello20011@163.com",
            "password": "Password"
        })
        assert data['code'] == 200
        assert data['payload']['token'] is not None
        assert data['request'] == '/api/v1/auth/token'
