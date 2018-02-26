import time
import Queue

from . import session
from . import translator
from . import translation_task
from .config import config


def _validate_session(instance_method):
    def session_validator(self, sid, *args, **kwargs):
        if sid not in self._sessions:
            raise ValueError('invalid sid')
        if self._sessions[sid].is_expired():
            del self._sessions[sid]
            raise AssertionError('expired session')
        
        return instance_method(self, sid, *args, **kwargs)
    return session_validator


class TranslationService(object):
    def __init__(self, poll_size=15, queue_size=0, executable_path=None,
                                                    desired_capabilities=None,
                                                    service_args=None,
                                                    google_translate_url=None,
                                                    window_size=None):

        self._poll = []
        self._queue = Queue.Queue(queue_size)
        self._sessions = {}

        for i in xrange(poll_size):
            kwargs = {}

            if executable_path is not None:
                kwargs['executable_path'] = executable_path
            if desired_capabilities is not None:
                kwargs['desired_capabilities'] = dict(desired_capabilities)
            if service_args is not None:
                kwargs['service_args'] = list(service_args)
            if google_translate_url is not None:
                kwargs['google_translate_url'] = google_translate_url
            if window_size is not None:
                kwargs['window_size'] = tuple(window_size)

            self._poll.append(translator.Translator(self._queue, **kwargs))

    def login(self, username, password):
        if username not in config['passwd_db'] or config['passwd_db'][username] != password:
            raise ValueError('invalid username or password')
        
        for sid, s in self._sessions.iteritems():
            if s['username'] == username:
                s.set_expiration_time(time.time() + config['session_duration'])
                return sid
        
        s = session.Session(
            expiration_time=time.time() + config['session_duration'],
            username=username,
            async_tasks={}
        )
        
        self._sessions[s.get_id()] = s
        return s.get_id()
    
    @_validate_session
    def logout(self, sid):
        self._sessions[sid].expire()
        del self._sessions[sid]

    @_validate_session
    def translate(self, sid, string, src_lang, target_lang, sync=False):
        task = translation_task.Translate(string, src_lang, target_lang)
        self._queue.put(task)

        if sync:
            return task.get_result()

        self._sessions[sid]['async_tasks'][task.get_uuid()] = task
        return task.get_uuid()

    @_validate_session
    def poll(self, sid, uuid=None):
        if uuid:
            if uuid not in self._sessions[sid]['async_tasks']:
                raise KeyError('invalid uuid')
            
            task = self._sessions[sid]['async_tasks'][uuid]

            if task.is_result():
                result = task.get_result()
                del self._sessions[sid]['async_tasks'][uuid]
                return result
            return None
        else:
            if not self._sessions[sid]['async_tasks']:
                raise KeyError('there is no tasks')
            
            results = {}
            
            for uuid, task in self._sessions[sid]['async_tasks'].items():
                if task.is_result():
                    result = task.get_result()
                    del self._sessions[sid]['async_tasks'][uuid]
                    results[uuid] = result
            
            if results:
                return results
            return None

    @_validate_session
    def cancel(self, sid, uuid=None):
        if uuid:
            if uuid not in self._sessions[sid]['async_tasks']:
                raise KeyError('invalid uuid')
            
            task = self._sessions[sid]['async_tasks'][uuid]
            task.cancel()
            del self._sessions[sid]['async_tasks'][uuid]
        else:
            if not self._sessions[sid]['async_tasks']:
                raise KeyError('there is no tasks')
            
            for uuid, task in self._sessions[sid]['async_tasks'].items():
                task.cancel()
                del self._sessions[sid]['async_tasks'][uuid]

    def start(self):
        for t in self._poll:
            t.start()

    def stop(self):
        for i in xrange(len(self._poll)):
            self._queue.put(None)

        self._queue.join()

        for t in self._poll:
            t.join()
