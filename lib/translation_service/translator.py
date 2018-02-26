import threading

from selenium.webdriver import PhantomJS

from .config import config


class Translator(threading.Thread):
    def __init__(self, queue, executable_path=None,
                              desired_capabilities=None,
                              service_args=None,
                              google_translate_url=config['google_translate_url'],
                              window_size=config['window_size']):

        super(self.__class__, self).__init__()
        self._queue = queue

        kwargs = {}

        if executable_path is not None:
            kwargs['executable_path'] = executable_path
        if desired_capabilities is not None:
            kwargs['desired_capabilities'] = desired_capabilities
        if service_args is not None:
            kwargs['service_args'] = service_args

        self._driver = PhantomJS(**kwargs)
        self._driver.set_window_size(*window_size)
        self._driver.get(google_translate_url)

    def run(self):
        while True:
            task = self._queue.get()

            if task is None:
                self._queue.task_done()
                self._driver.quit()
                break

            task.do(self._driver)
            self._queue.task_done()
