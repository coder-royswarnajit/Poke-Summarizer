import streamlit as st

def apply_custom_css():
    """Apply custom CSS to override Streamlit defaults and create a professional look"""
    
    is_dark_mode = st.session_state.get('dark_mode', False)
    
    base_css = """
    <style>
        /* Main layout styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Logo and branding */
        .logo-container {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .logo-text {
            font-size: 1.5rem;
            font-weight: bold;
            margin-left: 0.5rem;
        }
        
        /* Gastly Logo specific styling */
        .gastly-logo {
            width: 64px; 
            height: 64px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 0.25rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* File uploader styling */
        .uploadedFile {
            border-radius: 0.25rem;
            padding: 0.5rem;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            padding-top: 2rem;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Custom footer */
        .custom-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 0.5rem;
            text-align: center;
            font-size: 0.8rem;
            border-top: 1px solid;
            z-index: 999;
        }
        
        /* Dark mode toggle button */
        .dark-mode-toggle {
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            transition: all 0.2s ease;
        }
        
        .dark-mode-toggle:hover {
            opacity: 0.9;
        }
        
        .toggle-icon {
            margin-right: 0.5rem;
        }
    """
    
    # Light mode specific CSS
    light_mode_css = """
        /* Header styling */
        h1, h2, h3, h4 {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 600;
            color: #1E3A8A;
        }
        
        h1 {
            border-bottom: 2px solid #4B6BF5;
            padding-bottom: 0.5rem;
        }
        
        .logo-text {
            color: #1E3A8A;
        }
        
        /* Card styling for containers */
        .stCard {
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1rem;
            background-color: #FFFFFF;
        }
        
        /* File uploader styling */
        .uploadedFile {
            border: 1px solid #E2E8F0;
        }
        
        /* Footer styling */
        footer {
            border-top: 1px solid #E2E8F0;
            padding-top: 1rem;
            text-align: center;
            font-size: 0.8rem;
            color: #718096;
        }
        
        /* Custom footer */
        .custom-footer {
            background-color: #F0F2F6;
            border-top-color: #E2E8F0;
            color: #718096;
        }
        
        /* News card styling */
        .news-card {
            border: 1px solid #E2E8F0;
            border-radius: 0.375rem;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: #003153;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .news-source {
            color: #718096;
            font-size: 0.85rem;
        }
        
        /* Summary container */
        .summary-container {
            background-color: #F0F7FF;
            border-left: 4px solid #4B6BF5;
            padding: 1.25rem;
            border-radius: 0.25rem;
            color: #2D3748;
        }
        
        /* Sentiment analysis container */
        .sentiment-container {
            background-color: #F0FDFA;
            border-left: 4px solid #0EA5E9;
            padding: 1.25rem;
            border-radius: 0.25rem;
            color: #2D3748;
        }
        
        /* Pro features badge */
        .pro-badge {
            background-color: #F0F7FF;
            color: #2D3748;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-weight: 500;
            font-size: 0.75rem;
            margin-left: 0.5rem;
        }
        
        /* Dark mode toggle button */
        .dark-mode-toggle {
            background-color: #E2E8F0;
            color: #4A5568;
        }
    """
    
    # Dark mode specific CSS
    dark_mode_css = """
        /* Dark mode background and text colors */
        body {
            background-color: #1A202C;
            color: #E2E8F0;
        }
        
        .stApp {
            background-color: #1A202C;
        }
        
        /* Header styling for dark mode */
        h1, h2, h3, h4 {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 600;
            color: #90CDF4;
        }
        
        h1 {
            border-bottom: 2px solid #4B6BF5;
            padding-bottom: 0.5rem;
        }
        
        .logo-text {
            color: #90CDF4;
        }
        
        /* Card styling for containers in dark mode */
        .stCard {
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            padding: 1.5rem;
            margin-bottom: 1rem;
            background-color: #2D3748;
        }
        
        /* File uploader styling */
        .uploadedFile {
            border: 1px solid #4A5568;
        }
        
        /* Footer styling */
        footer {
            border-top: 1px solid #4A5568;
            padding-top: 1rem;
            text-align: center;
            font-size: 0.8rem;
            color: #A0AEC0;
        }
        
        /* Custom footer */
        .custom-footer {
            background-color: #2D3748;
            border-top-color: #4A5568;
            color: #A0AEC0;
        }
        
        /* News card styling */
        .news-card {
            border: 1px solid #4A5568;
            border-radius: 0.375rem;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: #2D3748;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .news-source {
            color: #A0AEC0;
            font-size: 0.85rem;
        }
        
        /* Summary container */
        .summary-container {
            background-color: #2A4365;
            border-left: 4px solid #4B6BF5;
            padding: 1.25rem;
            border-radius: 0.25rem;
            color: #E2E8F0;
        }
        
        /* Sentiment analysis container */
        .sentiment-container {
            background-color: #234E52;
            border-left: 4px solid #0EA5E9;
            padding: 1.25rem;
            border-radius: 0.25rem;
            color: #E2E8F0;
        }
        
        /* Pro features badge */
        .pro-badge {
            background-color: #744210;
            color: #F6E05E;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-weight: 500;
            font-size: 0.75rem;
            margin-left: 0.5rem;
        }
        
        /* Sidebar background */
        [data-testid="stSidebar"] {
            background-color: #2D3748;
        }
        
        /* Dark mode toggle button */
        .dark-mode-toggle {
            background-color: #4A5568;
            color: #E2E8F0;
        }
        
        /* Streamlit inputs in dark mode */
        [data-baseweb="select"] {
            background-color: #4A5568;
            color: #E2E8F0;
        }
        
        /* Streamlit metrics in dark mode */
        [data-testid="stMetricValue"] {
            color: #E2E8F0;
        }
        
        /* Streamlit expanders in dark mode */
        .streamlit-expanderHeader {
            background-color: #2D3748;
            color: #E2E8F0;
        }
        
        /* Links in dark mode */
        a {
            color: #90CDF4;
        }
        
        /* Streamlit buttons in dark mode */
        .stButton > button {
            background-color: #4A5568;
            color: #E2E8F0;
        }
        
        .stButton > button:hover {
            background-color: #2D3748;
        }
    """
    
    # Combine base CSS with either light or dark mode CSS based on session state
    if is_dark_mode:
        custom_css = base_css + dark_mode_css
    else:
        custom_css = base_css + light_mode_css
    
    st.markdown(custom_css, unsafe_allow_html=True)

def toggle_dark_mode():
    """Toggle dark mode state"""
    st.session_state.dark_mode = not st.session_state.get('dark_mode', False)
    
def render_dark_mode_toggle():
    """Render a toggle button for dark mode"""
    is_dark_mode = st.session_state.get('dark_mode', False)
    
    # Use a more accessible toggle design with icons
    if is_dark_mode:
        toggle_html = """
        <div class="dark-mode-toggle" onclick="javascript:document.querySelector('#dark_mode_toggle_button').click();">
            <span class="toggle-icon">🌙</span>
            <span>Light Mode</span>
        </div>
        """
    else:
        toggle_html = """
        <div class="dark-mode-toggle" onclick="javascript:document.querySelector('#dark_mode_toggle_button').click();">
            <span class="toggle-icon">☀️</span>
            <span>Dark Mode</span>
        </div>
        """
    
    st.markdown(toggle_html, unsafe_allow_html=True)
    
    # Hidden button that actually triggers the callback
    st.button("Toggle Theme", key="dark_mode_toggle_button", on_click=toggle_dark_mode, help="Switch between light and dark mode")

def render_logo():
    """Render the Gastly Pokemon logo and app name"""
    # Use base64 encoding to include the Gastly image directly in the HTML
    # This avoids relying on local file paths which won't work in deployed apps
    gastly_logo_html = """
    <div class="logo-container">
        <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/92.png" 
             alt="Gastly Logo" 
             class="gastly-logo">
        <div class="logo-text">Poke Summarizer</div>
    </div>
    """
    st.markdown(gastly_logo_html, unsafe_allow_html=True)
    
def render_card(content, key=None):
    """Render content in a card-like container"""
    st.markdown(f"""
    <div class="stCard" id="{key or ''}">
        {content}
    </div>
    """, unsafe_allow_html=True)

def render_custom_footer():
    """Render a custom professional footer"""
    footer_html = """
    <div class="custom-footer">
        Poke Summarizer © 2025 | AI-powered Meeting Transcription and Summarization Tool
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def render_summary_box(summary):
    """Render a professional-looking summary box"""
    st.markdown(f"""
    <div class="summary-container">
        {summary}
    </div>
    """, unsafe_allow_html=True)

def render_sentiment_box(sentiment, sentiment_type="Standard"):
    """Render a professional-looking sentiment analysis box"""
    st.markdown(f"""
    <div class="sentiment-container">
        <strong>{sentiment_type} Sentiment Analysis</strong><br><br>
        {sentiment}
    </div>
    """, unsafe_allow_html=True)

def render_news_card(article):
    """Render a single news article in a professional card"""
    published_date = article.get('publishedAt', '')
    if published_date:
        try:
            from datetime import datetime
            dt = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%SZ")
            formatted_date = dt.strftime("%B %d, %Y")
        except:
            formatted_date = published_date
    else:
        formatted_date = ""
    
    # Add image rendering with fallback to placeholder
    image_url = article.get('urlToImage')
    if image_url:
        image_html = f'<img src="{image_url}" alt="{article["title"]}" style="width:100%; height:180px; object-fit:cover; border-radius:0.25rem; margin-bottom:0.75rem;">'
    else:
        # Use placeholder if no image available
        image_html = '<img src="/api/placeholder/400/180" alt="placeholder" style="width:100%; height:180px; object-fit:cover; border-radius:0.25rem; margin-bottom:0.75rem;">'
        
    return f"""
    <div class="news-card">
        {image_html}
        <h4>{article['title']}</h4>
        <p class="news-source">{article['source']} • {formatted_date}</p>
        <p>{article["description"]}</p>
        <a href="{article['url']}" target="_blank">Read more</a>
    </div>
    """
def render_pro_feature_banner(message="Upgrade to Pro for this feature"):
    """Render a professional-looking banner for Pro features"""
    st.markdown(f"""
    <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 0.375rem; padding: 1rem; display: flex; align-items: center; margin-bottom: 1rem;">
        <div style="margin-right: 1rem;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M13 10V3L4 14H11V21L20 10H13Z" fill="#3B82F6" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div>
            <strong>Pro Feature</strong><br>
            <span>{message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
