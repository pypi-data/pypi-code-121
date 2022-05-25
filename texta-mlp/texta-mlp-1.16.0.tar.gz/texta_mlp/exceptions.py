class LanguageNotSupported(Exception):
    """Raised when MLP fails to detect language or language is not supported.""" 
    pass

class BoundedListEmpty(Exception):
    """Raised when in Concatenator class the BOUNDS are not yet loaded, but concatenate() is tried""" 
    pass

class StanzaPipelineFail(Exception):
    """Raised when Stanza pipelines fail to load."""
    pass

class CUDAException(Exception):
    """Raised when problems with CUDA settings or support."""
    pass
