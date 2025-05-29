"""
Custom CSS styles for the Streamlit app.
"""

CUSTOM_CSS = """
<style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Custom metric cards */
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    div[data-testid="metric-container"]:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    /* Styled headers */
    .custom-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .section-header {
        color: #1f2937;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }
    
    /* Upload area styling */
    .uploadfile {
        background-color: #f8fafc;
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8fafc;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
        border-color: #667eea;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #667eea;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #764ba2;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Dataframe styling */
    .dataframe {
        border: none !important;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Success/Error message styling */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    /* Fix selectbox text color */
    .stSelectbox > div > div {
        color: #1f2937 !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background-color: white;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background-color: white;
        color: #1f2937 !important;
    }
    
    /* Dropdown menu styling */
    [data-baseweb="popover"] {
        background-color: white !important;
    }
    
    [data-baseweb="popover"] li {
        color: #1f2937 !important;
    }
    
    [data-baseweb="popover"] li:hover {
        background-color: #f0f2f6 !important;
    }
</style>
"""