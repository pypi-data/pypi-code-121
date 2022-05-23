import os

import selenium
from webdriver_setup import get_webdriver_for
from pyshadow.main import Shadow

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GoogleDriver:
    DEFAULT_DIR = os.path.join('~', '.config', 'google-webdriver')
    SIGNINGIN_ELEMENT_IDS = ['captchaimg', 'gaia_loginform']
    SIGNEDIN_ELEMENT_IDS = ['wiz_jd']
    def _id_exists(ids):
        def ec(webdriver):
            return any((webdriver.find_elements_by_id(id) for id in ids))
        return ec
    def __init__(self, engine = 'firefox', dir = None):
        if dir is None:
            dir = GoogleDriver.DEFAULT_DIR
        dir = os.path.expanduser(dir)
        self.engine = engine
        self.dir = os.path.join(dir, self.engine, '')
        self.create()
    def create(self):
        os.makedirs(self.dir, exist_ok=True)
        try:
            if self.engine == 'firefox':
                options = selenium.webdriver.FirefoxOptions()
                options.profile = self.dir
                options.headless = True
                #ff_options.add_argument('--headless')
                self.webdriver = get_webdriver_for('firefox', options=options)
                self.webdriver.get('https://accounts.google.com/')
                WebDriverWait(self.webdriver, 10).until(GoogleDriver._id_exists(GoogleDriver.SIGNINGIN_ELEMENT_IDS + GoogleDriver.SIGNEDIN_ELEMENT_IDS))
                if GoogleDriver._id_exists(GoogleDriver.SIGNINGIN_ELEMENT_IDS)(self.webdriver):
                    # not logged in
                    raise Exception('Not logged in.  Please run this, login, exit, and try again: XRE_PROFILE_PATH="' + self.dir + '" firefox https://accounts.google.com')
            elif self.engine == 'chrome':
                options = selenium.webdriver.ChromeOptions()
                options.add_argument('--user-data-dir=' + self.dir)
                #options.add_argument('--enable-logging')
                #options.headless = True
                self.webdriver = get_webdriver_for('chrome', options=options)
                self.webdriver.get('https://accounts.google.com/')
                WebDriverWait(self.webdriver, 10).until(GoogleDriver._id_exists(GoogleDriver.SIGNINGIN_ELEMENT_IDS + GoogleDriver.SIGNEDIN_ELEMENT_IDS))
                if GoogleDriver._id_exists(GoogleDriver.SIGNINGIN_ELEMENT_IDS)(self.webdriver):
                    # not logged in
                    raise Exception('Not logged in.  Please run this or similar, login, exit, and try again: google-chrome --user-data-dir="' + self.dir + '" https://accounts.google.com')
            else:
                raise Exception('unimplemented engine:', engine)
        except selenium.common.exceptions.TimeoutException:
            print(self.webdriver.execute_script('return Array.prototype.map.call(document.querySelectorAll("*[id]"), x=>x.id)'))
            raise Exception("element ids unrecognised, please update SIGNINGIN_ELEMENT_IDS and SIGNEDIN_ELEMENT_IDS in source code to reflect element ids that indicate needing to sign or, or being signed in, at https://accounts.google.com/ .  Ids in a page can be found in the developer console in a web browser using hardcoded element ids in source code using: console.log(JSON.stringify(Array.prototype.map.call(document.querySelectorAll('*[id]'), x=>x.id))).  Here's the current list: " + self.webdriver.execute_script('return Array.prototype.map.call(document.querySelectorAll("*[id]"), x=>x.id)'))
        return self.webdriver

class GoogleDriverChrome(GoogleDriver):
    def __init__(self, dir = GoogleDriver.DEFAULT_DIR):
        super().__init__('chrome', dir)

class GoogleDriverFirefox(GoogleDriver):
    def __init__(self, dir = GoogleDriver.DEFAULT_DIR):
        super().__init__('firefox', dir)
        
class Colab:
    # these are collected here to make them easy to update
    def BASEURL():
        return 'https://colab.research.google.com/'

    def NEW_NOTEBOOK(webdriver):
        webdriver.get(Colab.BASEURL() + '#create=true')

    def CONDITIONS_NOTEBOOK_LOADED():
        return EC.presence_of_element_located((By.ID, 'doc-name'))

    def GET_NOTEBOOK_NAME(webdriver):
        return webdriver.find_element_by_id('doc-name').get_attribute('value')

    def SET_NOTEBOOK_NAME(webdriver, newname):
        name = webdriver.find_element_by_id('doc-name')
        name.clear()
        name.send_keys(newname, Keys.RETURN)
        return name.get_attribute('value')

    def CELL_ELEMENTS(webdriver):
        return webdriver.find_elements_by_class_name('cell')

    def FIELD_ELEMENTS(cell_element):
        return cell_element.find_elements_by_css_selector('colab-form-input,colab-form-dropdown')

    def INSERT_CELL_BELOW_CURRENT(webdriver):
        webdriver.find_element_by_id('toolbar-add-code').click()

    def RUN_CELL(webdriver, shadow, cell_element):
        cell_element.click()
        outer = cell_element.find_element_by_tag_name('colab-run-button')
        inner = shadow.find_element(outer, '.cell-execution')
        inner.click()

    def IS_RUN_COMPLETE(webdriver, shadow, cell_element):
        outer = cell_element.find_element_by_tag_name('colab-run-button')
        # div id status
        return bool(shadow.find_elements(outer, '#status'))

    def GET_CELL_TEXT(cell_element):
        try:
            return cell_element.find_element_by_tag_name('textarea').get_attribute('value')
        except:
            return cell_element.find_element_by_class_name('main-content').text

    def TO_CELL_OUTPUT(webdriver, cell_element, handler):
        output = cell_element.find_element_by_class_name('output')
        iframes = output.find_elements_by_tag_name('iframe')
        if iframes:
            try:
                webdriver.switch_to.default_content()
                webdriver.switch_to.frame(iframes[0])
                return handler(webdriver.find_element_by_id('output-body'))
            except:
                # seems an exception can be thrown when the iframe disappears
                pass
            finally:
                webdriver.switch_to.default_content()
        renderers = output.find_elements_by_tag_name('colab-static-output-renderer')
        if renderers:
            return handler(renderers[0])
        else:
            return handler(output)

    def GET_CELL_OUTPUT(webdriver, cell_element):
        return Colab.TO_CELL_OUTPUT(webdriver, cell_element, lambda element: element.text)

    def GET_CELL_IMGS(webdriver, cell_element):
        def elem2imgs(elem):
            return [
                img.get_attribute('src')
                for img in elem.find_elements_by_tag_name('img')
            ]
        return Colab.TO_CELL_OUTPUT(webdriver, cell_element, elem2imgs)

    def GENERATE_CELL_OUTPUT(webdriver, shadow, cell_element):
        last_output = None
        next_output = None
        def output_changed(webdriver):
            nonlocal last_output, next_output
            next_output = Colab.GET_CELL_OUTPUT(webdriver, cell_element)   
            dialog_title = Colab.DIALOG_MESSAGE(webdriver, shadow)
            if next_output != last_output or Colab.IS_RUN_COMPLETE(webdriver, shadow, cell_element):
                return True
            elif dialog_title is not None:
                Colab.CLOSE_DIALOG(webdriver, shadow)
                next_output = last_output + dialog_title
                return True
            else:
                return False
        output_changed(webdriver)
        yield next_output
        last_output = next_output
        while not Colab.IS_RUN_COMPLETE(webdriver, shadow, cell_element):
            WebDriverWait(webdriver, 60*60).until(output_changed)
            commonprefix = os.path.commonprefix((next_output, last_output))
            yield next_output[len(commonprefix):]
            last_output = next_output

    def SET_CELL_TEXT(webdriver, cell_element, text):
        editor = cell_element.find_element_by_class_name('monaco-editor')
        editor.click()
        lines = cell_element.find_element_by_tag_name('textarea')
        # erase existing content
        ActionChains(webdriver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        lines.send_keys(Keys.DELETE)
        editor.click()
        # type new content.  character by character to handle indentation adjustment.
        sent = ''
        for char in text:
            _nextchar = False
            while True:
                state = Colab.GET_CELL_TEXT(cell_element)
                #print('state=', state, 'sent=', sent)
                if state == sent:
                    break
                commonprefix = os.path.commonprefix((state, text))
                if len(commonprefix) > len(sent):
                    sent += commonprefix[len(sent)]
                    _nextchar = True
                    break
                else:
                    lines.send_keys(Keys.END, Keys.BACKSPACE)
                    continue
            if _nextchar:
                continue
            #print('sending', char)
            lines.send_keys(char)
            sent += char
        return sent

    def GET_FIELD_NAME(field_element):
        name = field_element.find_element_by_class_name('formview-namelabel').text
        if name[-1] == ':':
            name = name[:-1]
        return name

    def GET_FIELD_TYPE(elem):
        if elem.tag_name == 'colab-form-input':
            if elem.find_elements_by_tag_name('paper-input'):
                return "INPUT"
            inputs =  elem.find_elements_by_tag_name('input')
            if inputs and inputs[0].get_attribute('type') == 'checkbox':
                return "CHECKBOX"
        elif elem.tag_name == 'colab-form-dropdown':
            if elem.find_elements_by_tag_name('select'):
                return "SELECT"
            elif elem.find_elements_by_tag_name('paper-input'):
                return "DROPDOWN"
        raise Exception('unrecognised field ' + elem.tag_name)

    def GET_FIELD_INPUT_VALUE(shadow, field_element):
        return shadow.find_element(field_element, 'input').get_attribute('value')

    def SET_FIELD_INPUT_VALUE(shadow, field_element, text):
        elem = shadow.find_element(field_element, 'input')
        elem.clear()
        elem.send_keys(text)

    def GET_FIELD_SELECT_OPTIONS(field_element):
        elems = field_element.find_element_by_tag_name('select').find_elements_by_tag_name('option')
        return [elem.text for elem in elems]

    def GET_FIELD_SELECT_VALUE(field_element):
        return field_element.find_element_by_tag_name('select').get_attribute('value')

    def SET_FIELD_SELECT_VALUE(field_element, text):
        elems = field_element.find_element_by_tag_name('select').find_elements_by_tag_name('option')
        for elem in elems:
            if str(elem.text) == str(text):
                elem.click()
                return
        raise Exception('not an option: ' + str(text))

    def GET_FIELD_DROPDOWN_OPTIONS(webdriver, shadow, field_element):
        elems = shadow.find_elements(field_element, 'paper-item')
        return [elem.get_attribute('value') for elem in elems]

    def GET_FIELD_DROPDOWN_VALUE(webdriver, shadow, field_element):
        return shadow.find_element(field_element, 'input').get_attribute('value')

    def SET_FIELD_DROPDOWN_VALUE(webdriver, shadow, field_element, text):
        button = shadow.find_element(field_element, 'paper-icon-button')
        button.click()
        elems = shadow.find_elements(field_element, 'paper-item')
        for elem in elems:
            if str(elem.get_attribute('value')) == str(text):
                WebDriverWait(webdriver, 10).until(lambda webdriver: elem.get_attribute('aria-disabled') != 'true')
                shadow.find_element(field_element, 'input').clear()
                shadow.find_element(field_element, 'input').send_keys(str(text))
                #elem.click()
                return
        raise Exception('not an option: ' + str(text))

    def GET_FIELD_CHECKBOX_VALUE(field_element):
        return field_element.find_element_by_tag_name('input').get_property('checked')

    def SET_FIELD_CHECKBOX_VALUE(field_element, state : bool):
        if bool(state) != Colab.GET_FIELD_CHECKBOX_VALUE(field_element):
            field_element.find_element_by_tag_name('input').click()

    def RESTART_RUNTIME(webdriver, shadow):
        webdriver.find_element_by_id('runtime-menu-button').click()
        webdriver.find_element_by_id('runtime-menu').find_element_by_xpath('//div[@command="restart"]').click()
        if Colab.DIALOG_MESSAGE(webdriver, shadow):
            Colab.CLOSE_DIALOG(webdriver, shadow)
        
    def OPEN_DIALOG(webdriver):
        webdriver.find_element_by_id('file-menu-button').click()
        webdriver.find_element_by_id('file-menu').find_element_by_xpath('//div[@command="open"]').click()
    def OPEN_DISMISS(webdriver):
        webdriver.find_element_by_class_name('dismiss').click()

    def DIALOG_MESSAGE(webdriver, shadow):
        try:
            dialog = webdriver.find_element_by_tag_name('paper-dialog')
            return shadow.find_element(dialog, 'div').text
        except:
            return None

    def CLOSE_DIALOG(webdriver, shadow):
        # first wait for buttons to be enabled

        # the aria-disabled attribute of the paper-button elements is 'false' when can be clicked, 'true' when unclickable
        dialog = webdriver.find_element_by_tag_name('paper-dialog')
        WebDriverWait(webdriver, 10).until(lambda webdriver: shadow.find_element(dialog, 'paper-button').get_attribute('aria-disabled') != 'true')

        # click button
        try:
            shadow.find_element(dialog, '#ok').click()
        except:
            shadow.find_element(dialog, '.dismiss').click()

        # wait for dialog to go away
        WebDriverWait(webdriver, 10).until(lambda webdriver: not Colab.DIALOG_MESSAGE(webdriver, shadow))
            
    def __init__(self, url = None, googledriver = None):
        if googledriver is None:
            import random
            engines = ['chrome', 'firefox']
            random.shuffle(engines)
            exception = None
            for engine in engines:
                try:
                    googledriver = GoogleDriver(engine)
                    break
                except Exception as exception:
                    continue
            if exception is not None:
                raise exception
        elif type(googledriver) is str:
            googledriver = GoogleDriver(googledriver)
        if url is None:
            url = Colab.BASEURL()
        self.googledriver = googledriver
        self.webdriver = googledriver.webdriver
        self.shadow = Shadow(self.webdriver)
        self.open(url)
    def reconnect(self):
        self.googledriver.create()
        self.webdriver = self.googledriver.webdriver
        self.open(self.url)
    def open(self, url):
        self.url = url
        self.webdriver.get(url)
        self._wait_for_loaded()
    def new(self):
        Colab.NEW_NOTEBOOK(self.webdriver)
        self._wait_for_loaded()
        return self.name
    def restart(self):
        Colab.RESTART_RUNTIME(self.webdriver, self.shadow)
    def insert_cell_below(self):
        Colab.INSERT_CELL_BELOW_CURRENT(self.webdriver)
    @property
    def cells(self):
        return [
            Colab.Cell(self, cell)
            for cell in Colab.CELL_ELEMENTS(self.webdriver)
        ]
    @property
    def name(self):
        return Colab.GET_NOTEBOOK_NAME(self.webdriver)
    @name.setter
    def doc_name(self, name):
        Colab.SET_NOTEBOOK_NAME(self.webdriver, name)
    def _wait_for_loaded(self):
        WebDriverWait(self.webdriver, 10).until(Colab.CONDITIONS_NOTEBOOK_LOADED())

    class Cell:
        def __init__(self, colab, element):
            self.colab = colab
            self.element = element
        def run(self):
            Colab.RUN_CELL(self.colab.webdriver, self.colab.shadow, self.element)
            if Colab.DIALOG_MESSAGE(self.colab.webdriver, self.colab.shadow):
                Colab.CLOSE_DIALOG(self.colab.webdriver, self.colab.shadow)
            return self.stream
        @property
        def text(self):
            return Colab.GET_CELL_TEXT(self.element)
        @property
        def fields(self):
            return [
                getattr(Colab.Cell, Colab.GET_FIELD_TYPE(element).title() + 'Field')(self, element)
                for element in Colab.FIELD_ELEMENTS(self.element)
            ]
        @text.setter
        def text(self, text):
            return Colab.SET_CELL_TEXT(self.colab.webdriver, self.element, text)
        @property
        def output(self):
            return Colab.GET_CELL_OUTPUT(self.colab.webdriver, self.element)
        @property
        def imgs(self):
            return Colab.GET_CELL_IMGS(self.colab.webdriver, self.element)
        @property
        def stream(self):
            return Colab.GENERATE_CELL_OUTPUT(self.colab.webdriver, self.colab.shadow, self.element)

        @property
        def is_run_complete(self):
            return Colab.IS_RUN_COMPLETE(self.colab.webdriver, self.colab.shadow, self.element)

        def __str__(self):
            try:
                return self.text + '\n' + self.output
            except:
                return self.text

        def __repr__(self):
            return str(self)

        class Field:
            def __init__(self, cell, element):
                self.cell = cell
                self.element = element
            @property
            def name(self):
                return Colab.GET_FIELD_NAME(self.element)
            def __str__(self):
                return self.name + ': ' + str(self.value)
            def __repr__(self):
                return str(self)

        class InputField(Field):
            @property
            def value(self):
                return Colab.GET_FIELD_INPUT_VALUE(self.cell.colab.shadow, self.element)
            @value.setter
            def value(self, text):
                return Colab.SET_FIELD_INPUT_VALUE(self.cell.colab.shadow, self.element, text)

        class SelectField(Field):
            @property
            def options(self):
                return Colab.GET_FIELD_SELECT_OPTIONS(self.element)
            @property
            def value(self):
                return Colab.GET_FIELD_SELECT_VALUE(self.element)
            @value.setter
            def value(self, text):
                return Colab.SET_FIELD_SELECT_VALUE(self.element, text)

        class DropdownField(Field):
            @property
            def options(self):
                return Colab.GET_FIELD_DROPDOWN_OPTIONS(self.cell.colab.webdriver, self.cell.colab.shadow, self.element)
            @property
            def value(self):
                return Colab.GET_FIELD_DROPDOWN_VALUE(self.cell.colab.webdriver, self.cell.colab.shadow, self.element)
            @value.setter
            def value(self, text):
                return Colab.SET_FIELD_DROPDOWN_VALUE(self.cell.colab.webdriver, self.cell.colab.shadow, self.element, text)

        class CheckboxField(Field):
            @property
            def value(self):
                return Colab.GET_FIELD_CHECKBOX_VALUE(self.element)
            @value.setter
            def value(self, state : bool):
                Colab.SET_FIELD_CHECKBOX_VALUE(self.element, state)
