"""
Example usage of the chat parsers.
"""

from parsers.whatsapp import WhatsAppParser
from parsers.telegram import TelegramParser
from models.message import Message
import pandas as pd


def analyze_chat(file_path: str, parser_type: str = "whatsapp"):
    """
    Analyze a chat file and print basic statistics.
    
    Args:
        file_path: Path to the chat file
        parser_type: Type of parser to use ("whatsapp" or "telegram")
    """
    # Select parser
    if parser_type == "whatsapp":
        parser = WhatsAppParser(file_path)
    elif parser_type == "telegram":
        parser = TelegramParser(file_path)
    else:
        raise ValueError(f"Unknown parser type: {parser_type}")
    
    # Parse messages
    print(f"Parsing {parser_type} chat...")
    messages = parser.parse(verbose=True)
    
    if not messages:
        print("No messages found!")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame([msg.to_dict() for msg in messages])
    
    # Print statistics
    print(f"\n📊 Chat Statistics:")
    print(f"Total messages: {len(df):,}")
    print(f"Unique participants: {df['sender'].nunique()}")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print(f"Average message length: {df['text'].str.len().mean():.1f} characters")
    
    # Top participants
    print(f"\n👥 Top 5 Participants:")
    top_senders = df['sender'].value_counts().head(5)
    for sender, count in top_senders.items():
        percentage = (count / len(df)) * 100
        print(f"  {sender}: {count:,} messages ({percentage:.1f}%)")
    
    # Media statistics
    if 'media_type' in df.columns:
        media_messages = df[df['media_type'].notna()]
        if len(media_messages) > 0:
            print(f"\n📎 Media Messages:")
            print(f"Total media: {len(media_messages):,} ({len(media_messages)/len(df)*100:.1f}%)")
            media_types = media_messages['media_type'].value_counts()
            for media_type, count in media_types.items():
                print(f"  {media_type}: {count:,}")


if __name__ == "__main__":
    # Example usage - update with your chat file path
    print("Chat Parser Example Usage")
    print("=" * 50)
    
    # Example for WhatsApp
    # analyze_chat("path/to/whatsapp_chat.txt", "whatsapp")
    
    # Example for Telegram
    # analyze_chat("path/to/telegram_export.json", "telegram")
    
    print("\nTo use this script, uncomment one of the examples above")
    print("and update the file path to your chat export file.")