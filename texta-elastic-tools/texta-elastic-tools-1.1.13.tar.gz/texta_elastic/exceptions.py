class NotFoundError(Exception):
    """Raised when not found."""
    pass

class ElasticsearchError(Exception):
    """Raised elasticsearch Error."""
    pass

class DocPathsWithoutValuesAggregationError(Exception):
    """Raised when the user defines aggregations with include_values=False and include_doc_paths=True"""
    pass

class KeyFieldEqualsValueFieldError(Exception):
    """Raised when the user tries to use the same value for key_field and value_field while aggregating over facts in facts_abstract."""
    pass

class InvalidKeyFieldError(Exception):
    """Raised when the user tries to use inavlid key_field while aggregating over facts in facts_abstract."""
    pass

class InvalidValueFieldError(Exception):
    """Raised when the user tries to use invalid value_field while aggregating over facts in facts_abstract."""
    pass
