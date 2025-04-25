import streamlit as st

def apply_custom_css():
    """Apply custom CSS to override Streamlit defaults and create a professional look"""
    custom_css = """
    <style>
        /* Main layout styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
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
            color: #1E3A8A;
        }
        
        /* Card styling for containers */
        .stCard {
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1rem;
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
            border: 1px solid #E2E8F0;
            border-radius: 0.25rem;
            padding: 0.5rem;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            padding-top: 2rem;
        }
        
        /* Footer styling */
        footer {
            border-top: 1px solid #E2E8F0;
            padding-top: 1rem;
            text-align: center;
            font-size: 0.8rem;
            color: #718096;
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
            background-color: #F0F2F6;
            padding: 0.5rem;
            text-align: center;
            font-size: 0.8rem;
            border-top: 1px solid #E2E8F0;
            z-index: 999;
        }
        
        /* News card styling */
        .news-card {
            border: 1px solid #E2E8F0;
            border-radius: 0.375rem;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .news-source {
            color: #718096;
            font-size: 0.85rem;
        }
        
        /* Summary container */
        .summary-container {
            background-color: #6C3BAA;
            border-left: 4px solid #4B6BF5;
            padding: 1.25rem;
            border-radius: 0.25rem;
        }
        
        /* Sentiment analysis container */
        .sentiment-container {
            background-color: #6C3BAA;
            border-left: 4px solid #0EA5E9;
            padding: 1.25rem;
            border-radius: 0.25rem;
        }
        
        /* Pro features badge */
        .pro-badge {
            background-color: #FEF3C7;
            color: #92400E;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-weight: 500;
            font-size: 0.75rem;
            margin-left: 0.5rem;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_logo():
    """Render a professional logo and branding"""
    logo_html = """
    <div class="logo-container">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M6 2L18 12L6 22L6 2Z" fill="#4B6BF5" stroke="#1E3A8A" stroke-width="2"/>
        </svg>
        <div class="logo-text">Poke Summarizer</div>
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)

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