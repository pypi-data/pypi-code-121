"""Regex pattern for parsing the output of `size` in the berkeley format"""
# regex pattern for arm-gcc-eabi-size in Berkeley format
# Example:
# https://regex101.com/r/f0wctA/1
# [ 99%] Linking C executable application.elf
#   text	   data	    bss	    dec	    hex	filename
#  130584	   2064	  69440	 202088	  31568	application.elf

# bss=>RAM
# data=>RAM (variables) + FLASH (initialization constants)
# text=> FLASH
SIZE_PATTERN = (
    r"text\s+data\s+bss\s+dec\s+hex\s+filename\n\s+"
    r"(?P<flash_code_size>\d+)\s+"
    r"(?P<flash_data_size>\d+)\s+"
    r"(?P<ram_size>\d+)\s+"
    r"(?P<dec>\d+)\s+"
    r"(?P<hex>[a-fA-F0-9]+)\s+"
    r"(?P<build_output_filename>\S+)"
)
