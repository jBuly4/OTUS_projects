#  Prepare tarantool
#  connection.eval('box.schema.space.create("new_space")')
#  connection.eval("box.space.examples:create_index('primary', {type = 'hash', parts = {1, 'unsigned'}})")
# Check if a space named 'myspace' exists
# result = conn.eval('return box.space.myspace ~= nil')

import time

import tarantool

HOST = "127.0.0.1"
HOST_PORT = 3301
RECONNECT_MAX_COUNT = 3
RECONNECT_DELAY = 20
TIMEOUT = 180


class Store:
    def __init__(
            self,
            space_name: str,
            host: str = HOST,
            port: int = HOST_PORT,
            user: str = None,
            passwd: str = None,
            reconnect_max_attempts: int = RECONNECT_MAX_COUNT,
            reconnect_delay: int = RECONNECT_DELAY,
            connect_now: bool = False,
            connect_timeout: int = TIMEOUT
    ):
        self.connect = tarantool.Connection(
                host=host,
                port=port,
                user=user,
                password=passwd,
                reconnect_max_attempts=reconnect_max_attempts,
                reconnect_delay=reconnect_delay,
                connect_now=connect_now,
                connection_timeout=connect_timeout
        )
        self.space_name = space_name
        self.cache = {}
        self._run_config()

    def _run_config(self):
        """
            After installing docker of Tarantool you need to prepare db:
            create space, create index for this space.
            After that you can use this space to save data.
            """
        check_space_exists = self.connect.eval(f"return box.space.{self.space_name} ~= nil")
        if not check_space_exists:
            self.connect.eval(f"box.schema.space.create('{self.space_name}')")
            self.connect.eval(
                    f"box.space.{self.space_name}:create_index('primary', {{type = 'hash', parts = {{1, 'unsigned'}}}})"
            )

    def cache_set(self, key, value, time_to_be_stored):
        self.cache[key] = (value, time.time() + time_to_be_stored)

    def cache_get(self, key):
        cached_value = self.cache.get(key, None)
        if cached_value:
            value, time_stored = cached_value
            if time.time() <= time_stored:
                return value

    def set(self, key, value):
        self.connect.replace(self.space_name, (key, value))

    def get(self, key):
        response = self.connect.select(self.space_name, key)
        return response


# store = Store('test5')
# print(store.connect.space('test2').__dict__)

