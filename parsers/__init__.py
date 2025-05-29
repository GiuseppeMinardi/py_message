"""
Chat message parsers for different messaging platforms.
"""

from .base import BaseParser
from .whatsapp import WhatsAppParser
from .telegram import TelegramParser
from .instagram import InstagramParser

__all__ = ['BaseParser', 'WhatsAppParser', 'TelegramParser', 'InstagramParser']