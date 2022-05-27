'''Utility Module'''
import re
import sys
import time
import inspect
import json
import hashlib
from os import path, mkdir
from PIL import Image, ImageColor

re_time_str_format = r'(\d\d)(:)(\d\d)'


def wait(seconds):
    '''Wait for number of seconds'''
    while seconds >= 0:
        for each_symbol in ['-', '\\', '|', '/']:
            print('{0}......[{1:.1f} sec]   '.format(each_symbol, seconds), end='\r')
            seconds -= 0.1
            time.sleep(0.1)
            if seconds < 0:
                break
            print('{0}......[{1:.1f} sec]'.format(each_symbol, seconds), end='\r')
            seconds -= 0.1
            time.sleep(0.1)
            if seconds < 0:
                break
            print('{0}......[{1:.1f} sec]'.format(each_symbol, seconds), end='\r')
            seconds -= 0.1
            time.sleep(0.1)
            if seconds < 0:
                break
    # time.sleep(1.5)
    print()
    

def get_line_number():
    '''Returns the current line number in the source code'''
    return inspect.currentframe().f_back.f_lineno


def crc32c(crc, data):
    '''Calculate the CRC32C as Digital Signature
        @param crc The initial CRC
        @param data The data that needs to be calculated, could be hexstring or byte array
        @return CRC of the command
    '''
    crc = (crc ^ 0xffffffff) & 0xffffffff
    i = 0
    poly = 0xedb88320
    # if the [data] is a byte array, convert it to hex string first
    if isinstance(data, bytes):
        data = data.hex().upper()

    while i < len(data):
        crc ^= (int(data[i] + data[i + 1], 16) & 0xff)
        j = 0
        while j < 8:
            crc = (crc >> 1) ^ poly if ((crc & 1) > 0) else crc >> 1
            j += 1
        i += 2
    crc = ~crc
    # return the CRC as a 4-byte integer
    return crc & 0xffffffff


def crc_fill(crc, data, length=-1):
    '''Calculate the CRC32C as Digital Signature and fill the bytes to the length
        @param crc The initial CRC
        @param data The data that needs to be calculated, must be bytes
        @param length The expected length of the output byte array
        @return Bytes with last four bytes been crc, length to be the length parsed in.
         None if length doesn't make sense
    '''
    result = None
    output_hex = False

    if isinstance(data, str):
        output_hex = True
        data = bytes.fromhex(data)
        if length % 2 == 0:
            length = int(length / 2)
        else:
            print("Error: invaild length ", length)
            length = 0

    if length > 5:
        while len(data) < length - 4:
            data += int(0xFF).to_bytes(1, 'little')

        data_hex = data.hex().upper()
        data += crc32c(crc, data_hex).to_bytes(4, 'little')
        if output_hex:
            result = data.hex().upper()
        else:
            result = data

    return result


def byte_fill(data, length, fill_byte=0xFF):
    '''Calculate the CRC32C as Digital Signature and fill the bytes to the length
        @param data The data that needs to be calculated, must be bytes
        @param length The expected length of the output byte array
        @return Bytes array of length. None if length doesn't make sense
    '''
    while len(data) < length:
        data += int(fill_byte).to_bytes(1, 'little')
    return data


def check_sum(command):
    '''Calculate the CRC for Error-Detection Purpose
        @param command R/W+Index+Parameters
        @return CRC of the command
    '''
    summ = 0
    # crc = ''
    for i in range(len(command)):
        # += for nimbus II and CAPS, ^= for nimbus unified H
        summ += ord(command[i:i + 1])
    crc = hex(summ)[2:].zfill(2)
    return crc[len(crc) - 2: len(crc)]


def load_json_file(file_path):
    """Load data from a JSON file"""
    # read JSON file
    with open(file_path, "r", encoding='UTF-8') as file:
        content_json = file.read()
    # convert JSON to Python Dict
    config = json.loads(content_json)
    return config


def json_to_file(config, file_path):
    """Dump data to a JSON file"""
    dir_name = path.dirname(file_path)
    if dir_name != '':
        if not path.isdir(dir_name):
            mkdir(dir_name)   
    if config == None:
        config = {}
    # convert Python Dict to JSON:
    config_json = json.dumps(config, indent=4)
    # Save to JSON file
    with open(file_path, "w+", encoding='UTF-8') as file:
        file.write(config_json)
    absolute_path = path.abspath(file_path)
    return absolute_path


def file_to_list(file_path, ignore_empty_line=True, strip_line=True):
    '''Convert each line in a text file into a list'''
    text_line_list = []
    file = open(file_path, "r")
    for each_line in file:
        if ignore_empty_line:
            if each_line.strip() != '':
                if strip_line:
                    text_line_list.append(each_line.strip())
                else:
                    text_line_list.append(each_line.rstrip())
        else:
            if strip_line:
                text_line_list.append(each_line.strip())
            else:
                text_line_list.append(each_line.rstrip())
    return text_line_list


def list_to_file(content_list, file_path):
    '''Save each element of the list to a text file'''
    dir_name = path.dirname(file_path)
    if dir_name != '':
        if not path.isdir(dir_name):
            mkdir(dir_name)   
            
    file = open(file_path, "w")
    for each_element in content_list: 
        file.write(each_element)
        file.write('\n')
    file.close()
    absolute_path = path.abspath(file_path)
    return absolute_path


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def compare_numbers(num1, num2, operator, delta, delta_is_percentage):
    upper_limit = num2
    lower_limit = num2
    if delta is not None:
        if delta_is_percentage: 
            upper_limit = num2 * (1 + delta / 100)
            lower_limit = num2 * (1 - delta / 100)
        else:
            upper_limit = num2 + delta
            lower_limit = num2 - delta
    
    if operator == '<=':
        if delta is None:
            return (num1 <= num2)
        else:
            return num1 <= upper_limit
    elif operator == '<':
        if delta is None:
            return (num1 < num2)
        else:
            return num1 < upper_limit
    elif operator == '==':
        if delta is None:
            return (num1 == num2)
        else:
            return lower_limit <= num1 <= upper_limit 
    elif operator == '>=':
        if delta is None:
            return (num1 >= num2)
        else:
            return num1 >= lower_limit
    elif operator == '>':
        if delta is None:
            return (num1 > num2)
        else:
            return num1 > lower_limit


def int_to_time_str(time_int, time_format='hh:mm:ss'):
    '''Convert integer to time format [hh:mm] string'''
    time_hour_str = str(int(time_int / 3600)).zfill(2)
    time_minute_str = str(int((time_int % 3600) / 60)).zfill(2)
    time_second_str = str(int((time_int % 3600) % 60)).zfill(2)
    time_str = time_hour_str + ':' + time_minute_str + ':' + time_second_str
    if time_format == 'hh:mm':
        time_str = time_hour_str + ':' + time_minute_str
    return time_str  


def time_str_to_int(time_str):
    '''Convert time format [hh:mm] string to integer'''
    match_result = re.match(re_time_str_format, time_str)
    time_int = int(match_result[1]) * 3600 + int(match_result[3]) * 60
    return time_int  


def hex_to_bitmap(hex_list):
    '''Convert screenshot hex list to bitmap
        ex. the bitmap is a 64x128 list
    '''
    byte_array_list = []
    for i in range(len(hex_list)):
        # Convert each line Hex string to Byte array
        # ex. 'FFFFFFFF' -> b'\xFF\xFF\xFF\xFF'
        byte_array = bytes.fromhex(hex_list[i])
        byte_array_list.append(byte_array)
    
    bit_str_list_list = []
    for i in range(len(byte_array_list)):
        # Convert each line Byte array to bit string list
        bit_str_list = []
        for j in range(len(byte_array_list[i])):
            # Convert Byte to Bit string
            # ex. 255 -> '0b11111111'
            # and ignore the first '0b' in '0b11111111'
            # [bit_str] is the VERTICAL bit string of ONE BYTE
            bit_str = bin(byte_array_list[i][j])[2:].zfill(8)
            bit_str_list.append(bit_str)
        bit_str_list_list.append(bit_str_list)
    
    bitmap_str_list = []
    # print('len(bit_str_list_list) = {}'.format(len(bit_str_list_list)))
    for i in range(len(bit_str_list_list)):
        bit_str_list = bit_str_list_list[i]
        # print('bit_str_list = {}'.format(bit_str_list))
        # print('len(bit_str_list[0]) = {}'.format(len(bit_str_list[0])))
        for j in range(len(bit_str_list[0])):
            bitmap_str_line = ''
            for k in range(len(bit_str_list)):
                # [bitmap_str_line] is the HORIZONTAL bit string WHOLE LINE
                bitmap_str_line += bit_str_list[k][7 - j]
            print(bitmap_str_line)
            bitmap_str_list.append(bitmap_str_line)
    return bitmap_str_list   


def apply_screenshot_masks(screenshot_bitmap, bitmap_masks):
    '''Apply screenshot masks'''
    if bitmap_masks != []:
        for each_mask in bitmap_masks:
            for i in range(each_mask['height']):
                screenshot_bitmap[each_mask['row'] + i] = screenshot_bitmap[each_mask['row'] + i][:each_mask['column']] \
                                                        +''.zfill(each_mask['width']) \
                                                        +screenshot_bitmap[each_mask['row'] + i][each_mask['column'] + each_mask['width']:]
    return screenshot_bitmap                               


def bitmap_to_image(bitmap_str_list, image_path, bitmap_masks=[]):
    '''Generate photo from Bitmap'''
    # Create directory if not exist
    dir_name = path.dirname(image_path)
    if dir_name != '':
        if not path.isdir(dir_name):
            mkdir(dir_name)
    # Apply masks
    bitmap_str_list = apply_screenshot_masks(bitmap_str_list, bitmap_masks)
    # Create image
    num_line = len(bitmap_str_list)
    num_colume = len(bitmap_str_list[0])
    image = Image.new('1', (num_colume, num_line), color=1)  # create the Image of size 1 pixel 
    for i in range(num_line):
        for j in range(num_colume):
            if bitmap_str_list[i][j] == '1': 
                image.putpixel((j, i), ImageColor.getcolor('black', '1'))
    image = image.resize((num_colume * 1, num_line * 1), resample=0)
    image.save(image_path)
    absolute_path = path.abspath(image_path)
    return absolute_path


def compare_file_equal(file_path, ref_file_path):
    '''Compare two files equal by using MD5'''
    file_handler = open(file_path, 'rb')
    realtime_md5 = hashlib.md5(file_handler.read()).hexdigest()
    file_handler.close()
    ref_file_handler = open(ref_file_path, 'rb')
    reference_md5 = hashlib.md5(ref_file_handler.read()).hexdigest()
    ref_file_handler.close()
    if realtime_md5 == reference_md5:
        return True
    else:
        return False
    
    
def main(argv):
    '''main function'''
    print(len(argv))
    print('line #: {}'.format(get_line_number()))
    

if __name__ == "__main__":
    main(sys.argv)
