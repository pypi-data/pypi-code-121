# -*- coding: utf-8 -*-

from openpyxl import load_workbook
from pathlib import Path
import configparser
import io
import os
import pandas as pd
import pickle
import zipfile


class FileWriter:
    @staticmethod
    def get_excel_writer(file_name, append=True):
        try:
            if not append:
                writer = pd.ExcelWriter(file_name, engine='openpyxl')
                return writer
            book = load_workbook(file_name)  # existed
            writer = pd.ExcelWriter(file_name, engine='openpyxl')
            writer.book = book
            writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        except:
            writer = pd.ExcelWriter(file_name, engine='openpyxl')
        return writer

    @staticmethod
    def write_file_content(file_name, content):
        with io.open(file_name, "a", encoding="utf-8") as f:
            f.write(content)
        return

    @staticmethod
    def write_file_property(filename, section_name, key, value):
        config = configparser.ConfigParser()
        config.read(filename, encoding="utf-8")
        if section_name not in config:
            config.add_section(section_name)
        config.set(section_name, key, value)
        with io.open(filename, 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    @staticmethod
    def clear_file(file_name):
        io.open(file_name, 'w', encoding="utf-8").close()
        return

    @staticmethod
    def df_to_hdf(df, file_name):
        if Path(file_name).is_file():
            os.remove(file_name)
        df.to_hdf(file_name, 'table')
        return

    @staticmethod
    def object_dump_to_file(obj, file_name):
        if Path(file_name).is_file():
            os.remove(file_name)
        pickle.dump(obj, open(file_name, "wb"), protocol=2)
        return

    @staticmethod
    def zip_direction_file(path_name, file_name):
        zip_file = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(path_name):
            for file in files:
                zip_file.write(os.path.join(root, file), file, zipfile.ZIP_DEFLATED)
        zip_file.close()
        return