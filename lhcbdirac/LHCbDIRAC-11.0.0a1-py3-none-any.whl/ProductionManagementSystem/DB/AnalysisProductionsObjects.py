###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Table/object defintions used in the AnalysisProductionsDB"""
from sqlalchemy import Integer, Column, String, JSON, DateTime, func, ForeignKey, Float
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
Base.__table_args__ = {
    "mysql_engine": "InnoDB",
    "mysql_charset": "utf8",
}


class Request(Base):
    __tablename__ = "ap_requests"

    VALID_STATES = [
        "waiting",
        "active",
        "replicating",
        "ready",
    ]
    request_id = Column(Integer, primary_key=True)
    state = Column(String(16), nullable=False, default="waiting")
    progress = Column(Float, nullable=True)
    last_state_update = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    name = Column(String(256), nullable=False)
    version = Column(String(64), nullable=False)
    auto_tags = relationship("AutoTag", back_populates="request", lazy="selectin")
    # TODO: Use the mutable extension and validate this object better?
    extra_info = Column(JSON(), nullable=False, default=lambda: {"transformations": []})

    @validates("name")
    def convert_lower(self, key, value):
        return value.lower()

    def toDict(self):
        result = {
            "name": self.name,
            "version": self.version,
            "request_id": self.request_id,
            "state": self.state,
            "last_state_update": self.last_state_update,
            "transformations": self.extra_info["transformations"],
        }
        if self.progress is not None:
            result["progress"] = self.progress
        if "jira_task" in self.extra_info:
            result["jira_task"] = self.extra_info["jira_task"]
        if "merge_request" in self.extra_info:
            result["merge_request"] = self.extra_info["merge_request"]
        return result


class AnalysisSample(Request):
    __tablename__ = "ap_analysis_samples"

    sample_id = Column(Integer, primary_key=True)
    wg = Column(String(16), nullable=False)
    analysis = Column(String(256), nullable=False)
    request_id = Column(Integer, ForeignKey("ap_requests.request_id"), nullable=False)

    owners = relationship("User", back_populates="sample", lazy="selectin")
    tags = relationship("Tag", back_populates="sample", lazy="selectin")
    publications = relationship("Publication", back_populates="sample", lazy="selectin")

    # Allow this table to be temporally versioned
    validity_start = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    validity_end = Column(DateTime(timezone=False), nullable=True)

    @validates("wg", "analysis")
    def convert_lower(self, key, value):
        return value.lower()

    def toDict(self):
        result = Request.toDict(self)
        result.update(
            {
                "wg": self.wg,
                "analysis": self.analysis,
                "sample_id": self.sample_id,
                "owners": [o.username for o in self.owners],
                "validity_start": self.validity_start,
                "validity_end": self.validity_end,
            }
        )
        return result


class User(Base):
    __tablename__ = "ap_users"

    id = Column(Integer, primary_key=True)
    username = Column(String(256), nullable=False)
    sample_id = Column(Integer, ForeignKey("ap_analysis_samples.sample_id"), nullable=False)
    sample = relationship("AnalysisSample", back_populates="owners", lazy="selectin")

    # Allow this table to be temporally versioned
    validity_start = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    validity_end = Column(DateTime(timezone=False), nullable=True)

    @validates("username")
    def convert_lower(self, key, value):
        return value.lower()


class Publication(Base):
    __tablename__ = "ap_publications"

    id = Column(Integer, primary_key=True)
    number = Column(String(64), nullable=False)
    sample_id = Column(Integer, ForeignKey("ap_analysis_samples.sample_id"), nullable=False)
    sample = relationship("AnalysisSample", back_populates="publications", lazy="selectin")

    @validates("number")
    def convert_upper(self, key, value):
        return value.upper()


class Tag(Base):
    __tablename__ = "ap_tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    value = Column(String(64), nullable=False)
    sample_id = Column(Integer, ForeignKey("ap_analysis_samples.sample_id"), nullable=False)
    sample = relationship("AnalysisSample", back_populates="tags", lazy="joined")

    # Allow this table to be temporally versioned
    validity_start = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    validity_end = Column(DateTime(timezone=False), nullable=True)

    @validates("name", "value")
    def convert_lower(self, key, value):
        return value.lower()


class AutoTag(Base):
    __tablename__ = "ap_auto_tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    value = Column(String(64), nullable=False)
    request_id = Column(Integer, ForeignKey("ap_requests.request_id"), nullable=False)
    request = relationship("Request", back_populates="auto_tags", lazy="joined", enable_typechecks=False)

    @validates("name", "value")
    def convert_lower(self, key, value):
        return value.lower()
