"""Module with various tools."""
import os
import json
from typing import Any, List, Dict, Literal, Callable, Union, Tuple, Type, Sequence, TypeVar

from werkzeug.wrappers.response import Response
from flask import make_response, redirect, flash, render_template
from warepy import log, join_paths, format_message, load_yaml


@log.catch
def generate_redirect_response(url: Any, status_code: int = 302) -> Response:
    """Generate redirect response with given url and return this response."""
    response = redirect(url, code=status_code)
    return response


@log.catch
def generate_success_response(data: Any, is_json_enabled: bool, ok_status_code: int = 200, no_content_status_code: int = 204) -> Response:
    """Generate success response with given data and return this response.
    
    If `is_json_enabled` == True, dump data to json."""
    # Check if data should be dumped to json.
    if is_json_enabled:
        content = json.dumps(data)
    else:
        content = data

    response = make_response(content)

    # Set special status code if there is no content and OK otherwise.
    if content:
        response.status_code = ok_status_code
    else:
        response.status_code = no_content_status_code

    return response


@log.catch
def generate_error_response(error: Exception, status_code: int = 400) -> Response:
    """Generate error response with given error and return this response."""
    data = {"error": repr(error)}
    json_data = json.dumps(data)
    response = make_response(json_data)
    response.status_code = status_code
    return response


@log.catch
def make_fail_response(
    template_path: str, template_ctx: dict = {}, flash_message: str = "Error", flash_category: Literal["message", "error", "info", "warning"] = "error"
) -> Response:
    """Generate fail response with rendered template by given path with status code 422 compatible with turbo.js.
    
    Also able to flash message to template context.
    
    Args:
        template_path: Path to template to render.
        template_ctx (optional): Context to push to template. Defaults to empty dict.
        flash_message (optional): Message to flash to template context. Defaults to "Error".
        flash_category (optional): Category for flash message according to Flask's `flash` categories. Defaults to "error".
    """
    # Login errors should be flashed to user.
    flash(flash_message, category=flash_category)
    response = make_response(render_template(template_path, **template_ctx))
    # Always set status code of failed to form posts responses to 422 or turbo.js will raise an error.
    # Ref: https://github.com/miguelgrinberg/turbo-flask/issues/11#issuecomment-883248949
    response.status_code = 422
    return response


@log.catch
def do_or_flash(func: Callable, message: str | None = None, *args, **kwargs) -> Any:
    """Call given function with given args and kwargs and flask.flash message if the function raised an error. Return function output if there was no exception.
    
    Args:
        func: Function to execute and grab output.  
        message: Message to flash by Flask engine. Defaults to None, which means;
        - If `PUFT_MODE` is `dev`, `test`: flash error text.    
        - If `PUFT_MODE` is `prod`: flash text: "Something bad happened."  
    """
    puft_mode = os.environ["PUFT_MODE"]

    try:
        output = func(*args, **kwargs)
    except Exception as error:
        if puft_mode in ["dev", "test"] and message:
            flash(message)
        elif puft_mode in ["prod"]:
            flash("Something bad happened.")
    else:
        return output
