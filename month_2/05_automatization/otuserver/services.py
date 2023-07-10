import mimetypes
import os

from os import path

from http_response import SimpleHTTPResponse
from http_requests import SimpleHTTPRequest
from simple_server import SimpleHTTPServer


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
    Parse request and call directory handling.
    :param server: server class instance
    :param request: initially processed request
    """
    requested_path = path.abspath(server.doc_root + request.URL)
    _head = False

    body = ""
    response = SimpleHTTPResponse()

    if request.method == "HEAD":
        _head = True

    if path.exists(requested_path) and "../" not in request.URL:
        if path.isfile(requested_path) and not request.URL.endswith("/"):
            with open(requested_path, 'rb') as file:
                body = file.read()
            file_name, file_extention = path.splitext(requested_path)
            content_type = mimetypes.types_map[file_extention]
            response.headers["Content-Type"] = content_type
            response.headers["Content-Length"] = len(body)
            if not _head:
                response.body = body
        elif index(requested_path):
            body = b"<html>Directory index file</html>"
            response.headers["Content-Type"] = "txt/html"
            response.headers["Content-Length"] = len(body)
            if not _head:
                response.body = body
        else:
            response.status = "NOT FOUND"
            response.status_code = 404
    else:
        response.status = "NOT FOUND"
        response.status_code = 404

    server.response(SimpleHTTPServer.response(response_data=response), _head)


def request_processor(request_bytes: bytes, server_instance: SimpleHTTPServer) -> None:
    """
    Get request and start to parse it depending on request.method.
    :param request_bytes: bytes from request stream
    :param server_instance: server
    """
    request = SimpleHTTPRequest(request_byte_array=request_bytes)

    if request.method == "HEAD" or request.method == "GET":
        parse_request(request, server_instance)
    else:
        response = SimpleHTTPResponse()
        response.status = "Method Not Allowed"
        response.status_code = 405

        server_instance.response(
                response_data=SimpleHTTPResponse.prepare_response_bytes(response)
        )
