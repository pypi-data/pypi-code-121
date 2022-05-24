import os
import sys
import importlib
import string
import logging
import traceback

########################################################
# Helper functions
########################################################
def extend_run_commandset(_run, config):
    """
    Load commands from the libraries specified
    """

    debug = config.debug
    paths = config.get_library_paths()

    if debug:
        logging.debug("Loading run commands")

    for p in paths:

        # Enable import from these directories
        p = os.path.abspath(p)
        if not os.path.exists(p):
            if debug:
                logging.debug("Unable to load path: {}".format(p))
            continue

        sys.path.append(p)

        commands = os.listdir(p)
        for c in commands:

            fullpath = os.path.join(p, c)

            #####################################
            # Check if I should skip it
            #####################################
            skip = False
            suffixes = [".pyc", ".pyo", "__pycache__", "#", "~"]
            for s in suffixes:
                if c.endswith(s):
                    skip = True
                    break
            if skip:
                if debug:
                    logging.debug("Skipping: {}".format(c))
                continue

            try:
                # => Get the spec...
                # Handle directories differently...
                modname = "".join([x if x in string.ascii_letters else "_" for x in c])
                if os.path.isdir(fullpath):
                    spec = importlib.util.find_spec(c)
                else:
                    spec = importlib.util.spec_from_file_location(modname, fullpath)

                if spec is None:
                    if debug:
                        logging.debug("can't find the module")
                    continue

                # If you chose to perform the actual import ...
                mod = importlib.util.module_from_spec(spec)
                if mod is None and spec.loader is not None:
                    if debug:
                        logging.debug(
                            "Loaded module is None or the loader is missing: {}".format(
                                c
                            )
                        )
                    continue

                spec.loader.exec_module(mod)
                if not hasattr(mod, "entrypoint"):
                    if debug:
                        logging.debug(
                            "Loaded module does not have 'entrypoint' attribute: {}".format(
                                c
                            )
                        )
                    continue

                _run.add_command(mod.entrypoint)
            except:
                if debug:
                    traceback.print_exc()
                pass

            if debug:
                logging.debug("Loaded module: {}".format(c))

        if debug:
            logging.debug("Completed loading commands")
