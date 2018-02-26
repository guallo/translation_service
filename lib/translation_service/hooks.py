from .web_services import translation_service


def start_translation_service():
    translation_service.start()


def stop_translation_service():
    translation_service.stop()
