import n_utils
from conversions import convert_number


def dip_this_func(number: str, new_base: int, current_base: int):
    """Now the real work begins (read in Ultron's voice)"""
    current_base_name = n_utils.base_find(current_base)
    new_base_name = n_utils.base_find(new_base)

    # ensure the bases to switch between are standard
    if n_utils.ensure_base_is_standard(new_base) and n_utils.ensure_base_is_standard(current_base):

        # Ensure a number is representable within it's base and overall
        if not n_utils.base_limits(number, current_base):
            print(f"'{number}' is not a {current_base_name}")
            return

        result = convert_number(number, current_base, new_base)
        q_string = f"'{number}' in {current_base_name} (base {current_base}) to {new_base_name} (base {new_base}) = "
        print(f"{q_string}'{result}'")

    else:
        non_standard = [
            str(base_) for base_ in [new_base, current_base] if not n_utils.ensure_base_is_standard(base_)
        ]
        print(f"The bases provided are not standard: {', '.join(non_standard)}")
