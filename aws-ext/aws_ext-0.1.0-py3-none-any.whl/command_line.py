#!/usr/bin/env python3

# aws_ext - Active Directory tool
# Copyright (C) 2020 - matteo.redaelli@gmail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

import os
import logging
import datetime
import sys
import aws_ext
import boto3
import fire
from aws_ext import glue_databases
from typing import List, Tuple, Dict


def _connect(service):
    session = boto3.session.Session()
    return session.client(service)


class AwsExt(object):
    """*aws_ext* is a set of some useful utilities over aws sdk"""

    def get_tables_with_many_versions(self, databases=[], threshold=100):
        glue_client = _connect("glue")
        result = aws_ext.glue_databases.get_tables_with_many_versions(
            glue_client, databases, threshold
        )
        print(result)

    def exist_tables_with_many_versions(self, databases=[], threshold=100):
        glue_client = _connect("glue")
        result = aws_ext.glue_databases.exist_tables_with_many_versions(
            glue_client, databases, threshold
        )
        print(result)

    def count_tables(self, databases=[]):
        glue_client = _connect("glue")
        result = aws_ext.glue_databases.count_tables(glue_client, databases)
        print(result)
        logging.info(f"Tot tables = {result}")

    def count_tables_versions(self, databases=[]):
        glue_client = _connect("glue")
        result = aws_ext.glue_databases.count_tables_versions(glue_client, databases)
        print(result)
        logging.info(f"Tot tables and versions = {result}")

    def delete_old_tables_versions(self, databases=[], threshold=100, dryrun=True):
        glue_client = _connect("glue")
        result = aws_ext.glue_databases.delete_old_tables_versions(
            glue_client, databases, threshold, dryrun
        )
        print(result)


def main():
    """main"""
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    fire.Fire(AwsExt)


if __name__ == "__main__":
    main()
