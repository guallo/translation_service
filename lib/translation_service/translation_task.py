import uuid
import time
import threading

from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys


PROGRESS_MARK = u'...'


class CSSSelector(object):
    SOURCE_INPUT = u'#source'
    TRANSLATIONS = u'.tlid-translation'
    TRANSLATION_GENDER_INDICATORS = u'.tlid-translation-gender-indicator'
    TRANSLATION_VERIFIED_BUTTONS = u'.tlid-trans-verified-button'
    SRC_LANG_BUTTON_TPL = u'.sl-wrap [role="button"][value="{}"]'
    TARGET_LANG_BUTTON_TPL = u'.tl-wrap [role="button"][value="{}"]'
    CHECKED_LANG_BUTTONS = u'.jfk-button-checked'


class TranslationTask(object):
    def __init__(self):
        self._uuid = str(uuid.uuid4())
        self._result = None
        self._mutex = threading.Semaphore(0)
        self._attempted_set = False
        self._attempted_get = False
        self._cancelled = False

    def get_uuid(self):
        return self._uuid

    def set_result(self, result):
        assert not self._attempted_set
        self._attempted_set = True

        self._result = result
        self._mutex.release()

    def get_result(self):
        assert not self._attempted_get
        self._attempted_get = True

        self._mutex.acquire()
        return self._result

    def is_result(self):
        return self._attempted_set

    def do(self, driver):
        if not self._cancelled:
            result = self._do(driver)
            self.set_result(result)

    def _do(self, driver):
        raise NotImplementedError('Should be implemented by subclasses')

    def cancel(self):
        self._cancelled = True


class Translate(TranslationTask):
    def __init__(self, string, src_lang, target_lang):
        super(self.__class__, self).__init__()

        self.string = self._clean_string(string)
        self.src_lang = src_lang
        self.target_lang = target_lang
    
    def _clean_string(self, string):
        string = string.strip()
        while string.endswith(PROGRESS_MARK):
            string = string[:-len(PROGRESS_MARK)].rstrip()
        return string

    def _do(self, driver):
        if not self.string:
            return ''
        
        self._clear_source_input(driver)
        self._wait_until_result_box_is_clear(driver)

        self._set_src_lang(driver)
        self._set_target_lang(driver)

        source_input = driver.find_element_by_css_selector(CSSSelector.SOURCE_INPUT)
        source_input.send_keys(self.string)

        self._wait_until_translated(driver)

        driver.save_screenshot(threading.currentThread().getName() + '-translate-screenshot.png')
        return self._get_result_box_text(driver)

    def _set_src_lang(self, driver):
        src_lang_button = driver.find_element_by_css_selector(
            CSSSelector.SRC_LANG_BUTTON_TPL.format(self.src_lang)
        )
        checked_lang_buttons = driver.find_elements_by_css_selector(
            CSSSelector.CHECKED_LANG_BUTTONS
        )
        
        if src_lang_button in checked_lang_buttons:
            return
        src_lang_button.click()

    def _set_target_lang(self, driver):
        target_lang_button = driver.find_element_by_css_selector(
            CSSSelector.TARGET_LANG_BUTTON_TPL.format(self.target_lang)
        )
        checked_lang_buttons = driver.find_elements_by_css_selector(
            CSSSelector.CHECKED_LANG_BUTTONS
        )
        
        if target_lang_button in checked_lang_buttons:
            return
        target_lang_button.click()

    def _clear_source_input(self, driver):
        source_input = driver.find_element_by_css_selector(CSSSelector.SOURCE_INPUT)

        while source_input.get_attribute('value'):
            source_input.send_keys(Keys.BACKSPACE)

    def _wait_until_result_box_is_clear(self, driver):
        translations = driver.find_elements_by_css_selector(CSSSelector.TRANSLATIONS)

        while translations:
            time.sleep(0.1)

    def _wait_until_translated(self, driver):
        def get_first_translation_text():
            try:
                return self._get_result_boxs_elements(driver)[0][0].text
            except (IndexError, exceptions.StaleElementReferenceException), e:
                return u''

        while (not get_first_translation_text() 
                or get_first_translation_text().endswith(PROGRESS_MARK)):
            time.sleep(0.1)
    
    def _get_result_box_text(self, driver):
        translations, genders, verifications = self._get_result_boxs_elements(driver)
        text = u''
        
        for i in range(len(translations)):
            translation_text = translations[i].text
            gender_text = genders[i].text if len(genders) > i else u''
            verification_text = (u'\u2714' if len(verifications) > i 
                and verifications[i].is_displayed() else u'')
            
            text += u'\n' if text else u''
            text += translation_text + gender_text + verification_text
        
        return text
    
    def _get_result_boxs_elements(self, driver):
        translations = driver.find_elements_by_css_selector(
            CSSSelector.TRANSLATIONS
        )
        genders = driver.find_elements_by_css_selector(
            CSSSelector.TRANSLATION_GENDER_INDICATORS
        )
        verifications = driver.find_elements_by_css_selector(
            CSSSelector.TRANSLATION_VERIFIED_BUTTONS
        )
        
        return (translations, genders, verifications)
