import os
import json
import base64

from ..common.constants import TIYARO_INTERNAL_DIR, TIYARO_INTERNAL_TEST_STATE_FILE, C_TEST_INPUT, C_TEST_OUTPUT, C_TEST_USER_CONFIRMED


def save_input(test_input):
    state = get_test_state()
    if isinstance(test_input, (bytearray, bytes)):
        test_input = base64.b64encode(test_input).decode('utf-8')
    state[C_TEST_INPUT] = test_input
    _write_state(state)
    pass


def save_output(test_output):
    state = get_test_state()
    state[C_TEST_OUTPUT] = test_output
    _write_state(state)
    pass


def save_user_confirmed(is_user_confirmed):
    state = get_test_state()
    state[C_TEST_USER_CONFIRMED] = is_user_confirmed
    _write_state(state)
    pass

def is_test_attempted():
    state = get_test_state()
    test_input = state.get(C_TEST_INPUT, None)
    return True if test_input else False

def get_test_state():
    if (not os.path.exists(TIYARO_INTERNAL_TEST_STATE_FILE)):
        existing_state = {}
    else:
       with open(TIYARO_INTERNAL_TEST_STATE_FILE, "r") as f:
           existing_state = json.load(f)
    return existing_state


def _write_state(state):
    if not os.path.isdir(TIYARO_INTERNAL_DIR):
        os.makedirs(TIYARO_INTERNAL_DIR)
    with open(TIYARO_INTERNAL_TEST_STATE_FILE, 'w+', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=4)
