#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import re
from abc import ABC, abstractmethod
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import BaseHTTPRequestHandler, HTTPServer

import scoring

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}
MAX_AGE = 70


class Field(ABC):
    """Basic field class"""

    def __init__(self, required=False, nullable=False):
        self.required = required
        self.empty = nullable

    @abstractmethod
    def validate_field(self, input_value):
        pass


class CharField(Field):

    def validate_field(self, input_value):
        if isinstance(input_value, str):
            return input_value
        raise ValueError("Expected string type on input!")


class ArgumentsField(Field):

    def validate_field(self, input_value):
        if isinstance(input_value, dict):
            return input_value
        raise ValueError("Expected dict type on input!")


class EmailField(CharField):

    def validate_field(self, input_value):
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(email_pattern, str(input_value)):
            return input_value
        raise ValueError("Email validation failed!")


class PhoneField(Field):

    def validate_field(self, input_value):
        phone_pattern = r"^7[\d]{10}$"
        if re.match(phone_pattern, str(input_value)):
            return input_value
        raise ValueError("Phone validation failed!")


class DateField(Field):

    def validate_field(self, input_value):
        try:
            date = datetime.datetime.strptime(input_value, "%d.%m.%Y")
        except Exception:
            raise ValueError("Wrong date format!")
        return date


class BirthDayField(DateField):

    def validate_field(self, input_value):
        b_date = super().validate_field(input_value)
        now = datetime.datetime.now()
        if now.year - b_date.year <= MAX_AGE:
            return b_date
        raise ValueError(f"Maximum age of {MAX_AGE} is reached.")


class GenderField(Field):

    def validate_field(self, input_value):
        gender_enum = [UNKNOWN, MALE, FEMALE]
        if input_value in gender_enum:
            return input_value
        raise ValueError(
                f"Gender validation failed! Use numbers: unknown is {UNKNOWN}, male is {MALE}, female is "
                f"{FEMALE}"
        )


class ClientIDsField(Field):

    def validate_field(self, input_value):
        if not isinstance(input_value, list):
            raise ValueError("Input value must be a list!")
        if not all(isinstance(number, int) for number in input_value):
            raise ValueError("Input value must be list of numbers!")
        return input_value


class RequestMetaClass(type):
    """Metaclass for all requests"""

    def __new__(mcs, name, bases, attrs):
        fields = []
        for key, attribute in attrs.items():
            if isinstance(attribute, Field):
                attribute.name = key
                fields.append(attribute)
        attrs.update({'fields': fields})
        return type.__new__(mcs, name, bases, attrs)


class Request(metaclass=RequestMetaClass):
    """Base request class"""

    def __init__(self, request):
        self._empty = (None, '', [], {}, ())
        self._errors = []
        self._has_errors = True
        self.request = request

    def validate_and_save_fields(self):
        for field in self.fields:
            try:
                value = self.request[field.name]
            except (TypeError, KeyError):
                if field.required:
                    self._errors.append(f'Field "{field}" is required!')
                    continue

            if value in self._empty and not field.empty:
                self._errors.append(f'Field "{field}" should not be empty!')

            try:
                if value not in self._empty:
                    value = field.validate_field(value)
                    setattr(self, field.name, value)
            except ValueError as exc:
                self._errors.append(f'Field "{field}" raised exception: {exc}')

        return self._errors

    def is_valid(self):
        if self._errors:
            self._has_errors = True

        return self._has_errors

    def get_fields(self):
        fields_to_return = []

        for field in self.fields:
            if field.name in self.request and field.name not in self._empty:
                fields_to_return.append(field.name)

        return fields_to_return

    def create_error_msg(self):
        return ', '.join(self._errors)


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Request):
    _pairs = (
        ('phone', 'email'),
        ('first_name', 'last_name'),
        ('birthday', 'gender')
    )

    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __init__(self, request):
        self._errors = super().validate_and_save_fields()

    def validate_and_save_fields(self):
        _fields = set(self.get_fields())
        validated_pairs = any(
                [
                    _fields.issuperset(pair) for pair in self._pairs
                ]
        )
        if not validated_pairs:
            error_msg = ' or '.join(str(pair) for pair in self._pairs)
            self._errors.append(f'Pairs {error_msg} shouldn\'t be empty')

        return self._errors


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class RequestHandler(ABC):
    """Request handler abstract class"""

    def __init__(self, request, context):
        self.request = request
        self.context = context

    @abstractmethod
    def create_request(self, data):
        """Create request"""
        pass

    @abstractmethod
    def request_handler(self, request_type):
        """Logic of handler"""
        pass

    def start_processing(self, data):
        request_type = self.create_request(data)

        if not request_type.is_valid():
            return request_type.create_error_msg(), INVALID_REQUEST

        return self.request_handler(request_type)


class OnlineScoreRequestHandler(RequestHandler):

    def create_request(self, data):
        return OnlineScoreRequest(data)

    def request_handler(self, request_type):
        self.context['has'] = request_type.get_fields()

        if self.request.is_admin:
            return {'score': 42}, OK

        phone, email, birthday, gender, first_name, last_name = self.create_request()
        response = dict(
                score=scoring.get_score(
                        None,
                        phone,
                        email,
                        birthday,
                        gender,
                        first_name,
                        last_name
                )
        )

        return response, OK

    @staticmethod
    def build_params_for_scoring(request_type):
        phone = getattr(request_type, 'phone', None)
        email = getattr(request_type, 'email', None)
        birthday = getattr(request_type, 'birthday', None)
        gender = getattr(request_type, 'gender', None)
        first_name = getattr(request_type, 'first_name', None)
        last_name = getattr(request_type, 'last_name', None)

        return phone, email, birthday, gender, first_name, last_name


class ClientsInterestsRequestHandler(RequestHandler):

    def create_request(self, data):
        return ClientsInterestsRequest(data)

    def request_handler(self, request_type):
        response = {
            client_id: scoring.get_interests(None, client_id) for client_id in request_type.client_ids
        }
        self.context['nclients'] = len(request_type.client_ids)

        return response, OK


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode()).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode()).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    handlers = {
        'online_score': OnlineScoreRequestHandler,
        'clients_interests': ClientsInterestsRequestHandler
    }
    return_code = INVALID_REQUEST
    request_body = request.get('body')

    if request_body:
        logging.info('Got request body!')
        request_new = MethodRequest(request_body)
        request_new.validate_and_save_fields()

        if request_new.is_valid():
            logging.info('Request is valid!')
            auth = check_auth(request_new)
            return_code = FORBIDDEN

            if auth:
                if request_new.method in handlers:
                    return handlers[request.method](request, ctx).start_processing(request.arguments)
                else:
                    return_code = NOT_FOUND
                    return None, return_code

            return None, return_code
        else:
            return request_new.create_error_msg(), return_code

    return None, return_code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
            filename=opts.log, level=logging.INFO,
            format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S'
    )
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
