import requests
import streamlit as st
from datetime import datetime, timedelta
import os
from config import NEWS_API_KEY

def get_news_client():
    """Check if News API key is configured"""
    api_key = os.environ.get("NEWS_API_KEY")
    if not api_key or api_key == "YOUR_NEWS_API_KEY":
        st.warning("News API key not configured. News features will be unavailable.", icon="⚠️")
        return None
    return api_key

def extract_keywords(text, max_keywords=5):
    """Extract important keywords from text for news search"""
    # Simple implementation: split by spaces and get most common words
    # In a real app, you'd use NLP techniques for better keyword extraction
    if not text:
        return []
        
    # Remove common words (simple stopwords)
    stopwords = ["the", "a", "an", "and", "in", "on", "at", "to", "for", "of", "with", "by", "as", "is", "are", "was", "were"]
    words = text.lower().split()
    words = [word for word in words if word not in stopwords and len(word) > 3]
    
    # Count word frequency
    word_freq = {}
    for word in words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    # Return top keywords
    return [word for word, _ in sorted_words[:max_keywords]]

def fetch_related_news(summary, api_key, max_results=5):
    """Fetch news related to Meetings and News summary content"""
    if not api_key or not summary:
        return []
    
    try:
        # Extract keywords from summary
        keywords = extract_keywords(summary)
        query = " OR ".join(keywords)
        
        if not query:
            # Default to technology news if no keywords extracted
            return fetch_latest_news(api_key, category="technology", max_results=max_results)
        
        # Calculate date one week ago for freshness
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Make request to News API
        url = f"https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": api_key,
            "language": "en",
            "sortBy": "relevancy",
            "from": week_ago,
            "pageSize": max_results
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            # Format the news articles
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    "title": article.get('title', 'No title'),
                    "source": article.get('source', {}).get('name', 'Unknown source'),
                    "url": article.get('url', '#'),
                    "publishedAt": article.get('publishedAt', ''),
                    "description": article.get('description', 'No description available'),
                    "urlToImage": article.get('urlToImage')  # Add image URL
                })
                
            return formatted_articles
            
        else:
            st.error(f"Error fetching news: {response.status_code}")
            return []
            
    except Exception as e:
        st.error(f"Error fetching related news: {e}")
        return []

def fetch_latest_news(api_key, category="general", max_results=5):
    """Fetch the latest news in a specific category"""
    if not api_key:
        return []
    
    try:
        # Make request to News API
        url = f"https://newsapi.org/v2/top-headlines"
        params = {
            "category": category,
            "apiKey": api_key,
            "language": "en",
            "pageSize": max_results
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            # Format the news articles
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    "title": article.get('title', 'No title'),
                    "source": article.get('source', {}).get('name', 'Unknown source'),
                    "url": article.get('url', '#'),
                    "publishedAt": article.get('publishedAt', ''),
                    "description": article.get('description', 'No description available'),
                    "urlToImage": article.get('urlToImage')  # Add image URL
                })
                
            return formatted_articles
            
        else:
            st.error(f"Error fetching news: {response.status_code}")
            return []
            
    except Exception as e:
        st.error(f"Error fetching latest news: {e}")
        return []
    
def render_news_column(articles):
    """Render news articles in a Streamlit container"""
    if not articles:
        st.info("No news articles available")
        return
    
    # Add custom CSS to ensure text visibility
    st.markdown("""
    <style>
        .news-title { color: #1E1E1E; font-weight: bold; font-size: 1.2rem; margin-bottom: 0.5rem; }
        .news-source { color: #5A5A5A; font-size: 0.8rem; }
        .news-description { color: #333333; margin: 0.7rem 0; }
        .news-link { color: #1E88E5; text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a grid layout for news articles
    cols = st.columns(min(3, len(articles)))
    
    for idx, article in enumerate(articles):
        col_idx = idx % len(cols)
        with cols[col_idx]:
            with st.container():
                # Use HTML/CSS to control text colors
                st.markdown(f"""
                <div class="news-title">{article['title']}</div>
                <div class="news-source">{article['source']} • {format_date(article['publishedAt'])}</div>
                <div class="news-description">{article['description']}</div>
                <a href="{article['url']}" target="_blank" class="news-link">Read more</a>
                """, unsafe_allow_html=True)
                st.divider()
                
    # Display any remaining articles in a list format if more than fits in the grid
    if len(articles) > 3:
        st.markdown("### More Related Articles")
        for idx, article in enumerate(articles[3:], 3):
            with st.expander(f"{article['title']} ({article['source']})"):
                # Use HTML/CSS to control text colors in expanders too
                st.markdown(f"""
                <div class="news-source">{format_date(article['publishedAt'])}</div>
                <div class="news-description">{article['description']}</div>
                <a href="{article['url']}" target="_blank" class="news-link">Read more</a>
                """, unsafe_allow_html=True)
                               
def format_date(date_str):
    """Format date string to a more readable format"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%B %d, %Y")
    except:
        return date_str