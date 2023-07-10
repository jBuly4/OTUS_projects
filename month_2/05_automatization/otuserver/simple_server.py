import socket
import logging

logging.basicConfig(
        format='[%(asctime)s] %(levelname).1s %(message)s',
        level=logging.INFO, datefmt='%Y.%m.%d %H:%M:%S'
)


class SimpleHTTPServer:
    def __init__(
            self,
            doc_root: str,
            host: str,
            port: int,
            workers_num: int = 5
    ):
        self.doc_root = doc_root
        self.host = host
        self.port = port
        self.workers_num = workers_num
        self.timeout: int = 1
        self.reconnect_delay: int = 1
        self.reconnect_max_count: int = 3
        self._socket: socket.socket = None
        self.connection: socket.socket = None
        self.start_new_request_parsing = None

    def close_server_socket(self):
        if self._socket:
            self._socket.close()
        self._socket = None

    def collect_data(self):
        data = b""
        CRLF = b"\r\n\r\n"

        while CRLF not in data:
            buffer_data = self.connection.recv(1024)
            data += buffer_data

            if not buffer_data:
                raise ConnectionError

        self.start_new_request_parsing(self.workers_num, data)

    def response(self, response_data, need_to_close_connection=False):
        if response_data:
            self.connection.sendall(response_data)
            if need_to_close_connection:
                self.connection.close()

    def serve_forever(self):
        """Main server method"""
        try:
            if self._socket:
                self._socket.close()
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self.host, self.port))
            self._socket.listen(1)  # worker_num?

            while True:
                self.connection, address_from = self._socket.accept()
                logging.info(f"Received connection from {address_from}")
                self.connection.settimeout(self.timeout)
                try:
                    self.collect_data()
                except Exception as clinet_error:
                    logging.exception(f"Error occurred while working with client! Error: {clinet_error}")
        except socket.error as socket_error:
            logging.exception(f"Received error in socket! Error: {socket_error}")
            raise socket_error
        finally:
            if self._socket:
                self._socket.close()
