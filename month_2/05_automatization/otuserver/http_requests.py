import logging
from urllib import parse

logging.basicConfig(
        format='[%(asctime)s] %(levelname).1s %(message)s',
        level=logging.INFO, datefmt='%Y.%m.%d %H:%M:%S'
)


class HeaderCollector:
    @staticmethod
    def collect_headers(input_headers):
        result_headers = {}
        for header in input_headers:
            # According to 3.2 Header Fields (RFC7230) we have a header line with one ':'
            raw_header = header.split(":")
            hdr = raw_header[0]

            if not len(hdr) != 0:
                continue

            hdr_value = raw_header[1] if len(raw_header) > 1 else ""  # min len should be 2. if 1 then we have empty
            # header
            hdr_value = hdr_value.strip()
            result_headers[hdr] = hdr_value

        return result_headers


class SetAttributesFromBytes:
    @staticmethod
    def set_attributes(instance, byte_array):
        decoded_array = str(byte_array, "UTF-8")
        rows = decoded_array.split("\r\n")

        # According to 3.1 Start Line (RFC7230)
        start_line = rows[0].split(" ")
        setattr(instance, "method", start_line[0])
        setattr(instance, "protocol", start_line[2] if len(start_line) >= 2 else "")
        setattr(instance, "headers", HeaderCollector.collect_headers(rows[1:]))

        url = ""
        if len(start_line) >= 1:
            url = start_line[1]

        if "?" in url:
            question_index = url.find("?")
            setattr(instance, "URL", parse.unquote_plus(url[0:question_index]))
            setattr(instance, "query_parameters", url[question_index + 1:] if len(url) > question_index + 1 else "")
        else:
            setattr(instance, "URL", parse.unquote_plus(url))
            setattr(instance, "query_parameters", "")


class SimpleHTTPRequest:
    def __init__(self, request_byte_array):
        SetAttributesFromBytes.set_attributes(self, request_byte_array)

        for key, value in self.__dict__.items():
            logging.info(f"Attribute {key} has been set to value:\n{value}\n")
