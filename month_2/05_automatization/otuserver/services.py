import logging
import mimetypes
import os

from os import path

from http_response import SimpleHTTPResponse
from http_requests import SimpleHTTPRequest
from simple_server import SimpleHTTPServer

logging.basicConfig(
        format='[%(asctime)s] %(levelname).1s %(message)s',
        level=logging.INFO, datefmt='%Y.%m.%d %H:%M:%S'
)


def index(path_to_dir: str) -> bool:
    """
    Check if directory has index.html for directory requests
    :param path_to_dir: path to directory
    :return: True if index.html in directory else False
    """
    if path.isdir(path_to_dir):
        return 'index.html' in os.listdir(path_to_dir)
    return False


#  for index.html look at https://github.com/s-stupnikov/http-test-suite/blob/master/httptest/dir2/index.html
def parse_request(request: SimpleHTTPRequest, server: SimpleHTTPServer) -> None:
    """
    Parse request.
    :param server: server class instance
    :param request: initially processed request
    """
    logging.info(f"Started parsing.")
    requested_path = path.abspath(server.doc_root + request.URL)
    _head = False

    response = SimpleHTTPResponse()

    if request.method == "HEAD":
        _head = True

    if path.exists(requested_path) and "../" not in request.URL:
        logging.info(f"Escaping directory passed.")
        if path.isfile(requested_path) and not request.URL.endswith("/"):
            logging.info(f"No / at the end and request file.")
            file_name, file_extension = path.splitext(requested_path)
            logging.info(f"Checking file extension {file_extension}.")
            content_type = mimetypes.types_map[file_extension]
            if not _head:
                with open(requested_path, "rb") as file:
                    body = file.read()
                response.body = body
            response.headers["Content-Type"] = content_type
            response.headers["Content-Length"] = len(response.body)
        elif index(requested_path):
            logging.info(f"Index file request.")
            if not _head:
                body = b"<html>Directory index file</html>"
                response.body = body
            response.headers["Content-Type"] = "txt/html"
            response.headers["Content-Length"] = len(response.body)
        else:
            response.status = "NOT FOUND"
            response.status_code = 404
    else:
        response.status = "NOT FOUND"
        response.status_code = 404

    server.response(SimpleHTTPResponse.prepare_response_bytes(instance=response), _head)


def request_processor(request_bytes: bytes, server_instance: SimpleHTTPServer) -> None:
    """
    Get request and start to parse it depending on request.method.
    :param request_bytes: bytes from request stream
    :param server_instance: server
    """
    logging.info(f"Started request_processor.")
    request = SimpleHTTPRequest(request_byte_array=request_bytes)

    if request.method == "HEAD" or request.method == "GET":
        logging.info(f"Request method {request.method}")
        parse_request(request, server_instance)
    else:
        logging.info("Unknown method!")
        response = SimpleHTTPResponse()
        response.status = "Method Not Allowed"
        response.status_code = 405

        server_instance.response(
                response_data=SimpleHTTPResponse.prepare_response_bytes(response)
        )
