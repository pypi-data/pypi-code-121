"""
Python module to initialize Server Extension for retrieving Rubin Observatory
settings.
"""

from typing import Dict, List

from .handlers import setup_handlers


def _jupyter_server_extension_paths() -> List[Dict[str, str]]:
    """
    Function to declare Jupyter Server Extension Paths.
    """
    # This comprehension actually works, but black can't handle it!
    # return [ {"module": f"rsp_jupyter_extensions.{ext}"} for ext in exts ]
    return [{"module": "rsp_jupyter_extensions"}]


def load_jupyter_server_extension(nbapp) -> None:
    """
    Function to load Jupyter Server Extension.
    """
    nbapp.log.info("Loading RSP server extensions.")
    setup_handlers(nbapp.web_app)
