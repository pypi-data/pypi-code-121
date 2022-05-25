# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.api.dtm_pb2 import ArchitectureComponent as ArchCompDtm
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class ArchitectureComponent(object):
    """
    Wrapper around api.dtm_pb2.ArchitectureComponent
    """

    def __init__(self, db_info: dict):
        self.db_info = db_info
        self.type = "db"
        self.url = (
            db_info.get("database")
            if db_info.get("database")
            else (db_info.get("vendor") or "default")
        )

    def to_dtm(self):
        arch_comp = ArchCompDtm()
        arch_comp.type = self.type
        arch_comp.url = self.url

        # vendor must be a string that exactly matches a value from
        # Teamserver's flowmap/technologies.json > service > one of "name"
        if self.db_info.get("vendor"):
            arch_comp.vendor = self.db_info.get("vendor")

        if self.db_info.get("host"):
            arch_comp.remote_host = self.db_info.get("host")

        if self.db_info.get("port"):
            port = self.db_info.get("port")
            try:
                arch_comp.remote_port = int(port)
            except ValueError:
                arch_comp.remote_port = -1

        return arch_comp

    def to_json(self):
        json = {
            "type": self.type,
            "url": self.db_info.get("database")
            if self.db_info.get("database")
            else (self.db_info.get("vendor") or "default"),
        }

        # vendor must be a string that exactly matches a value from
        # Teamserver's flowmap/technologies.json > service > one of "name"
        if self.db_info.get("vendor"):
            json["vendor"] = self.db_info.get("vendor")

        if self.db_info.get("host"):
            json["remoteHost"] = self.db_info.get("host")

        if self.db_info.get("port"):
            port = self.db_info.get("port")
            try:
                json["remotePort"] = str(int(port))
            except ValueError:
                # don't report port if it's not an int
                pass

        return json
