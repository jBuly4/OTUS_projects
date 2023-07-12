import datetime
import logging

from dataclasses import dataclass, field
from typing import Dict

logging.basicConfig(
        format='[%(asctime)s] %(levelname).1s %(message)s',
        level=logging.INFO, datefmt='%Y.%m.%d %H:%M:%S'
)


@dataclass
class SimpleHTTPResponse:
    protocol: str = "HTTP/1.0"
    status_code: int = 200
    status: str = "OK"
    body: bytes = b""
    headers: Dict = field(default_factory=dict)

    def __post_init__(self):
        self.headers = {
            "Content-Type": "text/html; charset=utf-8",
            "Content-Length": 0,
            "Date": self.get_date_now(),
            "Server": "OTUServer",
            "Connection": "close"
        }

        # for key, value in self.__dict__.items():
        #     logging.info(f"Attribute {key} has been set to value:\n{value}\n")

    @staticmethod
    def get_date_now():
        return datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    @staticmethod
    def prepare_response_bytes(instance):
        result = ""
        result += instance.protocol + " " + str(instance.status_code) + " " + instance.status + "\r\n"
        result += SimpleHTTPResponse.collect_headers(instance.headers)
        result += "\r\n"

        result = result.encode()

        if len(instance.body) > 0:
            result += instance.body

        return result

    @staticmethod
    def collect_headers(headers):
        result = ""

        for key, value in headers.items():
            result += str(key) + ": " + str(value) + "\r\n"

        return result
