"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2017 Laurent Labatut / Laurent Champagnac
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# ===============================================================================
"""

# Import
import logging

import os
import codecs

from pysolbase.SolBase import SolBase

logger = logging.getLogger(__name__)


class FileUtility(object):
    """
    File utility
    """

    @staticmethod
    def is_path_exist(path_name):
        """
        Check if a path (file or dir) name exist.
        :param path_name: Path name.
        :type path_name text_type
        :return: Return true (exist), false (do not exist, or invalid file name)
        :rtype bool
        """

        # Check
        if path_name is None:
            logger.warning("is_path_exist : file_name is None")
            return False
        elif not isinstance(path_name, str):
            logger.warning("is_path_exist : path_name not a text_type, className=%s", SolBase.get_classname(path_name))
            return False

        # Go
        return os.path.exists(path_name)

    @staticmethod
    def is_file_exist(file_name):
        """
        Check if file name exist.
        :param file_name: File name.
        :type file_name: str
        :return: Return true (exist), false (do not exist, or invalid file name)
        :rtype bool
        """

        # Check
        if file_name is None:
            logger.warning("is_file_exist : file_name is None")
            return False
        elif not isinstance(file_name, str):
            logger.warning("is_file_exist : file_name not a text_type, className=%s", SolBase.get_classname(file_name))
            return False

        # Go
        return os.path.isfile(file_name)

    @staticmethod
    def is_dir_exist(dir_name):
        """
        Check if dir name exist.
        :param dir_name: Directory name.
        :type dir_name: str
        :return: Return true (exist), false (do not exist, or invalid file name)
        :rtype bool
        """

        # Check
        if dir_name is None:
            logger.warning("is_dir_exist : file_name is None")
            return False
        elif not isinstance(dir_name, str):
            logger.warning("is_dir_exist : file_name not a text_type, className=%s", SolBase.get_classname(dir_name))
            return False

        # Go
        return os.path.isdir(dir_name)

    @staticmethod
    def get_file_size(file_name):
        """
        Return a file size in bytes.
        :param file_name: File name.
        :type file_name: str
        :return: An integer, gt-eq 0 if file exist, lt 0 if error.
        :rtype int
        """
        if not FileUtility.is_file_exist(file_name):
            return -1
        else:
            return os.path.getsize(file_name)

    @classmethod
    def get_current_dir(cls):
        """
        Return the current directory.
        :return: A String
        :rtype text_type
        """

        return os.getcwd()

    @staticmethod
    def file_to_binary(file_name):
        """
        Load a file toward a binary buffer.
        :param file_name: File name.
        :type file_name: str
        :return: Return the binary buffer or None in case of error.
        :rtype: bytes,None
        """

        # Check
        if not FileUtility.is_file_exist(file_name):
            logger.warning("file_to_binary : file_name not exist, file_name=%s", file_name)
            return None

        # Go
        rd = None
        try:
            # Open (binary : open return a io.BufferedReader)
            rd = open(file_name, "rb")

            # Read everything
            return rd.read()
        except IOError as e:
            # Exception...
            logger.warning("IOError, ex=%s", SolBase.extostr(e))
            return None
        except Exception as e:
            logger.warning("Exception, ex=%s", SolBase.extostr(e))
            return None
        finally:
            # Close if not None...
            if rd:
                rd.close()

    @staticmethod
    def file_to_textbuffer(file_name, encoding):
        """
        Load a file toward a text buffer (UTF-8), using the specify encoding while reading.
        CAUTION : This will read the whole file IN MEMORY.
        :param file_name: File name.
        :type file_name: str
        :param encoding: Encoding to use.
        :type encoding: str
        :return: A text buffer or None in case of error.
        :rtype str
        """

        # Check
        if not FileUtility.is_file_exist(file_name):
            logger.warning("file_to_textbuffer : file_name not exist, file_name=%s", file_name)
            return None

        # Go
        rd = None
        try:
            # Open (text : open return a io.BufferedReader)
            rd = codecs.open(file_name, "r", encoding, "strict", -1)

            # Read everything
            return rd.read()
        except IOError as e:
            # Exception...
            logger.warning("file_to_binary : IOError, ex=%s", SolBase.extostr(e))
            return None
        except Exception as e:
            logger.warning("file_to_binary : Exception, ex=%s", SolBase.extostr(e))
            return None
        finally:
            # Close if not None...
            if rd:
                rd.close()

    @staticmethod
    def append_binary_to_file(file_name, bin_buf):
        """
        Write to the specified filename, the provided binary buffer.
        Create the file if required.
        :param file_name:  File name.
        :type file_name: str
        :param bin_buf: Binary buffer to write.
        :type bin_buf: bytes
        :return: The number of bytes written or lt 0 if error.
        :rtype int
        """

        # Go
        rd = None
        try:
            # Open (text : open return a io.BufferedReader)
            rd = open(file_name, "ab+")

            # Read everything
            return rd.write(bin_buf)
        except IOError as e:
            # Exception...
            logger.warning("append_binary_to_file : IOError, ex=%s", SolBase.extostr(e))
            return -1
        except Exception as e:
            logger.warning("append_binary_to_file : Exception, ex=%s", SolBase.extostr(e))
            return -1
        finally:
            # Close if not None...
            if rd:
                rd.close()

    @staticmethod
    def append_text_to_file(file_name, text_buffer, encoding, overwrite=False):
        """
        Write to the specified filename, the provided binary buffer
        Create the file if required.
        :param file_name:  File name.
        :type file_name: str
        :param text_buffer: Text buffer to write.
        :type text_buffer: str
        :param encoding: The encoding to use.
        :type encoding: str
        :param overwrite: If true, file is overwritten.
        :type overwrite: bool
        :return: The number of bytes written or lt 0 if error.
        :rtype int
        """

        # Go
        rd = None
        try:
            # Open (text : open return a io.BufferedReader)
            if not overwrite:
                rd = codecs.open(file_name, "a+", encoding, "strict", -1)
            else:
                rd = codecs.open(file_name, "w", encoding, "strict", -1)

            # Read everything
            # CAUTION : 2.7 return None :(
            return rd.write(text_buffer)
        except IOError as e:
            # Exception...
            logger.warning("append_text_to_file : IOError, ex=%s", SolBase.extostr(e))
            return -1
        except Exception as e:
            logger.warning("append_text_to_file : Exception, ex=%s", SolBase.extostr(e))
            return -1
        finally:
            # Close if not None...
            if rd:
                rd.close()
