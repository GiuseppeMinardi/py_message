"""
Instagram chat parser implementation (DEPRECATED).
"""

import warnings
from typing import List

from models.message import Message
from .base import BaseParser


class InstagramParser(BaseParser):
    """
    DEPRECATED: Instagram parser is no longer supported.
    
    Instagram has changed their export format and this parser is outdated.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize with deprecation warning."""
        warnings.warn(
            "InstagramParser is deprecated and no longer supported. "
            "Instagram has changed their export format.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)
    
    def parse(self, verbose: bool = False) -> List[Message]:
        """
        This method is deprecated and will return an empty list.
        
        Args:
            verbose: Ignored
            
        Returns:
            Empty list of messages
        """
        raise NotImplementedError(
            "Instagram parser is deprecated and no longer functional. "
            "Please use WhatsApp or Telegram parsers instead."
        )