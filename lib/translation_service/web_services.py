import json

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from .config import config
from .translation_service import TranslationService

desired_capabilities = dict(DesiredCapabilities.PHANTOMJS)
desired_capabilities['phantomjs.page.settings.userAgent'] = config['user_agent']

translation_service = TranslationService(
    poll_size=config['poll_size'],
    executable_path=config['phantomjs_bin'],
    desired_capabilities=desired_capabilities,
    service_args=config['service_args']
)

def _send_error(handler, error, status_code):
    response_data = {'error_type': type(error).__name__, 'error_msg': str(error)}
    
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(response_data))

def login(handler):
    request_data = json.loads(handler.rfile.read(int(handler.headers['Content-Length'])))

    kwargs = {
        'username': request_data['username'],
        'password': request_data['password']
    }

    try:
        result = translation_service.login(**kwargs)
    except ValueError, err:
        _send_error(handler, err, 401)  # Unauthorized. TODO: add WWW-Authenticate header (see https://tools.ietf.org/html/rfc7235#section-4.1)
    else:
        response_data = {'sid': result}

        handler.send_response(200)
        handler.send_header('Content-Type', 'application/json')
        handler.end_headers()
        handler.wfile.write(json.dumps(response_data))

def logout(handler):
    request_data = json.loads(handler.rfile.read(int(handler.headers['Content-Length'])))

    kwargs = {
        'sid': request_data['sid']
    }

    try:
        translation_service.logout(**kwargs)
    except (ValueError, AssertionError), err:
        _send_error(handler, err, 401)  # Unauthorized. TODO: add WWW-Authenticate header (see https://tools.ietf.org/html/rfc7235#section-4.1)
    else:
        handler.send_response(200)
        handler.end_headers()

def translate(handler):
    request_data = json.loads(handler.rfile.read(int(handler.headers['Content-Length'])))

    kwargs = {
        'sid': request_data['sid'],
        'string': request_data['string'],
        'src_lang': request_data['src_lang'],
        'target_lang': request_data['target_lang']
    }

    if 'sync' in request_data:
        kwargs['sync'] = request_data['sync']

    try:
        result = translation_service.translate(**kwargs)
    except (ValueError, AssertionError), err:
        _send_error(handler, err, 401)  # Unauthorized. TODO: add WWW-Authenticate header (see https://tools.ietf.org/html/rfc7235#section-4.1)
    else:
        if 'sync' in kwargs and kwargs['sync']:
            response_data = {'result': result}
        else:
            response_data = {'uuid': result}

        handler.send_response(200)
        handler.send_header('Content-Type', 'application/json')
        handler.end_headers()
        handler.wfile.write(json.dumps(response_data))


def poll(handler):
    request_data = json.loads(handler.rfile.read(int(handler.headers['Content-Length'])))

    kwargs = {
        'sid': request_data['sid']
    }
    
    if 'uuid' in request_data:
        kwargs['uuid'] = request_data['uuid']

    try:
        result = translation_service.poll(**kwargs)
    except (ValueError, AssertionError), err:
        _send_error(handler, err, 401)  # Unauthorized. TODO: add WWW-Authenticate header (see https://tools.ietf.org/html/rfc7235#section-4.1)
    except KeyError, err:
        _send_error(handler, err, 404)
    else:
        response_data = {'result': result}

        handler.send_response(200)
        handler.send_header('Content-Type', 'application/json')
        handler.end_headers()
        handler.wfile.write(json.dumps(response_data))


def cancel(handler):
    request_data = json.loads(handler.rfile.read(int(handler.headers['Content-Length'])))

    kwargs = {
        'sid': request_data['sid']
    }
    
    if 'uuid' in request_data:
        kwargs['uuid'] = request_data['uuid']

    try:
        translation_service.cancel(**kwargs)
    except (ValueError, AssertionError), err:
        _send_error(handler, err, 401)  # Unauthorized. TODO: add WWW-Authenticate header (see https://tools.ietf.org/html/rfc7235#section-4.1)
    except KeyError, err:
        _send_error(handler, err, 404)
    else:
        handler.send_response(200)
        handler.end_headers()
