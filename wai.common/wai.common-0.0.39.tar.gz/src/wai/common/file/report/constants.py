"""
Constants related to ADAMS reports.
"""
# The file extension of a report file
EXTENSION: str = ".report"

# The suffix for the names of properties which represent the datatype of another property
DATATYPE_SUFFIX: str = "\tDataType"

# The parent ID property
PROPERTY_PARENTID: str = "Parent ID"

# The database ID used when none is given
NO_ID: int = -1

# Field: Dummy report (in case there was no quantitation report and a
# dummy report was generated automatically)
FIELD_DUMMYREPORT: str = "Dummy report"

# Field: Excluded (= dodgy)
FIELD_EXCLUDED: str = "Excluded"
