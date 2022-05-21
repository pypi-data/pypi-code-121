import json
from pathlib import Path
from time import sleep
from urllib.parse import urlparse
from typing import Optional

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions


class BbAPI:
    """
    Blackboard API.

    Since the chance of legitamately build application for Blackboard
    and have it approved by OIT to be added to the deployed Blackboard
    at Ohio University is slim, this API client use selenium web testing
    framework to imitate user and sending request to the API endpoints
    using logged in user session.
    """

    API_SERVER_URL = "https://blackboard.ohio.edu"
    RESOURCES = {
        "columns": "/learn/api/public/v1/courses/{course_id}/gradebook/columns",
        "memberships": "/learn/api/public/v1/courses/{course_id}/users?fields=id,userId,user,courseRoleId",
        "attempts": "/learn/api/public/v1/courses/{course_id}/gradebook/columns/{column_id}/attempts",
        "attempt_files": "/learn/api/public/v1/courses/{course_id}/gradebook/attempts/{attempt_id}/files",
        "download_file": "/learn/api/public/v1/courses/{course_id}/gradebook/attempts/{attempt_id}/files/{attempt_file_id}/download",
        "questions": "/webapps/assessment/do/grade/viewQuestions?outcome_definition_id={outcome_definition_id}&course_id={course_id}",
        "grade_questions": "/webapps/assessment/do/gradeQuestions?questionId={question_id}&course_id={course_id}&filter=ALL&outcomeDefinitionId={outcome_definition_id}&anonymousMode=false",
    }

    HELPER_SCRIPT = """
window.get_url = function(url) {
    fetch(url).then(response => {
        window.helper_result = response.url;
    });
}
    """

    LOGIN_SLEEP_TIME = 5

    def __init__(self, course_id, driver):
        self.driver = driver
        if course_id.startswith("http"):
            self.course_id = BbAPI.parse_url_for_course_id(course_id)
        else:
            self.course_id = course_id

        self.is_firefox = False
        if driver.capabilities["browserName"] == "firefox":
            self.is_firefox = True

        self._students_cache = []

    @classmethod
    def parse_url_for_course_id(cls, url: str) -> Optional[str]:
        tokens = url.split("/")

        try:
            course_kw_pos = tokens.index("courses")
            if len(tokens) < course_kw_pos + 1:
                return None
            return tokens[course_kw_pos + 1]
        except ValueError:
            return None

    @classmethod
    def get_firefox_profile(cls, temp_download_dir):
        """
        Return a special Firefox profile.

        The profile is used to skip download confirm dialog for most file types
        in homework submission. The profile also relocate the download
        directory to the temporary location.

        To prevent PDF viewer to show the PDF file instead of downloading it,
        the profile also disable the pdfjs.
        """
        profile = FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference(
            "browser.download.dir", str(temp_download_dir.absolute())
        )
        profile.set_preference("browser.download.useDownloadDir", True)
        profile.set_preference("browser.download.viewableInternally.enabledTypes", "")
        profile.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/pdf;text/plain;application/text;text/xml;application/xml;"
            + "application/vnd.openxmlformats-officedocument.wordprocessingml.document;"
            + "application/rtf;application/vnd.rar;text/plain;image/webp;image/bmp;"
            + "image/jpeg;application/x-7z-compressed;application/zip;application/x-tar;"
            + "application/gzip;application/vnd.openxmlformats-officedocument.presentationml.presentation;"
            + "application/octet-stream;application/x-rar-compressed;application/x-zip-compressed;"
            + "multipart/x-zip;application/vnd.oasis.opendocument.presentation;"
            + "application/vnd.oasis.opendocument.spreadsheet;application/vnd.oasis.opendocument.text"
            + "application/tar;application/tar+gzip",
        )
        profile.set_preference("pdfjs.disabled", True)
        profile.update_preferences()
        return profile

    def login(self, username, password):
        """
        Login to Blackboard.

        Raise the ValueError when the sign-in fail.
        """
        self.driver.get(self.API_SERVER_URL)
        # input#i0116 for username.  //*[@id="i0116"]
        # input#idSIButton9 for Next button.  //*[@id="idSIButton9"]
        # input#i0118 for password.  //*[@id="i0118"]
        sleep(self.LOGIN_SLEEP_TIME)
        username_txt = self.driver.find_element_by_xpath('//*[@id="i0116"]')
        username_txt.send_keys(username)
        next_btn = self.driver.find_element_by_xpath('//*[@id="idSIButton9"]')
        next_btn.click()
        sleep(self.LOGIN_SLEEP_TIME)
        password_txt = self.driver.find_element_by_xpath('//*[@id="i0118"]')
        password_txt.send_keys(password)
        sleep(self.LOGIN_SLEEP_TIME)
        sign_in_btn = self.driver.find_element_by_xpath('//*[@id="idSIButton9"]')
        sign_in_btn.click()

        try:
            # User may have to approve MFA.
            WebDriverWait(self.driver, 60).until(EC.url_contains("blackboard"))
        except exceptions.TimeoutException as e:
            # Username or password is incorrect.
            raise ValueError(
                "Username or password is incorrect. Still stuck at login page."
            )

    def get_json(self, url):
        """
        Return JSON.

        Handle the different between Firefox and Chrome.
        """
        if self.is_firefox:
            url = "view-source:" + url

        self.driver.get(url)
        pre = self.driver.find_element_by_tag_name("pre").text
        data = json.loads(pre)
        return data

    def columns(self):
        """
        Return the columns in grade center.

        The ID in this is used to retrive questions
        """
        target_url = self.API_SERVER_URL + self.RESOURCES["columns"].format(
            course_id=self.course_id
        )
        data = self.get_json(target_url)
        return data["results"]

    def attempts(self, column_id):
        """
        Return attempts in the column.
        """
        target_url = self.API_SERVER_URL + self.RESOURCES["attempts"].format(
            course_id=self.course_id, column_id=column_id
        )
        data = self.get_json(target_url)
        return data["results"]

    def students(self):
        """
        Return list of students.
        """
        target_url = self.API_SERVER_URL + self.RESOURCES["memberships"].format(
            course_id=self.course_id
        )
        data = self.get_json(target_url)
        student_objects = [
            obj for obj in data["results"] if obj["courseRoleId"] == "Student"
        ]

        self._students_cache = student_objects
        return self._students_cache

    def get_file(self, url):
        """
        Download file at the URL.

        Navigate to URL and download file to the temporary area. Return path to file.

        The Selenium driver for Firefox need the profile that skip the download dialog.

        TODO: This still needs to be supervised. It does sometimes miss the certain file type.
        """
        download_dir = Path(
            self.driver.profile.default_preferences["browser.download.dir"]
        )

        try:
            self.driver.get(url)

            filename = Path(urlparse(url).path).name
            if url.endswith(".txt"):
                text = self.driver.find_element_by_tag_name("pre").text

                with open(download_dir.joinpath(filename), "w") as f:
                    f.write(text)

            elif (
                url.lower().endswith(".jpg")
                or url.lower().endswith(".png")
                or url.lower().endswith(".jpeg")
            ):
                target_image_url = self.driver.current_url

                response = requests.get(target_image_url)

                with open(download_dir.joinpath(filename), "wb") as f:
                    f.write(response.content)

        except exceptions.TimeoutException:
            pass
        sleep(20)

    def questions(self, column_id):
        """
        Return questions in the column.

        Column is expected to be the exam.
        """
        target_url = self.API_SERVER_URL + self.RESOURCES["questions"].format(
            course_id=self.course_id, outcome_definition_id=column_id
        )
        self.driver.get(target_url)
        tbody = self.driver.find_element_by_id("listContainer_databody")
        rows = tbody.find_elements_by_xpath(".//tr")

        questions = []
        for row in rows:
            question_text = row.find_elements_by_xpath(".//th/p")[0].text
            href = row.find_elements_by_xpath(".//td[4]/span/a")[0].get_property("href")
            question_type = row.find_elements_by_xpath(".//td[2]/span")[0].text

            quote_index_start = href.index("'", 0)
            quote_index_end = href.index("'", quote_index_start + 1)

            questions.append(
                {
                    "id": href[quote_index_start + 1 : quote_index_end],
                    "text": question_text,
                    "href": href,
                    "type": question_type,
                }
            )

        return questions

    def submission_files(self, attempt_id):
        target_url = self.base_url + self.RESOURCES["attempt_files"].format(
            course_id=self.course_id, attempt_id=attempt_id
        )
        self.driver.get(target_url)
        pre = self.driver.find_element_by_tag_name("pre").text
        data = json.loads(pre)

        return data["results"]

    def download_file(self, attempt_id, attempt_file_id):
        """This does not work.

        1. The url from the API point to the internal file cannot be accessed.
        """
        self.driver.get(self.API_SERVER_URL)
        self.driver.execute_async_script(self.HELPER_SCRIPT)

        url = self.API_SERVER_URL + self.RESOURCES["download_file"].format(
            course_id=self.course_id,
            attempt_id=attempt_id,
            attempt_file_id=attempt_file_id,
        )
        print(url)
        self.driver.execute_async_script("window.get_url('" + url + "');")
        sleep(5)
        target_url = self.driver.execute_script("return window.helper_result;")
        print(target_url)

        self.driver.get(target_url)

    def download_attempt_files(self, attempt_id):
        for files in self.submission_files(self.course_id, attempt_id):
            self.download_file(self.course_id, attempt_id, files["id"])

    def download_all_files(self, column_id):
        for attempt in self.attempts(self.course_id, column_id):
            self.download_attempt_files(self.course_id, attempt["id"])


def create_app():
    """
    Injector and processing application.

    This server prompt user to inject script into the console and wait for the
    script to call back.
    """
    app = Flask(__name__)
    CORS(app)

    @app.route("/", methods=["GET", "POST"])
    def handle_list():
        if request.method == "GET":
            return render_template("index.html")
        elif request.method == "POST":
            data = request.get_json()
            submission_files = data["submission_files"]

            entries = []
            for entry in submission_files:
                name = entry["name"].strip().replace("\n", "").replace("\xa0", "")
                try:
                    lparen_idx = name.index("(")
                    name = name[:lparen_idx].strip()
                except ValueError:
                    pass

                entries.append({"name": name, "url": entry["url"]})

            with open("files.json", "w") as f:
                json.dump(entries, f, indent=2)

            return jsonify({"status": "success"})

    return app
