# 💬 Chat Message Parser

A modern Python application for parsing and analyzing chat exports from WhatsApp and Telegram, with a beautiful Streamlit web interface.

## 🚀 Features

- **Multi-Platform Support**: Parse chat exports from WhatsApp (.txt) and Telegram (.json)
- **Interactive Web Interface**: Built with Streamlit for easy use
- **Comprehensive Analytics**:
  - Message statistics and counts
  - Participant analysis
  - Time-based patterns (hourly, daily, weekly)
  - Message distribution charts
- **Search & Filter**: Find specific messages with powerful filtering options
- **Data Export**: Export parsed data as CSV or JSON for further analysis
- **Modern Code**: Type hints, proper error handling, and clean architecture

## 📋 Requirements

- Python 3.9 or higher
- Dependencies listed in `requirements.txt`

## 🛠️ Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd py_message
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Running the Streamlit App

```bash
streamlit run streamlit_app.py
```

This will open the web interface in your browser (usually at <http://localhost:8501>).

### Using the Parsers Programmatically

```python
from parsers.whatsapp import WhatsAppParser
from parsers.telegram import TelegramParser

# Parse WhatsApp chat
whatsapp_parser = WhatsAppParser("whatsapp_chat.txt")
messages = whatsapp_parser.parse(verbose=True)

# Parse Telegram chat
telegram_parser = TelegramParser("telegram_export.json")
messages = telegram_parser.parse(verbose=True)

# Work with messages
for message in messages:
    print(f"{message.datetime} - {message.sender}: {message.text}")
```

## 📤 How to Export Chats

### WhatsApp

1. Open the chat you want to export
2. Tap the menu (⋮) and select "More"
3. Choose "Export chat"
4. Select "Without media" (to keep file size manageable)
5. Save the .txt file

### Telegram

1. Open Telegram Desktop
2. Select the chat you want to export
3. Click the menu (⋮) and choose "Export chat history"
4. Select "JSON" format
5. Uncheck "Media" to reduce file size
6. Click "Export"

## 📁 Project Structure

```
py_message/
├── parsers/              # Chat parsers for different platforms
│   ├── __init__.py
│   ├── base.py          # Abstract base parser
│   ├── whatsapp.py      # WhatsApp parser
│   ├── telegram.py      # Telegram parser
│   └── instagram.py     # Instagram parser (deprecated)
├── models/              # Data models
│   ├── __init__.py
│   └── message.py       # Message model
├── app/                 # Streamlit app components
│   ├── __init__.py
│   ├── styles.py        # Custom CSS styles
│   ├── utils.py         # Utility functions
│   ├── visualizations.py # Chart components
│   └── components.py    # UI components
├── streamlit_app.py     # Main Streamlit application
├── example_usage.py     # Example script
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

## 🏗️ Architecture

The project follows a clean architecture with:

- **Base Parser Class**: Abstract base class defining the parser interface
- **Platform-Specific Parsers**: Implementations for each chat platform
- **Message Model**: Standardized data model for all messages
- **Streamlit App**: Interactive web interface for parsing and analysis

## 🔧 Development

### Adding a New Parser

1. Create a new parser class inheriting from `BaseParser`
2. Implement the `parse()` method
3. Add the parser to `parsers/__init__.py`
4. Update the app to support the new platform

### Code Style

- Type hints for all functions
- Docstrings for classes and methods
- Error handling with proper logging
- Follow PEP 8 guidelines

## ⚠️ Notes

- The Instagram parser is deprecated due to changes in Instagram's export format
- Large chat files may take time to parse - progress bars are shown during parsing
- Media files are not included in the parsing (only media type indicators)

## 📝 License

This project is open source. Feel free to use and modify as needed.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
