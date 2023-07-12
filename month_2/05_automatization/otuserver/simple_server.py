import logging
import socket

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
        self.start_new_request_parsing = None  # attribute for calling future tasks

    def close_server_socket(self):
        if self._socket:
            self._socket.close()
        self._socket = None

    def collect_data(self) -> None:
        """Get data from the stream."""
        data = b""
        CRLF = b"\r\n\r\n"
        logging.info("Starting collecting data.")

        while CRLF not in data:
            buffer_data = self.connection.recv(1024)
            logging.info(f"Receiving data:\n{buffer_data.decode()}")
            data += buffer_data

            if not buffer_data:
                raise ConnectionError

        logging.info(f"Data collected:\n{data.decode()}")
        self.start_new_request_parsing(self.workers_num, data, self)

    def response(self, response_data: bytes, need_to_close_connection: bool = False) -> None:
        """
        Send response.
        :param response_data: data to be sent
        :param need_to_close_connection: flag to close socket.
        """
        logging.info("Starting response!")
        # logging.info(f"Got {response_data.decode()}") # That line broke the code... %)
        if response_data:
            self.connection.sendall(response_data)
            logging.info("Sent response!")
            if need_to_close_connection:
                self.connection.close()
                logging.info("Closed connection!")

    def serve_forever(self) -> None:
        """
        Main server method.
        Creates new socket connection, then gather data from the stream.
        """
        try:
            if self._socket:
                self._socket.close()
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self.host, self.port))
            self._socket.listen(1)  # worker_num?

            while True:
                self.connection, address_from = self._socket.accept()
                logging.info(f"Received connection from {address_from[0]}, started new connection:\n"
                             f"{self.connection}")
                self.connection.settimeout(self.timeout)
                try:
                    self.collect_data()
                except Exception as client_error:
                    logging.exception(f"Error occurred while working with client! Error: {client_error}")
        except socket.error as socket_error:
            logging.exception(f"Received error in socket! Error: {socket_error}")
            raise socket_error
        finally:
            if self._socket:
                self._socket.close()
