import json
from enum import Enum

from django.http import Http404
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist

from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, NotFound
from lottery.renderer import CentralizedResponseRenderer
CODE_OFFSET = 1000
class ErrorWrapper:
    def __init__(self, code, message):
        self.code = code
        self.message = message


class ErrorEnum(Enum):
    BAD_REQUEST = \
        ErrorWrapper(4000000, 'Bad request')
    INVALID_JSON_PAYLOAD = \
        ErrorWrapper(4000001, 'Invalid JSON payload')
    ROLE_UPDATE_FAIL = \
        ErrorWrapper(4000002, 'Client or guest cannot change role')
    HAS_VERIFIED = \
        ErrorWrapper(4000003, 'User has verified')
    IS_NOT_ACTIVE = \
        ErrorWrapper(4000004, 'User is not active')
    NAME_IS_EXISTS = \
        ErrorWrapper(4000005, 'Comany name already exists')
    CATEGORY_IS_EXISTS = \
        ErrorWrapper(4000006, 'Duplicated category name')
    CATEGORY_CREATE_FAIL = \
        ErrorWrapper(4000007, 'Can not add category here')
    FOLDER_WITH_SAME_NAME = \
        ErrorWrapper(4000008, 'Duplicated folder name')
    FILE_WITH_SAME_NAME = \
        ErrorWrapper(4000009, 'Duplicated file name')
    LOGIN_REQUIRED = \
        ErrorWrapper(4010001, 'Login required')
    INVALID_TOKEN = \
        ErrorWrapper(4010002, 'Invalid token')
    FORBIDDEN = \
        ErrorWrapper(4030000, 'Forbidden')
    CAN_NOT_DELETED = \
        ErrorWrapper(4030001, 'Root company can not be deleted')
    NOT_FOUND = \
        ErrorWrapper(4040000, 'Not found')
    BLUB_NOT_FOUND = \
        ErrorWrapper(4040001, 'File not found in bucket')
    FOLDER_NOT_FOUND = \
        ErrorWrapper(4040002, 'Folder not found')
    CONFLICT = \
        ErrorWrapper(4090000, 'Conflict')
    INTERNAL_SERVER_ERROR = \
        ErrorWrapper(5000000, 'Internal server error')


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = None
    default_code = ErrorEnum.BAD_REQUEST


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = None
    default_code = ErrorEnum.CONFLICT


def get_first_error_code(codes):
    if isinstance(codes, list):
        return get_first_error_code(codes[0]) if any(codes) else None
    elif isinstance(codes, dict):
        if not any(codes):
            return None
        return get_first_error_code(next(iter(codes.values())))
    return codes


def handler(exc, context):
    error_detail = getattr(exc, 'detail', exc)
    try:
        error_detail = json.loads(json.dumps(error_detail))
    except TypeError:
        error_detail = str(error_detail)

    def check_if_is_useful_detail(detail):
        return any(detail) and (not detail == 'None')

    def pick_code_message(detail, err_enum):
        error = err_enum.value
        is_readable_detail = \
            isinstance(detail, str) and check_if_is_useful_detail(detail)
        return error.code, detail if is_readable_detail else error.message

    if isinstance(exc, APIException):
        first_code = get_first_error_code(exc.get_codes())
        if isinstance(first_code, ErrorEnum):
            error = first_code.value
            error_code = error.code
            error_message = error.message
        else:
            error_code = exc.status_code * CODE_OFFSET
            error_message = error_detail \
                if isinstance(error_detail, str) else exc.default_detail
    elif isinstance(exc, Http404):
        error_code, error_message = \
            pick_code_message(error_detail, ErrorEnum.NOT_FOUND)
    elif isinstance(exc, PermissionDenied):
        error_code, error_message = \
            pick_code_message(error_detail, ErrorEnum.FORBIDDEN)
    else:
        if isinstance(exc, ObjectDoesNotExist):
            exc = NotFound()
            error_code, error_message = \
                pick_code_message(error_detail, ErrorEnum.NOT_FOUND)
        else:
            exc = APIException()
            error_code, error_message = \
                pick_code_message(
                    error_detail, ErrorEnum.INTERNAL_SERVER_ERROR)

    if error_detail == error_message or not check_if_is_useful_detail(error_detail):
        error_detail = None

    request = context['request']
    response = exception_handler(exc, context)
    payload = {
        'error': {
            'code': error_code,
            'message': error_message,
            'detail': error_detail
        }
    }

    response.data = payload
    # add needed attributes for CentralizedResponseRenderer
    response.accepted_renderer = CentralizedResponseRenderer()
    response.accepted_media_type = "application/json"
    response.renderer_context = {'request': request}
    response.render()
    return response