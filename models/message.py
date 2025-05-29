"""
Message data model for chat messages.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    """
    Represents a single chat message.
    
    Attributes:
        datetime: When the message was sent
        sender: Name of the person who sent the message
        text: The message content
        media_type: Type of media if the message contains media (optional)
    """
    datetime: datetime
    sender: str
    text: str
    media_type: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the message."""
        return f"[{self.datetime}] {self.sender}: {self.text[:50]}..."
    
    def to_dict(self) -> dict:
        """Convert message to dictionary for DataFrame creation."""
        return {
            'datetime': self.datetime,
            'sender': self.sender,
            'text': self.text,
            'media_type': self.media_type
        }