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


class Field:
    """Basic field class"""

    def __init__(self, required=False, nullable=False):
        self.required = required
        self.empty = nullable
        self.value = None
        self.field_is_valid = None

    def validate_field(self, field_type):
        """
        Method to validate value of field from input.

        :param field_type: type of field
        :return: True | False | raise ValueError
        """
        if self.value is None:
            return self.check_field_is_required()

        if self.check_field_is_empty():
            return self.check_field_is_nullable()

        if not isinstance(self.value, field_type):
            type_of_field = " or ".join([field_t.__name__ for field_t in field_type]) \
                if isinstance(field_type, tuple) else field_type.__name__
            raise TypeError(f"Field must be {type_of_field.__name__} type!")

        return True

    def check_field_is_required(self):
        if self.required:
            raise ValueError(f"Field is required and should not be empty or None!")
        else:
            self.field_is_valid = True
            return self.field_is_valid

    def check_field_is_empty(self):
        return not self.value

    def check_field_is_nullable(self):
        if not self.empty:
            raise ValueError(f"Field is not nullable and should not be empty!")
        else:
            self.field_is_valid = True
            return self.field_is_valid


class CharField(Field):

    def validate_field(self):
        return super().validate_field(str)


class ArgumentsField(Field):

    def validate_field(self, input_value):
        return super().validate_field(dict)


class EmailField(CharField):

    def validate_field(self):
        super().validate_field()
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if self.field_is_valid is None:
            if re.match(email_pattern, str(self.value)):
                return True
            raise ValueError("Email validation failed!")

        return self.field_is_valid


class PhoneField(Field):

    def validate_field(self):
        super().validate_field((str, int))
        phone_pattern = r"^7[\d]{10}$"

        if self.field_is_valid is None:
            if re.match(phone_pattern, str(self.value)):
                return True
            raise ValueError("Phone validation failed!")

        return self.field_is_valid


class DateField(Field):

    def validate_field(self):
        super().field_is_valid(str)

        if self.field_is_valid is None:
            try:
                date = datetime.datetime.strptime(self.value, "%d.%m.%Y")
                return True
            except Exception:
                raise ValueError("Wrong date format!")

        return self.field_is_valid


class BirthDayField(DateField):

    def validate_field(self):
        super().field_is_valid()
        b_date = datetime.datetime.strptime(self.value, "%d.%m.%Y")
        now = datetime.datetime.now()

        if now.year - b_date.year <= MAX_AGE:
            return True
        else:
            raise ValueError(f"Maximum age of {MAX_AGE} is reached.")

        return self.field_is_valid


class GenderField(Field):

    def validate_field(self):
        super().validate_field(int)

        if self.field_is_valid is None:
            if self.value in GENDERS:
                return True
            else:
                raise ValueError(
                        f"Gender validation failed! Use numbers: unknown is {UNKNOWN}, male is {MALE}, female is "
                        f"{FEMALE}"
                )

    def check_field_is_empty(self):
        if self.value != 0:
            return super().check_field_is_empty()
        return False


class ClientIDsField(Field):

    def validate_field(self):
        super().validate_field(list)
        if self.field_is_valid is None:
            if not all(isinstance(number, int) for number in self.value):
                raise TypeError("Input value must be list of numbers!")
            return True

        return self.field_is_valid


class RequestMetaClass(type):
    """Metaclass for all requests. Creates attribute fields - list of Field type attributes"""

    def __new__(mcs, name, bases, attrs):
        fields = []
        for attribute in attrs:
            if isinstance(attrs.get(attribute), Field):
                fields.append(attribute)
        attrs.update({'fields': fields})
        return type.__new__(mcs, name, bases, attrs)


class Request(metaclass=RequestMetaClass):
    """Base request class"""

    def __init__(self, request, context=None, store=None):
        self._errors = []
        self.request = request
        self.context = context
        self.store = store

        self.save_values()

    def save_values(self):
        for field in self.fields:
            # attribute = getattr(self, field)
            getattr(self, field).value = self.request.get(field, None)

    def validate_fields(self):
        for field in self.fields:
            try:
                getattr(self, field).validate_field(field)
            except (TypeError, KeyError) as error:
                self._errors.append(f'Field "{field}" failed validation with error {error}!')

        return not self._errors

    def get_fields(self):
        fields_to_return = []

        for field in self.fields:
            if field.name in self.request and not field.check_field_is_empty():
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

    def validate_fields(self):
        if super().validate_fields():
            _fields = set(self.get_fields())
            validated_pairs = any(
                    [
                        _fields.issuperset(pair) for pair in self._pairs
                    ]
            )
            if not validated_pairs:
                error_msg = ' or '.join(str(pair) for pair in self._pairs)
                self._errors.append(f'Pairs {error_msg} shouldn\'t be empty!')
            else:
                return True

        return False


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

    def __init__(self, request, is_admin=False, context=None, store=None):
        self.request = request
        self.context = context
        self.is_admin = is_admin
        self.store = store

    @abstractmethod
    def create_request_instance(self):
        """Create request"""
        pass

    @abstractmethod
    def handle_request(self):
        """Logic of handler"""
        pass


class OnlineScoreRequestHandler(RequestHandler):

    def create_request_instance(self):
        return OnlineScoreRequest(self.request)

    def handle_request(self):
        request_obj = self.create_request_instance()

        logging.info("Starting fields validation.")
        if not request_obj.validate_fields():
            return request_obj.create_error_msg(), INVALID_REQUEST
        logging.info("Method fields are valid!")

        self.context['has'] = request_obj.get_fields()
        logging.info("Context is updated.")

        if self.is_admin:
            logging.info("Admin response.")
            return {'score': 42}, OK

        phone, email, birthday, gender, first_name, last_name = self.build_params_for_scoring(request_obj)
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
    def build_params_for_scoring(request_obj):
        phone = getattr(request_obj, 'phone', None)
        email = getattr(request_obj, 'email', None)
        birthday = getattr(request_obj, 'birthday', None)
        gender = getattr(request_obj, 'gender', None)
        first_name = getattr(request_obj, 'first_name', None)
        last_name = getattr(request_obj, 'last_name', None)

        return phone, email, birthday, gender, first_name, last_name


class ClientsInterestsRequestHandler(RequestHandler):

    def create_request_instance(self):
        return ClientsInterestsRequest(self.request)

    def handle_request(self):
        request_obj = self.create_request_instance()

        logging.info("Starting fields validation.")
        if not request_obj.validate_fields():
            return request_obj.create_error_msg(), INVALID_REQUEST
        logging.info("Method fields are valid!")

        self.context['nclients'] = len(request_obj.client_ids.value)
        logging.info("Context is updated.")

        response = {
            str(client_id): scoring.get_interests(None, client_id) for client_id in request_obj.client_ids.value
        }
        logging.info("Response is ready.")

        return response, OK


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode()).hexdigest()
    else:
        digest = hashlib.sha512((str(request.account.value) + str(request.login.value) + SALT).encode()).hexdigest()
    if digest == request.token.value:
        return True
    return False


def method_handler(request, ctx, store):
    handlers = {
        'online_score': OnlineScoreRequestHandler,
        'clients_interests': ClientsInterestsRequestHandler
    }
    request_body = request.get('body', None)

    if not request_body:
        return None, INVALID_REQUEST
    logging.info('Got request body!')

    request_obj = MethodRequest(request_body)
    if not request_obj.validate_fields():
        return request_obj.create_error_msg(), INVALID_REQUEST
    logging.info('Fields are valid!')

    if not check_auth(request_obj):
        return "Failed auth!", FORBIDDEN
    logging.info('Auth passed!')

    if request_obj.method.value in handlers:
        method_handler_cls = handlers.get(request_obj.method.value)
    else:
        return "No method found!", NOT_FOUND

    return method_handler_cls(request_obj.arguments.value, request_obj.is_admin, ctx, store).handle_request()


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
