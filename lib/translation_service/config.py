import os

_RELATIVE_ROOT_DIR = os.path.join(os.pardir, os.pardir)
_ABS_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), _RELATIVE_ROOT_DIR))
_ABS_BIN_DIR = os.path.join(_ABS_ROOT_DIR, 'bin')

config = {
    'urlmap': [
        # (method pattern, URL pattern, handler name from `web_services.py')
        (r'POST', r'^/login', 'login'),
        (r'POST', r'^/logout', 'logout'),
        (r'POST', r'^/translate', 'translate'),
        (r'POST', r'^/poll', 'poll'),
        (r'POST', r'^/cancel', 'cancel'),
    ],
    'poll_size': 10,
    'wait_for_incoming_request_timeout': 0.5,  # in seconds
    # server hooks from `hooks.py'
    'on_server_start': [
        'start_translation_service'
    ],
    'on_server_stop': [
        'stop_translation_service'
    ],
    # browser
    'phantomjs_bin': os.path.join(_ABS_BIN_DIR, 'phantomjs-2.1.1-linux-x86_64', 'bin', 'phantomjs'),
    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/52.0.2743.116 Chrome/52.0.2743.116 Safari/537.36',
    'service_args': [
        '--ignore-ssl-errors=true', 
        '--ssl-protocol=any'
    ],
    'window_size': (1366, 768),
    'google_translate_url': 'https://translate.google.com/',
    # session
    'session_duration': 300,  # max seconds without touch'ing the session before it expires
    'passwd_db': {
        # 'username': 'password'
        'user1': 'passwd1',
    },
}
