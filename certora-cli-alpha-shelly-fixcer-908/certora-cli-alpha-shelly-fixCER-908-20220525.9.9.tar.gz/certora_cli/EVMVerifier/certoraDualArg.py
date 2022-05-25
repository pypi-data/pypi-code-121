import argparse
import re
import logging

arg_logger = logging.getLogger("arguments")

"""
This file is here to handle dually-defined arguments: command line arguments that can also be passed as a setting.
For example, we can use either '--rule law' or '--settings -rule=law'
Another example is: '--loop_iter 2' or '--settings -b=2'

The argparser does not handle the value of --settings at all. This is so the jar developers can add flags quickly
 without changing the scripts.
"""

# Note: we do not check if the argument is defined in the ArgumentParser.
val_arg_to_setting = {
    'loop_iter': 'b',
    "rule_sanity": "ruleSanityChecks",
    'max_graph_depth': 'graphDrawLimit',
    'method': 'method',
    'smt_timeout': 't',
    'bytecode_spec': 'spec'
}

val_arg_to_list_setting = {
    'bytecode_jsons': 'bytecode',
    'rule': 'rule'
}

setting_aliases = {
    'rule': 'rules',
    'rules': 'rules',
}

'''
The options below are boolean, and their default in the CVT is False. If in the future, the CVT default of an options
will change, we should remove that option from the dictionary.
'''
bool_arg_to_implicit_setting = {
    "optimistic_loop": "assumeUnwindCond",
    "multi_assert_check": "multiAssertCheck"
}

'''
The options below are boolean, their default in the CVT is False, and require to explicitly set their value to true.
If in the future, the CVT default of an options will change, we should remove that option from the dictionary.
'''
bool_arg_to_explicit_setting = {
    'short_output': 'ciMode'
}


def __check_single_arg_and_setting_consistency(args: argparse.Namespace, arg_name: str, setting_name: str,
                                               is_list_setting: bool) -> None:
    """
    We accept two syntaxes for settings: --rule or --settings -rule.
    This function checks that:
    1. The two syntaxes are consistent within the same command line (do not have contradicting values)
    2. The --settings syntax is consistent (gets a single setting -setting_name at most)
    3. If we use both the setting and the argument, warn of the redundancy

    After running this function, the value will be stored both in the settings and in the argument namespace.
    The arguments in settings may now be unsorted.

    @param args: a namespace containing command line arguments
    @param arg_name: name of the argument, for example: --rule or --loop_iterations
    @param setting_name: name of the setting, for example: -rule or -b
    @raises argparse.ArgumentTypeError if there is an inconsistent use of the argument.
    """
    setting_value = None
    all_settings_vals = set()
    setting_names = [setting_name]
    if setting_name in setting_aliases:
        setting_names.append(setting_aliases[setting_name])
    if args.settings is not None:
        for setting in args.settings:
            for sname in setting_names:
                setting_match = re.search(r'^-' + sname + r'(\S*)', setting)
                if setting_match is not None:
                    curr_val = setting_match[1]
                    if curr_val == "" or curr_val == "=":
                        raise argparse.ArgumentTypeError(f"No value was provided for setting {sname}")
                    if re.search(r"^=[^=\s]+", curr_val):
                        if curr_val in all_settings_vals:
                            arg_logger.warning(
                                f"Used --settings -{sname} more than once with the same value: {setting}"
                            )
                        all_settings_vals.add(curr_val[1:])  # remove the leading =
                    elif not re.search(r"^\w+(=[^=\s]+)?$", curr_val):
                        # there might a setting for which this setting is a substring, like -rule and -ruleSanityChecks
                        raise argparse.ArgumentTypeError(f"wrong syntax for --settings -{arg_name}: {setting}")
        if len(all_settings_vals) > 1:
            all_vals_str = ' '.join(sorted(list(all_settings_vals)))
            raise argparse.ArgumentTypeError(
                f"Multiples values were given to setting {setting_name}: {all_vals_str}")
        if len(all_settings_vals) > 0:
            setting_value = list(all_settings_vals)[0]

    arg_val = getattr(args, arg_name, None)
    if arg_val is not None:
        if is_list_setting:
            arg_val = ','.join(arg_val)
        else:
            arg_val = arg_val.replace(' ', '')
            # needed in case where we have --method foo(bool,address),
            # as we include an artificial space after the comma inside the parenthesis

    if arg_val is None and setting_value is None:
        return

    # given both as an argument and as a setting
    if arg_val is not None and setting_value is not None and arg_val != setting_value:
        raise argparse.ArgumentTypeError(
            f"There is a conflict between argument {arg_name} value of {arg_val} "
            f"and --settings -{setting_name} value of {setting_value}")

    if arg_val is None:  # backfill argument
        setattr(args, arg_name, setting_value)  # settings value is not None

    if setting_value is None:  # backfill settings
        settings_str = f'-{setting_name}={arg_val}'
        if args.settings is None:
            args.settings = list()
        args.settings.append(settings_str)  # it is now unsorted!


def __check_bool_arg_and_implicit_setting_consistency(args: argparse.Namespace, arg_name: str, setting_name: str) \
        -> None:
    """
    We accept two syntaxes for settings: --rule or --settings -rule.
    This function checks boolean settings, that can either appear, or not.
    This function reverts if a value is erroneously given to the boolean setting.

    If we use both the setting and the argument syntaxes, we warn of the redundancy. We also warn if the setting is
     given more than once.

    After running this function, the value will be stored both in the settings and in the argument namespace.
    The order of flags in settings may now no longer be sorted alphabetically.

    @param args: a namespace containing command line arguments
    @param arg_name: name of the argument, for example: --optimistic_loop or --rule_sanity
    @param setting_name: name of the setting, for example: -assumeUnwindCondition or -ruleSanityChecks
    @raises argparse.ArgumentTypeError if there is an inconsistent use of the argument.
    """
    setting_appeared = False
    all_warnings = set()

    if args.settings is not None:
        for setting in args.settings:
            setting_match = re.search(r'^-' + setting_name + r'(=[^=]+)?$', setting)
            if setting_match is not None:
                if '=' in setting_match[0]:
                    raise argparse.ArgumentTypeError(
                        f"Boolean setting {setting_name} cannot get a value, given {setting_match[1]}")
                if setting_appeared:
                    all_warnings.add(f"Setting {setting_name} appeared more than once, this is redundant")
                else:
                    setting_appeared = True

    arg_val = getattr(args, arg_name, None)
    assert arg_val is None or isinstance(arg_val, bool)
    arg_appeared = arg_val is not None and arg_val

    if not arg_appeared and not setting_appeared:
        return

    if not arg_appeared and setting_appeared:
        setattr(args, arg_name, True)
    elif arg_appeared and not setting_appeared:  # add value to settings
        settings_str = f'-{setting_name}'
        if args.settings is None:
            args.settings = list()
        args.settings.append(settings_str)  # the settings are now no longer sorted alphabetically
    else:  # both a setting and an argument were used
        all_warnings.add(f"Redundant use of argument {arg_name} and setting {setting_name}")

    for warning in all_warnings:
        arg_logger.warning(warning)


def __check_bool_arg_and_explicit_setting_consistency(args: argparse.Namespace, arg_name: str, setting_name: str) \
        -> None:
    """
    We accept two syntaxes for settings: --rule or --settings -rule.
    This function checks boolean settings, that can appear with explicit value, like -ci_mode=true, or -ci_mode=false.
    We assume that by default the value of the setting is false. One can use -ci_mode=false, even though it should have
    no effect. --short_output, without any arguments, is the equivalent of -ci_mode=true.

    This function raises an exception if any of the following holds:
    1. The setting has no argument
    2. The setting has a non-boolean argument
    3. The settings appears multiple times with conflicting truth values, like --settings -ci_mode=false,-ci_mode=true
    4. The option appears, but also a setting with truth value false: --short_output --settings -ci_mode=false

    This function warns if it does not raise an exception, in each of the following redundant scenarios:
    1. The setting has truth value false
    2. We use both an option and a setting with truth value true

    After running this function, the value will be stored both in the settings and in the argument namespace.
    The order of flags in settings may now no longer be sorted alphabetically.

    @param args: a namespace containing command line arguments
    @param arg_name: name of the argument, for example: --optimistic_loop or --rule_sanity
    @param setting_name: name of the setting, for example: -assumeUnwindCondition or -ruleSanityChecks
    @raises argparse.ArgumentTypeError if there is an inconsistent use of the argument.
    """
    setting_truth_val = None
    all_warnings = set()

    if args.settings is not None:
        for setting in args.settings:
            setting_match = re.search(r'^-' + setting_name + r'(=[^=]+)?$', setting)
            if setting_match is not None:
                setting_expr = setting_match[0]
                if '=' not in setting_expr:
                    raise argparse.ArgumentTypeError(
                        f"Setting {setting_name} must get a boolean value: {setting_name}=true/false")
                else:
                    curr_truth_val = setting_match[0].split('=')[1].lower()
                    if curr_truth_val == 'true':
                        if setting_truth_val is None:
                            setting_truth_val = True
                        elif setting_truth_val:
                            all_warnings.add(f"setting {setting_name} was given the same value more than once: true")
                        else:
                            raise argparse.ArgumentTypeError(
                                f"setting {setting_name} was given two conflicting values: true and false")
                    elif curr_truth_val == 'false':
                        if setting_truth_val is None:
                            setting_truth_val = False
                        elif not setting_truth_val:
                            all_warnings.add(f"setting {setting_name} was given the same value more than once: false")
                        else:
                            raise argparse.ArgumentTypeError(
                                f"setting {setting_name} was given two conflicting values: true and false")
                    else:
                        raise argparse.ArgumentTypeError(
                            f"Setting {setting_name} must get a boolean value: {setting_name}=true/false")

    arg_val = getattr(args, arg_name, None)
    assert arg_val is None or isinstance(arg_val, bool)
    arg_appeared = arg_val is not None and arg_val

    if not arg_appeared and setting_truth_val is None:
        return

    if not arg_appeared and setting_truth_val is not None:  # Add value to args dictionary
        setattr(args, arg_name, setting_truth_val)
    elif arg_appeared and setting_truth_val is None:  # add value to settings
        settings_str = f'-{setting_name}=true'
        if args.settings is None:
            args.settings = list()
        args.settings.append(settings_str)  # the settings are now no longer sorted alphabetically
    else:  # both a setting and an argument were used
        if not setting_truth_val:
            raise argparse.ArgumentTypeError(f"{arg_name} and --setting -{setting_name}=false conflict each other")
        all_warnings.add(f"Redundant use of argument {arg_name} and setting {setting_name} with value false")

    for warning in all_warnings:
        arg_logger.warning(warning)


def check_arg_and_setting_consistency(args: argparse.Namespace) -> None:
    """
    Check consistency for all dually-defined arguments.
    An argument is consistent if it has at most a single value.
    If an argument is defined both as a command-line argument and inside settings, we warn the user.
    At the end of this functions, all the dually-defined argument values will appears in both the argument namespace and
     inside the settings list in the namespace.
    args.settings will be sorted in ascending order.
    @param args: a namespace containing command line arguments
    @raises argparse.ArgumentTypeError if there is a dually-defined argument.
    """
    for (argument, setting) in val_arg_to_setting.items():
        __check_single_arg_and_setting_consistency(args, argument, setting, False)

    for (argument, setting) in val_arg_to_list_setting.items():
        __check_single_arg_and_setting_consistency(args, argument, setting, True)

    for (argument, setting) in bool_arg_to_implicit_setting.items():
        __check_bool_arg_and_implicit_setting_consistency(args, argument, setting)

    for (argument, setting) in bool_arg_to_explicit_setting.items():
        __check_bool_arg_and_explicit_setting_consistency(args, argument, setting)

    if args.settings is not None:
        args.settings.sort()
