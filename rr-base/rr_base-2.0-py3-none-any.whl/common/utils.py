import time
from multiprocessing import Process
import os
import shutil


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


def terminal(c):
    os.system(command=c)


def run_command_line_process(command: str):
    p = Process(target=terminal, args=(command,))
    p.start()


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
