import ast
import json
import time
import unicodedata
from multiprocessing import Process
import os
import shutil
import pandas as pd
import streamlit.components.v1 as component


class StreamlitUtils:
    def __init__(self, st_session):
        self.__st = st_session

    def __get_user_tab_selection(self, tabs, set_tab):
        if set_tab is None:
            query_params = self.__st.experimental_get_query_params()
            if "tab" in query_params:
                active_tab = query_params["tab"][0]
                return active_tab
            else:
                active_tab = tabs[0]
            if active_tab in tabs:
                self.__st.experimental_set_query_params(tab=tabs[0])
                active_tab = tabs[0]
                return active_tab
        else:
            return set_tab

    def build_tabs_html(self, tabs, set_tab=None):
        current_tab = self.__get_user_tab_selection(tabs, set_tab)
        self.__st.markdown(
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" '
            'integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" '
            'crossorigin="anonymous">',
            unsafe_allow_html=True,
        )
        li_items = "".join(
            f"""
                <li class="nav-item">
                    <a class="nav-link{' active' if t == current_tab else ''}" href="/?tab={t}">{t}</a>
                </li>
                """
            for t in tabs
        )
        tabs_html = f"""
                <ul class="nav nav-tabs">
                {li_items}
                </ul>
            """
        self.__st.markdown(tabs_html, unsafe_allow_html=True)
        return current_tab

    def set_component(self, obj, css, js_component: bool = False, height: int = 100, width: int = 1000,
                      scrolling: bool = True):
        if not js_component:
            self.__st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
            self.__st.markdown(obj, unsafe_allow_html=True)
        else:
            component.html(obj, height=height, width=width, scrolling=scrolling)

    def __generate_columns(self, columns_count: int, column_width: int):
        if columns_count > 1:
            index = 0
            columns = []
            while index < columns_count:
                columns.append(column_width)
                index += 1
        else:
            columns = [columns_count, column_width]
        return self.__st.columns(columns)

    def create_columns_data(self, data, column_width: int = 6):
        temp_list = []
        columns_count = len(data)
        for d, col in zip(data, self.__generate_columns(columns_count, column_width)):
            temp_list.append({f'{d[0]}': col.radio(label=d[0], options=d[1])})
        return temp_list

    def initial_session_state(self, items: list):
        for item in items:
            self.__st.session_state.setdefault(item[0], item[1])
        return self.__st.session_state


class PyPIArtifact:
    def __init__(self, main_path, user=None, password=None):
        self.__dist_dir = f"{main_path}/dist"
        if user is not None:
            self.__user = user
            self.__password = password
        else:
            self.__user = os.environ.get('pypi-user')
            self.__password = os.environ.get('pypi-password')
        self.__build_commands = self.__build_terminal_commands

    @property
    def __build_terminal_commands(self):
        return ["python setup.py develop", "python -m pip install --upgrade pip",
                "python -m pip install --upgrade build", "python -m build", "python setup.py sdist bdist_wheel"]

    @property
    def __upload_terminal_command(self):
        return f"twine upload -u {self.__user} -p {self.__password}" \
               f" --repository-url https://upload.pypi.org/legacy/ dist/*"

    def __delete_dist_dir(self):
        if os.path.exists(self.__dist_dir) and os.path.isdir(self.__dist_dir):
            shutil.rmtree(self.__dist_dir)
        else:
            print("The dist directory does not exist")

    def __build(self):
        for command in self.__build_commands:
            os.system(command)

    def __upload(self):
        os.system(self.__upload_terminal_command)

    def run(self):
        self.__delete_dist_dir()
        self.__build()
        self.__upload()


class RunningFramework:
    def __init__(self, app_session: Process, before: dict = None, join_session: bool = False):
        self.__before_session = before
        self.__app_session = app_session
        self.__join_session = join_session
        self.__tasks = self.__session_tasks()

    @property
    def get_session_tasks(self):
        return self.__tasks

    @property
    def is_alive(self):
        return self.__app_session.is_alive()

    def kill(self):
        return self.__after()

    def run_session(self):
        next(self.__tasks)  # before all
        next(self.__tasks)  # running session
        next(self.__tasks)  # after all

    def __session_tasks(self):
        self.__before()
        yield
        self.__running()
        yield
        self.__after()
        yield

    def __before(self):
        print('Start App Session')
        session = []
        if self.__before_session is not None:
            for before in self.__before_session.items():
                before[1].start()
                session.append(before[1])
            self.__before_session = session

    def __running(self):
        print(f'{self.__app_session.name} is running..')
        self.__app_session.start()
        if self.__join_session:
            self.__app_session.join()
            self.__after()

    def __after(self):
        for process in self.__before_session:
            if type(process) is Process:
                if process.is_alive():
                    process.kill()
                print(f"{process.name} closed successfully")
            if self.__app_session.is_alive():
                self.__app_session.kill()
            print(f"{self.__app_session.name} closed successfully")
        print('End App Session')


class RunParallel:
    @staticmethod
    def run_multi_process(function_target, count_of_process: int = 1, args: list = None):
        start = time.perf_counter()
        process_index = 0
        process_list = []
        while process_index < count_of_process:
            if args is not None:
                process_list.append(Process(target=function_target, args=args[process_index]))
            else:
                process_list.append(Process(target=function_target))
            process_index += 1

        for process in process_list:
            process.start()

        for process in process_list:
            process.join()

        finish = time.perf_counter()
        print(f'Finished in {round(finish - start, 2)} second(s)')


def rmdiacritics(char):
    '''
    Return the base character of char, by "removing" any
    diacritics like accents or curls and strokes and the like.
    '''
    if char == 'æ':
        char = 'e'
        return char
    if char == 'ß':
        char = 's'
        return char
    desc = unicodedata.name(char)
    cutoff = desc.find(' WITH ')
    if cutoff != -1:
        desc = desc[:cutoff]
        try:
            char = unicodedata.lookup(desc)
        except KeyError:
            pass  # removing "WITH ..." produced an invalid name
    return char


def strip_accents(text):
    """ Function to format special characters to english"""
    string_format = ""
    if "Ã¡" in text:
        text = text.replace("Ã¡", "a")
    if "Ã­" in text:
        text = text.replace("Ã­", "i")
    if "Ãª" in text:
        text = text.replace("Ãª", "e")
    if "Ã©" in text:
        text = text.replace("Ã©", "e")
    if "Ãº" in text:
        text = text.replace("Ãº", "u")
    if "Ã¼" in text:
        text = text.replace("Ã¼", "u")
    if "Ã¼" in text:
        text = text.replace("Ã¼", "u")
    if 'u00f' in text and "\\u00f" not in text:
        text = text.replace('u00f', "\\u00f").encode().decode('unicode_escape')
    for char in text:
        new_char = rmdiacritics(char)
        string_format += new_char
    string_format = unicodedata.normalize('NFD', string_format) \
        .encode('ascii', 'ignore').decode("utf-8")
    return str(string_format)


# ---------------------------- files actions ------------------------------------#
def dict_to_json(string_content):
    try:
        return json.dumps(str_to_dict(string_content))
    except Exception as e:
        print(e)


def str_to_dict(string_content):
    try:
        return ast.literal_eval(str(string_content))
    except Exception as e:
        print(e)
        return load_json(string_content)


def load_json(string_content):
    try:
        return json.loads(string_content)
    except Exception as e:
        print(e)


def read_json(path):
    with open(path, 'r') as file:
        json_object = json.load(file)
    return json_object


def read_table_from_html(save_path, browser_session, url=None):
    if '.html' not in save_path:
        save_path = f"{save_path}.html"
    if browser_session is not None:
        if url is not None:
            browser_session.get_url(url)
        with open(save_path, 'w') as file:
            html_data = browser_session.actions.get_page_source()
            file.write(html_data)
    df = pd.read_html(save_path)
    return df
