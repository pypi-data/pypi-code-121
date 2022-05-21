"""Command line interface for ta-tooling."""
import json
import os
import getpass
from pathlib import Path
import shutil
from time import sleep
from uuid import uuid4

import click
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.remote.command import Command
from dotenv import load_dotenv

import ta_tooling
from bbutils import BbAPI, create_app


@click.group()
def main():
    pass


@click.command(help="Group files from the same student together in a folder")
@click.argument(
    "source",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, writable=True
    ),
    required=True,
)
@click.argument(
    "destination",
    type=click.Path(
        exists=False, file_okay=False, dir_okay=True, readable=True, writable=True
    ),
    required=True,
)
def categorize(source, destination):
    click.echo("Categorizing files ...")
    ta_tooling.categorize(source, destination)


@click.command(help="Start the server for injection script to call back to")
def serve_inject():
    app = create_app()
    # TODO open a browser window pointing to the web server URL.
    app.run()


@click.command(help="Download the file using the link file")
@click.argument(
    "user_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    required=True,
)
@click.argument(
    "link_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    required=True,
)
def download_links(user_file, link_file):
    load_dotenv(".env")
    course_id = os.getenv("COURSE_ID", None)
    username = os.getenv("BB_USERNAME", None)
    password = os.getenv("BB_PASSWORD", None)

    if course_id is None:
        text = input("Course ID: ")
        if text.startswith("http"):
            course_id = BbAPI.parse_url_for_course_id(text)
        else:
            course_id = text
    if username is None:
        username = input("Username: ")
    if password is None:
        password = getpass.getpass("Password: ")

    temp_working_dir = str(uuid4())
    temp_download_dir = Path(temp_working_dir) / "download"
    os.mkdir(temp_working_dir)
    os.mkdir(temp_download_dir)

    options = Options()
    options.page_load_strategy = "none"

    profile = BbAPI.get_firefox_profile(temp_download_dir)
    driver = webdriver.Firefox(firefox_profile=profile, options=options)
    driver.command_executor.set_timeout(20)
    driver.implicitly_wait(5)
    driver.set_page_load_timeout(5)
    driver.set_script_timeout(5)
    api = BbAPI(course_id, driver)

    api.login(username, password)

    df = pd.read_csv(user_file)
    df["full_name"] = df["firstName"] + " " + df["lastName"]

    with open(link_file, "r") as f:
        entries = json.load(f)

        for entry in entries:
            email_handle = df[df["full_name"] == entry["name"]]["emailHandle"].values[0]
            print("Processing", entry["name"], email_handle)

            entry_dir = Path(os.path.join(temp_working_dir, email_handle))

            if not entry_dir.is_dir():
                os.mkdir(entry_dir)

            if len(entry["url"]) == 0:
                continue

            api.get_file(entry["url"])

            print("Moving files")
            files = list(temp_download_dir.glob("*"))
            if len(files) >= 1:
                for f in files:
                    shutil.move(f, entry_dir)

            sleep(1.3)

    print(f"Working directory was {temp_working_dir}")


@click.command(help="Download the student list")
def get_student_list():
    load_dotenv(".env")
    course_id = os.getenv("COURSE_ID", None)
    username = os.getenv("BB_USERNAME", None)
    password = os.getenv("BB_PASSWORD", None)

    # TODO Search and use available browser.
    driver = webdriver.Firefox()

    if course_id is None:
        text = input("Course ID: ")
        if text.startswith("http"):
            course_id = BbAPI.parse_url_for_course_id(text)
        else:
            course_id = text
    if username is None:
        username = input("Username: ")
    if password is None:
        password = getpass.getpass("Password: ")

    api = BbAPI(course_id, driver)
    api.login(username, password)

    student_list = api.students()

    with open(f"users{course_id}.csv", "w") as f:
        f.write("emailHandle,firstName,lastName,userId,courseMembershipId\n")
        for entry in student_list:
            f.write(
                "{},{},{},{},{}\n".format(
                    entry["user"]["userName"],
                    entry["user"]["name"]["given"],
                    entry["user"]["name"]["family"],
                    entry["userId"],  # or user['user']['id']
                    entry["id"],
                )
            )

    driver.quit()


main.add_command(categorize)
main.add_command(serve_inject)
main.add_command(download_links)
main.add_command(get_student_list)

if __name__ == "__main__":
    main()
