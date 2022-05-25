"""A vulnerability notice"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Advisory:  # pylint: disable=too-many-instance-attributes
    """A vulnerability notice"""
    access: Optional[str] = None
    cvss_score: Optional[float] = None
    identifier: Optional[str] = None
    overview: Optional[str] = None
    patched_versions: Optional[str] = None
    recommendation: Optional[str] = None
    references: Optional[str] = None
    severity: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    vulnerable_versions: Optional[str] = None

    def __str__(self):
        if self.severity:
            return f"known vulnerability (severity `{self.severity}`)"
        return "known vulnerability"
