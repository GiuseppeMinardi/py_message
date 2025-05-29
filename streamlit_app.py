"""
Main Streamlit application for chat message parsing and analysis.
"""

import streamlit as st
from app.styles import CUSTOM_CSS
from app.utils import detect_file_type, parse_file, create_dataframe
from app.visualizations import (
    display_statistics, 
    display_sender_stats, 
    display_time_analysis,
    display_word_stats
)
from app.components import (
    display_message_viewer,
    display_export_options,
    display_sidebar,
    display_landing_page
)


# Page configuration
st.set_page_config(
    page_title="Chat Analytics Studio",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    # Header with gradient
    st.markdown('<h1 class="custom-header">Chat Analytics Studio</h1>', unsafe_allow_html=True)
    st.markdown("Transform your chat exports into beautiful insights 🚀")
    
    # Initialize session state for file processing
    if 'file_processed' not in st.session_state:
        st.session_state.file_processed = False
    
    # Sidebar for file upload
    with st.sidebar:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'json', 'html'],
            help="Upload WhatsApp (.txt), Telegram (.json), or Instagram (.html) export"
        )
        
        display_sidebar(uploaded_file)
    
    # Main content area
    if uploaded_file is not None:
        # Detect file type
        file_content = uploaded_file.read()
        uploaded_file.seek(0)  # Reset file pointer
        
        detected_platform = detect_file_type(uploaded_file.name, file_content)
        
        if detected_platform:
            # Platform badge
            platform_emoji = {"whatsapp": "💚", "telegram": "✈️", "instagram": "📷"}
            st.markdown(f"""
                <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 10px 20px; border-radius: 20px; 
                            display: inline-block; margin: 10px 0;">
                    {platform_emoji.get(detected_platform, "💬")} Detected Platform: <strong>{detected_platform.capitalize()}</strong>
                </div>
            """, unsafe_allow_html=True)
            
            # Parse the file
            messages = parse_file(uploaded_file, detected_platform)
            
            if messages:
                # Show balloons only when file is first processed
                if not st.session_state.file_processed:
                    st.balloons()
                    st.session_state.file_processed = True
                
                # Convert to DataFrame
                df = create_dataframe(messages)
                
                # Create modern tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📊 Overview", 
                    "📅 Time Analysis", 
                    "💬 Messages",
                    "📝 Word Analysis",
                    "💾 Export"
                ])
                
                with tab1:
                    display_statistics(df)
                    display_sender_stats(df)
                
                with tab2:
                    display_time_analysis(df)
                
                with tab3:
                    display_message_viewer(df)
                
                with tab4:
                    display_word_stats(df)
                
                with tab5:
                    display_export_options(df)
            else:
                st.error("❌ No messages were parsed from the file.")
        else:
            st.error("❌ Could not detect the chat platform. Please ensure you're uploading a valid chat export.")
    else:
        # Reset file processed state when no file is uploaded
        st.session_state.file_processed = False
        display_landing_page()


if __name__ == "__main__":
    main()