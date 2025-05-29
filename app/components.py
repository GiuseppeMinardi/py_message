"""
UI components for the Streamlit app.
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime


def display_message_viewer(df: pd.DataFrame):
    """
    Display message viewer with search and filters.
    
    Args:
        df: DataFrame with message data
    """
    st.markdown('<h2 class="section-header">💬 Message Explorer</h2>', unsafe_allow_html=True)
    
    # Create filter columns
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        # Sender filter with emoji
        senders = ['All Participants'] + sorted(df['sender'].unique().tolist())
        selected_sender = st.selectbox("👤 Filter by Sender", senders)
    
    with col2:
        # Date range filter
        if 'datetime' in df.columns and len(df) > 0:
            date_range = st.date_input(
                "📅 Date Range",
                value=(df['datetime'].min().date(), df['datetime'].max().date()),
                min_value=df['datetime'].min().date(),
                max_value=df['datetime'].max().date()
            )
        else:
            date_range = None
    
    with col3:
        # Search box with placeholder
        search_term = st.text_input("🔍 Search Messages", placeholder="Type to search...")
    
    with col4:
        # Media filter
        show_media_only = st.checkbox("📎 Media Only", value=False)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_sender != 'All Participants':
        filtered_df = filtered_df[filtered_df['sender'] == selected_sender]
    
    if date_range and len(date_range) == 2 and 'datetime' in filtered_df.columns:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['datetime'].dt.date >= start_date) & 
            (filtered_df['datetime'].dt.date <= end_date)
        ]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['text'].str.contains(search_term, case=False, na=False)
        ]
    
    if show_media_only:
        filtered_df = filtered_df[filtered_df['media_type'].notna()]
    
    # Display results count with styling
    st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 8px; margin: 10px 0;">
            <strong>📊 Results:</strong> Showing {len(filtered_df):,} of {len(df):,} messages
        </div>
    """, unsafe_allow_html=True)
    
    # Format and display messages
    if len(filtered_df) > 0:
        display_df = filtered_df.copy()
        if 'datetime' in display_df.columns:
            display_df['Time'] = display_df['datetime'].dt.strftime('%Y-%m-%d %H:%M')
        
        # Rename columns for display
        display_columns = {
            'Time': 'Time',
            'sender': 'Sender',
            'text': 'Message',
            'media_type': 'Media'
        }
        
        display_df = display_df[[col for col in display_columns.keys() if col in display_df.columns]]
        display_df = display_df.rename(columns=display_columns)
        
        # Display with custom styling
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )
    else:
        st.info("No messages match your filters.")


def display_export_options(df: pd.DataFrame):
    """
    Display export options for the data.
    
    Args:
        df: DataFrame with message data
    """
    st.markdown('<h2 class="section-header">💾 Export Your Data</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV export
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON export
        json_str = df.to_json(orient='records', date_format='iso')
        st.download_button(
            label="📋 Download JSON",
            data=json_str,
            file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        # Excel export (requires openpyxl)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Messages', index=False)
        
        st.download_button(
            label="📊 Download Excel",
            data=buffer.getvalue(),
            file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


def display_sidebar(uploaded_file):
    """
    Display sidebar content.
    
    Args:
        uploaded_file: The uploaded file object
    """
    st.markdown("### 📤 Upload Chat Export")
    
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Show file info
        file_size = len(uploaded_file.getvalue()) / 1024 / 1024  # MB
        st.info(f"📁 Size: {file_size:.2f} MB")
    
    # Instructions expander
    with st.expander("📖 How to Export Chats"):
        st.markdown("""
        **WhatsApp:**
        1. Open the chat
        2. Tap ⋮ → More → Export chat
        3. Choose "Without media"
        4. Save the .txt file
        
        **Telegram:**
        1. Open Telegram Desktop
        2. Select the chat
        3. Click ⋮ → Export chat history
        4. Choose JSON format
        5. Export without media
        """)


def display_landing_page():
    """
    Display landing page when no file is uploaded.
    """
    st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h2>Welcome to Chat Analytics Studio! 👋</h2>
            <p style="font-size: 1.2rem; color: #666;">
                Upload your chat export file to get started with beautiful analytics and insights.
            </p>
            <p style="margin-top: 30px;">
                <strong>Supported Platforms:</strong><br>
                💚 WhatsApp • ✈️ Telegram
            </p>
        </div>
    """, unsafe_allow_html=True)