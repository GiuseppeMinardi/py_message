"""
Base parser class for all chat parsers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union, IO
import logging

from models.message import Message


logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """
    Abstract base class for chat message parsers.
    
    All platform-specific parsers should inherit from this class
    and implement the parse method.
    """
    
    def __init__(self, file_path: Union[str, Path, IO]):
        """
        Initialize the parser with a file path or file object.
        
        Args:
            file_path: Path to the chat file or file-like object
        """
        if hasattr(file_path, 'read'):
            # It's a file-like object (e.g., from Streamlit)
            self.file_obj = file_path
            self.file_path = None
        else:
            # It's a path
            self.file_path = Path(file_path) if isinstance(file_path, str) else file_path
            self.file_obj = None
            
            if not self.file_path.exists():
                raise FileNotFoundError(f"File not found: {self.file_path}")
    
    @abstractmethod
    def parse(self, verbose: bool = False) -> List[Message]:
        """
        Parse the chat file and return a list of Message objects.
        
        Args:
            verbose: Whether to show progress during parsing
            
        Returns:
            List of Message objects
        """
        pass
    
    def _get_file_content(self) -> str:
        """Get file content from either file path or file object."""
        if self.file_obj:
            # Reset file pointer to beginning
            self.file_obj.seek(0)
            return self.file_obj.read()
        else:
            return self.file_path.read_text(encoding='utf-8')
    
    def _get_file_lines(self) -> List[str]:
        """Get file lines from either file path or file object."""
        content = self._get_file_content()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        return content.splitlines()
    
    def validate_messages(self, messages: List[Message]) -> List[Message]:
        """
        Validate parsed messages and filter out invalid ones.
        
        Args:
            messages: List of parsed messages
            
        Returns:
            List of valid messages
        """
        valid_messages = []
        for msg in messages:
            if self._is_valid_message(msg):
                valid_messages.append(msg)
            else:
                logger.warning(f"Invalid message filtered out: {msg}")
        
        return valid_messages
    
    def _is_valid_message(self, message: Message) -> bool:
        """
        Check if a message is valid.
        
        Args:
            message: Message to validate
            
        Returns:
            True if message is valid, False otherwise
        """
        # Basic validation - can be overridden in subclasses
        return (
            message.datetime is not None and
            message.sender and
            (message.text or message.media_type)
        )