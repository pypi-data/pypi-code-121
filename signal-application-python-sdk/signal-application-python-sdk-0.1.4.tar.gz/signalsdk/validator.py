import logging


def throw_if_parameter_not_found_in(value, param, location):
    """validate parameter existence in location
    """
    if not value:
        error_message = f"signalsdk::Application SDK can not start " \
                        f"because {param} is not found in {location}"
        logging.info(error_message)
        raise Exception(error_message)
