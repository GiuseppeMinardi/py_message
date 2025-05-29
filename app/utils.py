"""
Utility functions for the Streamlit app.
"""

import pandas as pd
from typing import List, Optional
from models.message import Message
from parsers.whatsapp import WhatsAppParser
from parsers.telegram import TelegramParser
from parsers.instagram import InstagramParser
import streamlit as st


def detect_file_type(file_name: str, file_content: bytes) -> Optional[str]:
    """
    Detect the chat platform based on file name and content.
    
    Args:
        file_name: Name of the uploaded file
        file_content: File content as bytes
        
    Returns:
        Detected platform ('whatsapp', 'telegram', 'instagram') or None
    """
    # Check by file extension
    if file_name.endswith('.json'):
        return 'telegram'
    elif file_name.endswith('.html'):
        return 'instagram'
    elif file_name.endswith('.txt'):
        # Check content for WhatsApp patterns
        try:
            content_str = file_content.decode('utf-8')
            if ' - ' in content_str[:200] and ': ' in content_str[:200]:
                return 'whatsapp'
        except:
            pass
    
    return None


def parse_file(uploaded_file, platform: str) -> List[Message]:
    """
    Parse the uploaded file based on the platform.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        platform: Chat platform ('whatsapp', 'telegram', 'instagram')
        
    Returns:
        List of parsed messages
    """
    try:
        if platform == 'whatsapp':
            parser = WhatsAppParser(uploaded_file)
        elif platform == 'telegram':
            parser = TelegramParser(uploaded_file)
        elif platform == 'instagram':
            parser = InstagramParser(uploaded_file)
        else:
            st.error(f"Unknown platform: {platform}")
            return []
        
        with st.spinner("🔄 Parsing messages..."):
            messages = parser.parse(verbose=True)
        
        return messages
    
    except Exception as e:
        st.error(f"❌ Error parsing file: {str(e)}")
        return []


def create_dataframe(messages: List[Message]) -> pd.DataFrame:
    """
    Convert messages to pandas DataFrame.
    
    Args:
        messages: List of Message objects
        
    Returns:
        DataFrame with message data
    """
    data = [msg.to_dict() for msg in messages]
    df = pd.DataFrame(data)
    
    # Ensure datetime column is datetime type
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
    
    return df