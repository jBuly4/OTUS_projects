import datetime
import hashlib
import json
import random

import pytest, tarantool

from apiscoring import api
from apiscoring.store import Store

pytest.store = Store('api_store')
pytest.context = {}
pytest.headers = {}


class Mock:
    """Mocking class for get_interest internal call of store.get(cid)"""
    @staticmethod
    def get(key):
        _key = key
        interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek", "otus"]
        return json.dumps(random.sample(interests, 2))


# using few functions from old homework =)
def get_response(request):
    return api.method_handler({"body": request, "headers": pytest.headers}, pytest.context, pytest.store)


def set_valid_auth(request):
    if request.get("login") == api.ADMIN_LOGIN:
        request["token"] = hashlib.sha512(
            (datetime.datetime.now().strftime("%Y%m%d%H") +
             api.ADMIN_SALT).encode()
            ).hexdigest()
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(msg.encode()).hexdigest()


# test order from last homework. instead of unittests pytest is used
def test_empty_request():
    _, code = get_response({})
    assert api.INVALID_REQUEST == code


@pytest.mark.parametrize(
        'req',  # dunno why but requests is reserved and cannot be used in parametrize
        [
            {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}},
            {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}},
            {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
        ]
)
def test_bad_auth(req):
    _, code = get_response(req)

    assert api.FORBIDDEN, code


@pytest.mark.parametrize(
        'req',
        [
            {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
            {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
            {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
        ]
)
def test_invalid_method_request(req):
    set_valid_auth(req)
    response, code = get_response(req)

    assert len(response)
    assert api.INVALID_REQUEST, code


class TestScoreRequest:
    @pytest.mark.parametrize(
            'arguments',
            [
                {},
                {"phone": "79175002040"},
                {"phone": "89175002040", "email": "stupnikov@otus.ru"},
                {"phone": "79175002040", "email": "stupnikovotus.ru"},
                {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
                {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
                {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"},
                {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"},
                {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
                 "first_name": 1},
                {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
                 "first_name":
                     "s", "last_name": 2},
                {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
                {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
            ]
    )
    def test_invalid_score_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        set_valid_auth(request)
        response, code = get_response(request)
        assert api.INVALID_REQUEST, code
        assert len(response)

    @pytest.mark.parametrize(
            'arguments',
            [
                {"phone": "79175002040", "email": "stupnikov@otus.ru"},
                {"phone": 79175002040, "email": "stupnikov@otus.ru"},
                {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
                {"gender": 0, "birthday": "01.01.2000"},
                {"gender": 2, "birthday": "01.01.2000"},
                {"first_name": "a", "last_name": "b"},
                {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
                 "first_name": "a", "last_name": "b"},
            ]
    )
    def test_ok_score_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        set_valid_auth(request)
        response, code = get_response(request)
        assert api.OK, code
        score = response.get("score")
        assert isinstance(score, (int, float)) and score >= 0, arguments
        assert sorted(pytest.context["has"]), sorted(arguments.keys())

    def test_ok_score_admin_request(self):
        arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
        request = {"account": "horns&hoofs", "login": "admin", "method": "online_score", "arguments": arguments}
        set_valid_auth(request)
        response, code = get_response(request)
        assert api.OK, code
        score = response.get("score")
        assert score, 42


@pytest.fixture
def set_store():
    pytest.store = Mock()


class TestInterestsRequest:
    @pytest.mark.parametrize(
            'arguments',
            [
                {},
                {"date": "20.07.2017"},
                {"client_ids": [], "date": "20.07.2017"},
                {"client_ids": {1: 2}, "date": "20.07.2017"},
                {"client_ids": ["1", "2"], "date": "20.07.2017"},
                {"client_ids": [1, 2], "date": "XXX"},
            ]
    )
    def test_invalid_interests_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
        set_valid_auth(request)
        response, code = get_response(request)
        assert api.INVALID_REQUEST, code
        assert len(response)

    @pytest.mark.parametrize(
            'arguments',
            [
                {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
                {"client_ids": [1, 2], "date": "19.07.2017"},
                {"client_ids": [0]},
            ]
    )
    def test_ok_interests_request(self, arguments, set_store):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
        set_valid_auth(request)
        response, code = get_response(request)
        assert api.OK, code
        assert len(arguments["client_ids"]), len(response)
        assert all(
                v and isinstance(v, list) and all(isinstance(i, (bytes, str)) for i in v)
                for v in response.values()
        )
        assert pytest.context.get("nclients"), len(arguments["client_ids"])


class TestDBSpaceCreation:
    HOST = "127.0.0.1"
    HOST_PORT = 3301

    def setup(self):
        self.store = {}
        self.spaces = []
        self.connection = tarantool.Connection(self.HOST, self.HOST_PORT)

    @pytest.mark.parametrize(
            'space',
            [
                'test_space_1',
                'test_space_2',
                'test_space_3',
            ]
    )
    def test_space_creating(self, space):
        self.spaces.append(space)
        self.store[space] = Store(space)
        check_space_exists = self.connection.eval(f"return box.space.{space} ~= nil")[0]
        assert check_space_exists, True

    def teardown(self):
        for space in self.spaces:
            check_space_exists = self.connection.eval(f"return box.space.{space} ~= nil")[0]
            if check_space_exists:
                self.connection.eval(f"box.space.{space}:drop()")


class TestDBSetGet:
    HOST = "127.0.0.1"
    HOST_PORT = 3301

    def setup(self):
        self.store = None
        self.spaces = []
        self.connection = tarantool.Connection(self.HOST, self.HOST_PORT)

    @pytest.mark.parametrize(
            'space, key_value',
            [
                ('test_space_1', (1, 'one')),
                ('test_space_2', (2, 'two')),
                ('test_space_3', (1, 'three')),
            ]
    )
    def test_set_get_from_db(self, space, key_value):
        key, value = key_value
        self.spaces.append(space)
        self.store = Store(space)
        self.store.set(key, value)
        db_value = self.store.get(key)

        assert db_value, key_value[1]

    def teardown(self):
        for space in self.spaces:
            check_space_exists = self.connection.eval(f"return box.space.{space} ~= nil")[0]
            if check_space_exists:
                self.connection.eval(f"box.space.{space}:drop()")
