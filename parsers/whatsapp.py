"""
WhatsApp chat parser implementation.
"""

import re
from datetime import datetime
from typing import List, Optional, Tuple
import logging

from tqdm import tqdm

from models.message import Message
from .base import BaseParser


logger = logging.getLogger(__name__)


class WhatsAppParser(BaseParser):
    """
    Parser for WhatsApp chat exports.
    
    Handles the standard WhatsApp chat export format:
    DD/MM/YY, HH:MM - Sender: Message text
    """
    
    # Regex pattern for WhatsApp message format
    MESSAGE_PATTERN = re.compile(
        r'^(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}) - ([^:]+): (.*)$'
    )
    
    # Alternative pattern for messages with different date format
    ALT_MESSAGE_PATTERN = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}(?:\s*[AP]M)?) - ([^:]+): (.*)$'
    )
    
    def parse(self, verbose: bool = False) -> List[Message]:
        """
        Parse WhatsApp chat file.
        
        Args:
            verbose: Whether to show progress bar during parsing
            
        Returns:
            List of parsed Message objects
        """
        messages = []
        lines = self._get_file_lines()
        
        # Use tqdm for progress if verbose
        iterator = tqdm(lines, desc="Parsing WhatsApp messages") if verbose else lines
        
        current_message = None
        
        for line in iterator:
            # Try to parse as a new message
            parsed = self._parse_message_line(line)
            
            if parsed:
                # If we have a current message, add it to the list
                if current_message:
                    messages.append(current_message)
                
                # Start a new message
                date_str, time_str, sender, text = parsed
                current_message = self._create_message(date_str, time_str, sender, text)
            else:
                # This is a continuation of the previous message
                if current_message:
                    current_message.text += f"\n{line}"
        
        # Don't forget the last message
        if current_message:
            messages.append(current_message)
        
        # Validate messages before returning
        return self.validate_messages(messages)
    
    def _parse_message_line(self, line: str) -> Optional[Tuple[str, str, str, str]]:
        """
        Try to parse a line as a message header.
        
        Args:
            line: Line to parse
            
        Returns:
            Tuple of (date, time, sender, text) if successful, None otherwise
        """
        line = line.strip()
        if not line:
            return None
        
        # Try standard pattern first
        match = self.MESSAGE_PATTERN.match(line)
        if match:
            return match.groups()
        
        # Try alternative pattern
        match = self.ALT_MESSAGE_PATTERN.match(line)
        if match:
            return match.groups()
        
        return None
    
    def _create_message(self, date_str: str, time_str: str, sender: str, text: str) -> Message:
        """
        Create a Message object from parsed components.
        
        Args:
            date_str: Date string (DD/MM/YY)
            time_str: Time string (HH:MM)
            sender: Sender name
            text: Message text
            
        Returns:
            Message object
        """
        # Parse datetime
        datetime_str = f"{date_str} {time_str}"
        
        # Try different datetime formats
        datetime_formats = [
            "%d/%m/%y %H:%M",
            "%d/%m/%Y %H:%M",
            "%m/%d/%y %H:%M",
            "%m/%d/%Y %H:%M",
            "%d/%m/%y %I:%M %p",
            "%d/%m/%Y %I:%M %p",
        ]
        
        parsed_datetime = None
        for fmt in datetime_formats:
            try:
                parsed_datetime = datetime.strptime(datetime_str.strip(), fmt)
                break
            except ValueError:
                continue
        
        if not parsed_datetime:
            logger.warning(f"Could not parse datetime: {datetime_str}")
            parsed_datetime = datetime.now()  # Fallback to current time
        
        # Clean up sender name
        sender = sender.strip()
        
        # Check for media messages
        media_type = self._detect_media_type(text)
        
        return Message(
            datetime=parsed_datetime,
            sender=sender,
            text=text.strip(),
            media_type=media_type
        )
    
    def _detect_media_type(self, text: str) -> Optional[str]:
        """
        Detect if the message contains media.
        
        Args:
            text: Message text
            
        Returns:
            Media type if detected, None otherwise
        """
        media_indicators = {
            '<Media omitted>': 'media',
            'image omitted': 'image',
            'video omitted': 'video',
            'audio omitted': 'audio',
            'document omitted': 'document',
            'sticker omitted': 'sticker',
            'GIF omitted': 'gif',
            '.jpg': 'image',
            '.png': 'image',
            '.mp4': 'video',
            '.pdf': 'document',
        }
        
        text_lower = text.lower()
        for indicator, media_type in media_indicators.items():
            if indicator.lower() in text_lower:
                return media_type
        
        return None