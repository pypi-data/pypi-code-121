from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from requests import Session
from typing import Dict


def get_all_forms(url: str, session: Session) -> ResultSet:
    """Returns all form tags found on a web page's `url`"""
    # GET request
    res = session.get(url)
    # for javascript driven website
    # res.html.render()
    soup = BeautifulSoup(res.content, "html.parser")
    return soup.find_all("form")


def get_form_details(form: Tag) -> Dict[str, str]:
    """Returns the HTML details of a form,
    including action, method and list of form controls (inputs, etc)"""
    details = {}
    # get the form action (requested URL)
    action = form.attrs.get("action", "")
    # get the form method (POST, GET, DELETE, etc)
    # if not specified, GET is the default in HTML
    method = form.attrs.get("method", "get").lower()
    # get all form inputs
    inputs = []
    for input_tag in form.find_all("input"):
        # get type of input form control
        input_type = input_tag.attrs.get("type", "text")
        # get name attribute
        input_name = input_tag.attrs.get("name")
        # get the default value of that input tag
        input_value = input_tag.attrs.get("value", "")
        checked = None
        if input_type == "checkbox":
            checked_state = input_tag.attrs.get("checked", "false")
            checked = False if checked_state == "false" else True
        # add everything to that list
        inputs.append(
            {
                "type": input_type,
                "name": input_name,
                "value": input_value,
                "checked": checked,
            }
        )
    # put everything to the resulting dictionary
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details
