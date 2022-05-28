"""
Reads and prints approximations to (a) π, from a text file at the root of the package source directory and (b) `e` from
a text file in a subfolder "sample_data". 
"""

import argparse
from importlib.resources import files

from yachalk import chalk

from . import constants

def main():
    print("I am here, in __main__.py.")
    print("\n" + 15*"# " + "\n")

    # Checks for command line argument 
    user_contribution = check_CLI_for_user_input()
    if len(user_contribution) == 0:
        print("The user declined to share any knowledge. 🙁\n")
    else:
        user_wisdom = " ".join(user_contribution)
        print(f"The user chose to share: “{user_wisdom}”\n")

    print_value_from_resource("π", constants.PACKAGENAME_PI, constants.FILENAME_PI)
    print_value_from_resource("e", constants.PACKAGENAME_E, constants.FILENAME_E)
    print("\nPlease don’t be concerned when you see the following error message. It’s expected.")
    print_value_from_resource("Meaning of life", constants.PACKAGENAME_MOL, constants.FILENAME_MOL)
    print("\n" + 15*"* " + "\n")

    # For the rationale for `return 0`, see
    # https://docs.python.org/3/library/__main__.html#packaging-considerations
    # (`main` functions are often used to create command-line tools by specifying them as entry points for console
    # scripts. When this is done, pip inserts the function call into a template script, where the return value of `main`
    # is passed into `sys.exit()`, which expects a return value. By proactively specifying this return value, the
    # module will have the same behavior when run directly (i.e., `python my_module.py`) as it will as a console script
    # entry point in a pip-installable package.)
    # (That said, even without this, I can't run my_module.py directly, because it chokes on the import statement
    # `from . my_module import main` with the error message:
    #    ImportError: attempted relative import with no known parent package
    # So, this return statement may not have an actual benefit, but it certainly does no harm either.
    return 0


def check_CLI_for_user_input():
    parser = argparse.ArgumentParser()

    # Defines argument
    #   nargs='*': All command-line arguments present are gathered into a list.
    #       This allows the user to type a multi-word string without wrapping it in quotes.
    #   If no command-line argument is present, the value from default will be produced.
    #   type=str is included for clarity, but str  is the default type.
    help_text = "Please share some wisdom (as a string of words, with or without enclosing quotation marks)"
    parser.add_argument("user_wisdom", type=str, nargs='*', default=None, help=help_text)

    # Parses argument(s) from CLI and assigns to left-hand side
    cli_arguments = parser.parse_args()

    # Reference an arg with dot notation, using the string with which the .add_argument was called
    return cli_arguments.user_wisdom


def print_value_from_resource(message, packagename, filename):
    """
    Outputs the text read from a resource (identified by its immediately enclosing package and the resource’s filename),
    and prefix this output by the supplied `message`.
    """
    data = read_text_from_resource(packagename, filename)
    print(f"{message}: {data}")


def read_text_from_resource(packagename, filename):
    """
    Read and return text from a resource identified by its immediately enclosing package and the resource’s filename.

    If either the file/module is not found, or if the returned string is empty, instead return a string expressing
    cluelessness that will be incorporated into __main__.py's output.
    """
    try:
        # The following is equivalent to using the “/” in the next following line.
        # resource_location_as_string = files(packagename).joinpath(filename)
        resource_location_as_string = files(packagename) / filename

        # Use the following substitute only to test the "module not found" trap
        # resource_location_as_string = files('nonexistent_package') / filename

        data = resource_location_as_string.read_text()

        if not data:
            data = constants.CLUELESS_STRING
            print(f"\nOops! I found and read the data file {filename}, but it was empty.")
            print(f"Location:\n»» {resource_location_as_string}.")


        # Uncomment next line to test unanticipated error in the try … except block
        # y = 3/0
        
    except ModuleNotFoundError as errormessage_MNF:
        print(f"\nOops! The package name «{packagename}» was not a module that could be found.")
        print(f"»» {errormessage_MNF}")
        data = constants.CLUELESS_STRING
        return data
    except FileNotFoundError as errormessage_FNF:
        error_print(f"\nOops! The data file «{filename}» wasn’t found at this location:\n»» {resource_location_as_string}.")
        error_print(errormessage_FNF)
        data = constants.CLUELESS_STRING
        return data
    else:
        return data


def error_print(error_message):
    """
    Prints supplied error message to console with special error-message formatting
    """
    print(chalk.red(error_message))
    