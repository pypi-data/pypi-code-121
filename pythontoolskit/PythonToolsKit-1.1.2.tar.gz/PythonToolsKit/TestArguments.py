##########
# TEST 1
##########

# from Arguments import ArgumentParser, verbose as v
# from logging import getLogger
# import Arguments

# logger = getLogger(__name__)

# v("This line is not printed.")
# logger.debug("This line is not printed.")
# Arguments.verbose("This line is not printed.")

# print(v)

# a = ArgumentParser()
# a.add_verbose()
# a.add_debug()
# print(a.parse_args(["--debug", "--verbose"]))

# v("This line is printed.")
# logger.debug("This line is printed.")
# Arguments.verbose("This line is printed.")

# print(v)

# exit()

##########
# TEST 2
##########

# from Arguments import *

# verbose("This line is not printed.")

# a = ArgumentParser()
# a.add_verbose()
# a.add_debug()
# a.parse_args(["--debug", "--verbose"])

# verbose("This line is printed.")

# exit()

##########
# TEST 3
##########

# from Arguments import ArgumentParser

# a = ArgumentParser()
# a.add_verbose()
# a.add_debug()
# a.parse_args(["--debug", "--verbose"])

# from Arguments import verbose

# verbose("This line is printed.")

# exit()
