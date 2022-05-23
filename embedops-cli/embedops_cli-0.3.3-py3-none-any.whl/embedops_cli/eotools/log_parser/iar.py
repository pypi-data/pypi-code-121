"""Regex pattern for parsing the output of an IAR build"""


COMPILER_PATTERN = r"IAR ANSI C/C++ Compiler (V8.50.1.245/W32) for ARM"

# regex pattern for IAR size default output
# Example:
# https://regex101.com/r/QzCGwl/1
# b"  56'772 bytes of readonly  code memory"
# b"  14'128 bytes of readonly  data memory"
# b"  22'623 bytes of readwrite data memory"

SIZE_PATTERN = (
    r"(?P<flash_code_size>[\d']+).+readonly\s+code.+\n(?:b\")\s+"
    r"(?P<flash_data_size>[\d']+).+readonly\s+data.+\n(?:b\")\s+"
    r"(?P<ram_size>[\d']+).+readwrite\s+data.+"
)

WARNING_PATTERN = (
    r"(?:\"?(.*?)\"?[\(,](\d+)\)?\s+(?::\s)?)"
    r"(Error|Remark|Warning|Fatal[E|e]rror)\[(.*)\]: (.*)$"
)
