import json

from flask import request
from werkzeug.exceptions import HTTPException


class BaseResponse(HTTPException):
    code = 500
    payload = {'message': 'Server Error'}
    headers = [("Content-Type", "application/json")]

    def __init__(self, code=None, payload=None, headers=None, message=None):
        if code is not None:
            self.code = code
        if message is not None:
            self.payload = {'message': message}
        if payload is not None:
            self.payload = self.__parse_payload(payload)
        if headers is not None:
            self.headers = headers
        super(BaseResponse, self).__init__()

    def get_body(self, environ=None):
        body = {
            'code': self.code,
            'payload': self.payload,
            'request': self.get_request_url_without_params()
        }
        json_body = json.dumps(body)
        return json_body

    def __parse_payload(self, payload):
        if isinstance(payload, dict):
            return self.__parse_dict_payload(payload)
        elif isinstance(payload, list) or isinstance(payload, tuple):
            return self.__parse_iterable_payload(payload)
        else:
            from app.db import db
            if isinstance(payload, db.Model):
                return self.__parse_model_payload(payload)
            else:
                return payload

    def __parse_dict_payload(self, dict_payload):
        parsed_payload = {}
        for item in dict_payload.items():
            item_key = item[0]
            item_value = item[1]
            item_value = self.__parse_payload(item_value)
            parsed_payload[item_key] = item_value
        return parsed_payload

    def __parse_iterable_payload(self, iterable_payload):
        parsed_payload = []
        for item in iterable_payload:
            parsed_payload.append(self.__parse_payload(item))
        return parsed_payload

    @staticmethod
    def __parse_model_payload(model_payload):
        model_name = model_payload.__class__.__name__
        tmp = __import__('app.db.serializer', fromlist=[model_name + 'Schema'])
        schema_class = tmp.__getattribute__(model_name + 'Schema')
        schema = schema_class()
        return schema.dump(model_payload)

    @staticmethod
    def get_request_url_without_params():
        full_path = str(request.full_path)
        cleaned_path = full_path.split('?')[0]
        return cleaned_path

    def get_headers(self, environ=None):
        return self.headers


class Success(BaseResponse):
    code = 200
    payload = {'message': 'Success'}


class Fail(BaseResponse):
    code = 400
    payload = {'message': 'Fail'}


class ValidationError(BaseResponse):
    code = 400
    payload = {'message': 'Invalid params'}


class ServerError(BaseResponse):
    code = 500
    payload = {'message': 'Server error'}


class AuthError(BaseResponse):
    code = 403
    payload = {'message': 'Please login'}


class PageNotFound(BaseResponse):
    code = 404
    payload = {'message': 'Page not found'}
