import socket
import os
from urllib.request import urlretrieve, urlopen
from urllib.error import URLError
from wizzi_utils.misc import misc_tools as mt


def open_server(server_address: tuple = ('localhost', 10000), ack: bool = True, tabs: int = 1) -> socket:
    """
    :param server_address:
    :param ack:
    :param tabs:
    see open_server_test()
    """
    if ack:
        print('{}Opening server on IP,PORT {}'.format(tabs * '\t', server_address))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen(1)
    return sock


def get_host_name() -> str:
    """
    :return: hostname
    try using misc_tools.get_pc_name() instead
    see get_host_name_test()
    """
    hostname = socket.gethostname()
    return hostname


def get_ipv4() -> str:
    """
     :return ipv4 address of this computer
     see get_ipv4_test()
     """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipv4 = s.getsockname()[0]
    return ipv4


def send_msg(connection: socket, buflen: int, data: str, msg_end: str) -> None:
    """
    :param connection: the connection of this client\server to the server\client
    :param buflen: needed to split the message if it is longer than 'buflen'
    :param data: string to send
    :param msg_end: special string that notifies when the msg is over(faster than try catch)
        MUST BE A STRING THAT CANT APPEAR ON MESSAGES - e.g. "$#$#"
    see open_server_test()
    """
    data_e = str.encode(data + msg_end)
    data_e_len = len(data_e)
    for i in range(0, data_e_len, buflen):
        chunk_i = data_e[i:i + buflen]
        connection.send(chunk_i)
    return


def receive_msg(connection: socket, buflen: int, msg_end: str) -> str:
    """
    :param connection: the connection of this client\server to the server\client
    :param buflen: needed to receive the message in chunks
    :param msg_end: special string that notifies when the msg is over(faster than try catch)
        MUST BE A STRING THAT CANT APPEAR ON MESSAGES - e.g. "$#$#"
    :return: string of the received data
    see open_server_test()
    """
    data_in = ''
    saw_end_delimiter = False
    while not saw_end_delimiter:
        data_in += connection.recv(buflen).decode('utf-8')
        if not data_in:
            break  # empty transmission
        if data_in.endswith(msg_end):
            data_in = data_in.replace('$#$#', '')
            saw_end_delimiter = True

    return data_in


def buffer_to_str(data: str, prefix: str, tabs: int = 1, max_chars: int = 100) -> str:
    """
    :param data: data as string
    :param prefix: string prefix e.g. 'in', 'out', 'server', 'client'
    :param tabs:
    :param max_chars:
    :return: pretty print of the buffer
    see buffer_to_str_test()
    """
    data_len = len(data)
    data_chars = data_len + 1 if data_len <= max_chars else max_chars

    msg = '{}{}: {} (bytes sent={})'.format(tabs * '\t', prefix, data[:data_chars], data_len)
    if data_len > max_chars:
        msg += ' ... message is too long'
    return msg


def download_file(url: str, dst_path: str = './file', tabs: int = 1) -> bool:
    """
    :param url:
    :param dst_path: where to save the file.
        if dst_path contains non existing folders - it will fail.
            use mt.create_dir(dir) for new dirs
    :param tabs:
    :return: bool 1 for success
    see download_file_test()
    see load_img_from_web() in test_open_cv_tools.py
    """
    filename = url.split('/')[-1]

    def download_progress_hook(count, blockSize, totalSize):
        if totalSize < 0:  # saw this once
            percent = 'N\A'
            size_s = 'size N\A'
        else:
            percent = '{:.1f}%'.format(min(float(count * blockSize) / float(totalSize) * 100.0, 100))
            size_s = mt.convert_size(totalSize)
        print("\r{}Completed: {} from {} - {}".format((tabs + 1) * '\t', percent, size_s, filename), end="")
        return

    ret = False
    if not os.path.exists(dst_path):
        try:
            if mt.is_windows():
                # in windows - add prefix which allows the file name to be longer than the default len (70 chars)
                dst_path = mt.full_path_no_limit(dst_path)
                if len(os.path.basename(dst_path)) > 255:
                    err = 'len(os.path.basename(dst_path))={} exceeds the maximal length which is 255 chars. '
                    err += 'dst_path = {}'
                    mt.exception_error(err.format(len(os.path.basename(dst_path)), os.path.basename(dst_path)),
                                       real_exception=False, tabs=tabs)
                    return False
            msg = 'Downloading from {} to {}'.format(url, dst_path)
            print('{}{}'.format(tabs * '\t', mt.add_color(msg, ops='light_magenta')))
            urlretrieve(url, dst_path, download_progress_hook)
            print()  # release cartridge
            ret = True
        except URLError as e:
            mt.exception_error('{} {}'.format(e, url), real_exception=True, tabs=tabs + 1)
        except FileNotFoundError as e:
            mt.exception_error('{}'.format(e), real_exception=True, tabs=tabs + 1)

    else:
        mt.exception_error(mt.EXISTS.format(dst_path), real_exception=False, tabs=tabs)
    return ret


def get_file_size_by_url(url: str) -> str:
    try:
        obj_info = urlopen(url)
        size_int = int(obj_info.getheader('Content-Length'))
        size_pretty = mt.convert_size(size_bytes=size_int)
    except URLError as e:
        mt.exception_error('with file {} error: {}'.format(url, e), real_exception=True, tabs=1)
        size_pretty = 'N/A'
    return size_pretty
