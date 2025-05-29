"""
Telegram chat parser implementation.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from tqdm import tqdm

from models.message import Message
from .base import BaseParser


logger = logging.getLogger(__name__)


class TelegramParser(BaseParser):
    """
    Parser for Telegram chat exports in JSON format.
    
    Handles the standard Telegram JSON export format.
    """
    
    def parse(self, verbose: bool = False) -> List[Message]:
        """
        Parse Telegram chat file in JSON format.
        
        Args:
            verbose: Whether to show progress bar during parsing
            
        Returns:
            List of parsed Message objects
        """
        messages = []
        
        try:
            # Get file content and parse JSON
            content = self._get_file_content()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            data = json.loads(content)
            
            # Extract messages from JSON structure
            raw_messages = data.get('messages', [])
            
            # Use tqdm for progress if verbose
            iterator = tqdm(raw_messages, desc="Parsing Telegram messages") if verbose else raw_messages
            
            for raw_msg in iterator:
                message = self._parse_message(raw_msg)
                if message:
                    messages.append(message)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid Telegram JSON format: {e}")
        except Exception as e:
            logger.error(f"Error parsing Telegram file: {e}")
            raise
        
        # Validate messages before returning
        return self.validate_messages(messages)
    
    def _parse_message(self, raw_msg: Dict[str, Any]) -> Optional[Message]:
        """
        Parse a single message from Telegram JSON format.
        
        Args:
            raw_msg: Raw message dictionary from JSON
            
        Returns:
            Message object if successful, None otherwise
        """
        try:
            # Extract basic fields
            date_str = raw_msg.get('date', '')
            sender = raw_msg.get('from', 'Unknown')
            
            # Parse datetime
            parsed_datetime = self._parse_datetime(date_str)
            
            # Extract text content
            text = self._extract_text(raw_msg)
            
            # Detect media type
            media_type = self._detect_media_type(raw_msg)
            
            # If no text and no media, skip this message
            if not text and not media_type:
                return None
            
            return Message(
                datetime=parsed_datetime,
                sender=sender,
                text=text,
                media_type=media_type
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse message: {e}")
            return None
    
    def _parse_datetime(self, date_str: str) -> datetime:
        """
        Parse datetime from Telegram format.
        
        Args:
            date_str: Date string from Telegram JSON
            
        Returns:
            Parsed datetime object
        """
        if not date_str:
            return datetime.now()
        
        # Telegram uses ISO format: "2023-01-15T10:30:45"
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            # Try alternative format without timezone
            try:
                return datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                logger.warning(f"Could not parse datetime: {date_str}")
                return datetime.now()
    
    def _extract_text(self, raw_msg: Dict[str, Any]) -> str:
        """
        Extract text content from message.
        
        Args:
            raw_msg: Raw message dictionary
            
        Returns:
            Extracted text content
        """
        # Handle different text formats in Telegram export
        text = raw_msg.get('text', '')
        
        # Text might be a string or a list of text entities
        if isinstance(text, list):
            # Join text entities
            text_parts = []
            for entity in text:
                if isinstance(entity, dict):
                    text_parts.append(entity.get('text', ''))
                elif isinstance(entity, str):
                    text_parts.append(entity)
            text = ''.join(text_parts)
        elif not isinstance(text, str):
            text = str(text)
        
        return text.strip()
    
    def _detect_media_type(self, raw_msg: Dict[str, Any]) -> Optional[str]:
        """
        Detect media type from message.
        
        Args:
            raw_msg: Raw message dictionary
            
        Returns:
            Media type if detected, None otherwise
        """
        # Check for media_type field
        if 'media_type' in raw_msg:
            return raw_msg['media_type']
        
        # Check for file field
        if 'file' in raw_msg:
            file_name = raw_msg.get('file', '')
            if isinstance(file_name, str):
                return self._get_media_type_from_filename(file_name)
        
        # Check for specific media fields
        media_fields = {
            'photo': 'photo',
            'video': 'video',
            'voice_message': 'voice',
            'video_message': 'video_message',
            'sticker': 'sticker',
            'animation': 'animation',
            'document': 'document',
            'audio': 'audio',
        }
        
        for field, media_type in media_fields.items():
            if field in raw_msg and raw_msg[field]:
                return media_type
        
        return None
    
    def _get_media_type_from_filename(self, filename: str) -> str:
        """
        Determine media type from filename extension.
        
        Args:
            filename: File name
            
        Returns:
            Media type based on extension
        """
        filename_lower = filename.lower()
        
        if any(filename_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            return 'image'
        elif any(filename_lower.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.webm']):
            return 'video'
        elif any(filename_lower.endswith(ext) for ext in ['.mp3', '.ogg', '.wav', '.m4a']):
            return 'audio'
        elif any(filename_lower.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.txt']):
            return 'document'
        else:
            return 'file'