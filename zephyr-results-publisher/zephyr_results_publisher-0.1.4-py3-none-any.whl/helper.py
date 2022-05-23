import logging


def check_response_status(response, expected_code):
    logging.info(f"Response code: {response.status_code}")
    if response.status_code != expected_code:
        logging.info(f"Error appears: {response.text}")
        logging.info("Note: response code 400 doesn't mean the results were not published. Please check Zephyr Scale "
                     "Tests and Cycles.")
        raise Exception(response.text)


def find_folder_id_by_name(name, response):
    for value in response['values']:
        if value['name'] == name:
            logging.info(f"Folder id {value['id']} is found for folder name: {name}")
            return value['id']
