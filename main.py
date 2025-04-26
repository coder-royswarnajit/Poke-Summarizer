import streamlit as st
import os
import hashlib
from config import LANGUAGES, GROQ_API_KEY  # Import constants
from user_auth import render_auth_ui, render_user_profile
from datetime import datetime
from external_apis import get_groq_client, MonadBlockchainClient
from processing import extract_text_from_file, preprocess_audio
from pdf_utils import create_summary_pdf, get_pdf_download_link
from news_api import get_news_client, fetch_related_news, fetch_latest_news
from transcription_and_summarization import (
    transcribe_with_transformers_whisper,
    translate_to_english,
    translate_to_language,
    detect_language,
    improve_transcript_quality,
    summarize_text_groq,
    analyze_sentiment,
)  # Import all functions

# Import our custom styling
from custom import (
    apply_custom_css, 
    render_logo, 
    render_card, 
    render_custom_footer,
    render_summary_box,
    render_sentiment_box,
    render_news_card,
    render_pro_feature_banner,
    render_dark_mode_toggle,
)

# Initialize session state for dark mode if not already set
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Initialize session state for whisper model size if not already set
if 'whisper_model_size' not in st.session_state:
    st.session_state.whisper_model_size = "base"

# Initialize session state for summary language
if 'summary_language' not in st.session_state:
    st.session_state.summary_language = "English"

# Initialize session state for sentiment analysis approach
if 'sentiment_analysis_approach' not in st.session_state:
    st.session_state.sentiment_analysis_approach = "standard"
    
# Initialize session state for authentication
if 'user_authenticated' not in st.session_state:
    st.session_state.user_authenticated = False

if 'is_pro' not in st.session_state:
    st.session_state.is_pro = False

# Initialize clients
client = get_groq_client()
news_api_key = get_news_client()

# Initialize Monad blockchain client with error handling
try:
    monad_client = MonadBlockchainClient()
except Exception as e:
    st.warning(f"Failed to initialize Monad blockchain client: {e}")
    monad_client = None

def render_news_column(articles):
    """Render news articles in a Streamlit container with professional styling"""
    if not articles:
        st.info("No news articles available")
        return
    
    # Create a grid layout for news articles
    cols = st.columns(min(3, len(articles)))
    
    for idx, article in enumerate(articles):
        col_idx = idx % len(cols)
        with cols[col_idx]:
            st.markdown(render_news_card(article), unsafe_allow_html=True)
                
    # Display any remaining articles in a list format if more than fits in the grid
    if len(articles) > 3:
        st.markdown("### More Related Articles")
        for idx, article in enumerate(articles[3:], 3):
            with st.expander(f"{article['title']} ({article['source']})"):
                st.markdown(render_news_card(article), unsafe_allow_html=True)

def main():
    # Apply custom CSS based on current theme
    apply_custom_css()
    
    # Always render the authentication UI in the sidebar
    render_auth_ui()
    
    # Add dark mode toggle to sidebar (at the top, before other content)
    with st.sidebar:
        st.markdown("### Theme")
        render_dark_mode_toggle()
        st.markdown("---")
    
    # Render logo in main area
    render_logo()
    
    # Set page title in main area even when not authenticated
    st.header("AI Meeting Summarizer")
    
    # Only show main content if authenticated
    if st.session_state.user_authenticated:
        # Render user profile in sidebar
        render_user_profile()
    
        # Add settings in sidebar
        with st.sidebar:
            st.subheader("Settings")
            st.session_state.whisper_model_size = st.selectbox(
                "Whisper Model Size", 
                ["tiny", "base", "small", "medium", "large"],
                index=1  # Default to "base"
            )
            
            # Add language selection only for Pro users
            if st.session_state.is_pro:
                st.session_state.summary_language = st.selectbox(
                    "Summary Language",
                    list(LANGUAGES.keys()),
                    index=0  # Default to English
                )
                
                # Add sentiment analysis approach selection only for Pro users
                st.session_state.sentiment_analysis_approach = st.selectbox(
                    "Sentiment Analysis Type",
                    ["standard", "detailed", "emotional"],
                    index=0,  # Default to standard
                    help="Choose between standard, detailed, or emotional sentiment analysis"
                )
            else:
                st.info("📌 Upgrade to Pro for multi-language summaries and advanced sentiment analysis")
                # Default to English for non-Pro users
                st.session_state.summary_language = "English"
                # Default to standard sentiment analysis for non-Pro users
                st.session_state.sentiment_analysis_approach = "standard"
        
        # Main content area (full width)
        with st.container():
            upload_column, info_column = st.columns([2, 1])
            
            with upload_column:
                st.markdown("### Upload Meeting Content")
                uploaded_file = st.file_uploader("Upload meeting notes, audio, or video", type=["txt", "pdf", "docx", "mp3", "wav", "mp4", "avi", "mov"])
            
            with info_column:
                st.markdown("### How It Works")
                st.markdown("""
                1. Upload your meeting file
                2. Our AI will transcribe audio/video
                3. Get your summary and sentiment analysis
                4. See related news and insights
                """)
        if uploaded_file:
            file_path_or_text = extract_text_from_file(uploaded_file)

            if uploaded_file.type.startswith("audio/") or uploaded_file.type.startswith("video/"):
                if file_path_or_text:  # Only proceed if audio extraction was successful
                    with st.spinner("Processing audio..."):
                        # First preprocess the audio
                        enhanced_audio_path = preprocess_audio(file_path_or_text)
                        
                        # Then transcribe it
                        transcript = transcribe_with_transformers_whisper(
                            enhanced_audio_path,
                            st.session_state.whisper_model_size,
                        )
                        
                        # Improve transcript quality
                        transcript = improve_transcript_quality(transcript)
                        
                        # Set text_to_summarize to the transcript
                        text_to_summarize = transcript
                        
                        # Show the transcript to the user
                        with st.expander("View Transcript"):
                            st.write(transcript)
                        
                        try:
                            os.unlink(file_path_or_text)  # Clean up original audio
                            if enhanced_audio_path != file_path_or_text:
                                os.unlink(enhanced_audio_path)  # Clean up enhanced audio
                        except Exception as e:
                            st.warning(f"Error cleaning up temporary files: {e}")
                else:
                    st.error("Failed to extract audio from the uploaded file.")
                    return  # Stop processing if audio extraction failed
            else:
                text_to_summarize = file_path_or_text

            if text_to_summarize:
                content_hash = hashlib.sha256(text_to_summarize.encode()).hexdigest()

                # Display content processing in a card
                st.markdown("### Content Analysis")
                with st.container():
                    processing_cols = st.columns(4)
                    with processing_cols[0]:
                        st.metric("File Size", f"{len(text_to_summarize)/1000:.1f} KB")
                    with processing_cols[1]:
                        st.metric("Word Count", f"{len(text_to_summarize.split())}")
                    with processing_cols[2]:
                        content_type = "Audio/Video" if uploaded_file.type.startswith(("audio/", "video/")) else "Document"
                        st.metric("Content Type", content_type)
                    with processing_cols[3]:
                        st.metric("Processing", "Complete", delta="100%")

                # Blockchain verification only for Pro users
                if monad_client and st.session_state.is_pro:
                    try:
                        st.markdown("### Blockchain Verification")
                        
                        # Create two columns for blockchain info
                        blockchain_cols = st.columns(2)
                        
                        with blockchain_cols[0]:
                            # Track data provenance using Monad blockchain
                            monad_success, tx_hash = monad_client.track_data_provenance(
                                source="MeetingNotes", content_hash=content_hash
                            )
                            if monad_success:
                                st.success(f"Data provenance tracked successfully")
                                st.code(f"{tx_hash[:20]}...{tx_hash[-8:]}", language="text")
                                st.markdown(f"[View on Monad Explorer]({monad_client.explorer_url}/tx/{tx_hash})")
                            
                        with blockchain_cols[1]:
                            # Verify credibility using Monad blockchain
                            credibility_score, sources = monad_client.verify_credibility(content_hash)
                            
                            # Use a gauge-like visualization for credibility score
                            st.markdown("#### Content Credibility")
                            st.progress(credibility_score/100)
                            st.metric("Score", f"{credibility_score}/100")
                            
                    except Exception as e:
                        st.error(f"Error with Monad blockchain services: {e}")
                elif not st.session_state.is_pro:
                    # Show upgrade banner for credibility scoring
                    render_pro_feature_banner("Upgrade to Pro for content credibility verification")

                # Summarization and Analysis
                with st.spinner("Summarizing with AI..."):
                    if client:
                        # Generate summary in English first
                        summary_english = summarize_text_groq(text_to_summarize, client)
                        sentiment_english = analyze_sentiment(text_to_summarize, client)
                        
                        # Translate to target language if Pro user and not English
                        target_lang = st.session_state.summary_language
                        if target_lang != "English" and st.session_state.is_pro:
                            summary = translate_to_language(summary_english, target_lang, client)
                            sentiment = translate_to_language(sentiment_english, target_lang, client)
                        else:
                            summary = summary_english
                            sentiment = sentiment_english
                    else:
                        summary = "Summary unavailable. API client not initialized."
                        sentiment = "Sentiment analysis unavailable. API client not initialized."

                # Display the summary and sentiment
                st.markdown("### Summary")
                render_summary_box(summary)

                # Display sentiment analysis with type label for Pro users
                sentiment_type = st.session_state.sentiment_analysis_approach.capitalize()
                st.markdown(f"### Sentiment Analysis")
                
                # For non-Pro users, show a hint that advanced sentiment is available
                if not st.session_state.is_pro and sentiment_type == "Standard":
                    render_sentiment_box(sentiment, "Standard")
                    render_pro_feature_banner("Upgrade to Pro for detailed and emotional sentiment analysis")
                else:
                    render_sentiment_box(sentiment, sentiment_type)

                # PDF download option only for Pro users
                if st.session_state.is_pro:
                    st.markdown("### Export Options")
                    # Create PDF download link with the improved function
                    with st.spinner("Generating PDF..."):
                        pdf_path = create_summary_pdf(summary, sentiment)
                        
                        # Use Streamlit's native download button instead of HTML link
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                        
                        download_col1, download_col2 = st.columns([1, 3])
                        with download_col1:
                            st.download_button(
                                label="📄 Download as PDF",
                                data=pdf_bytes,
                                file_name="meeting_summary.pdf",
                                mime="application/pdf",
                                key="pdf_download"
                            )
                        
                        # Clean up the PDF file after offering download
                        try:
                            if 'previous_pdf_path' in st.session_state and st.session_state.previous_pdf_path != pdf_path:
                                os.unlink(st.session_state.previous_pdf_path)
                        except Exception as e:
                            pass  # Silently ignore cleanup errors
                        
                        # Store this path for cleanup on next run
                        st.session_state.previous_pdf_path = pdf_path
                else:
                    # Show upgrade banner for PDF download
                    render_pro_feature_banner("Upgrade to Pro to download summaries as PDF")
                
                # Fetch and display related news AFTER summary is created
                if news_api_key and client:
                    with st.spinner("Fetching latest news..."):
                        # Use summary_english for related news search (better keywords)
                        related_news = fetch_related_news(summary_english, news_api_key)
                        st.session_state.news_articles = related_news
                    
                                        
                    # Show related news after summary
                    st.subheader("📰 Latest News")
                    if related_news:
                        render_news_column(related_news)
                    else:
                        st.info("No latest news found. Showing latest technology news instead.")
                        latest_news = fetch_latest_news(news_api_key, category="technology")
                        render_news_column(latest_news)
                
       # If no file uploaded yet and authenticated, show latest news at the bottom
        elif st.session_state.user_authenticated:
            st.subheader("📰 Latest News")
            if news_api_key:
                news_category = st.selectbox(
                    "News Category",
                    ["business", "technology", "health", "science", "sports", "entertainment", "general"],
                    index=1  # Default to technology
                )
                latest_news = fetch_latest_news(news_api_key, category=news_category)
                render_news_column(latest_news)
            else:
                st.info("News API key not configured. Please add it to the .env file to see news.")
    else:
        
       

        def display_features_cards():
            # Create two columns for the feature cards
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.markdown("""
                <div style="border: 1px solid #4CAF50; border-radius: 10px; padding: 20px; height: 100%;">
                    <h2 style="color: #4CAF50; text-align: center;">Basic Features</h2>
                    <ul style="list-style-type: none; padding-left: 10px;">
                        <li style="margin-bottom: 10px;">✅ <b>Transcribe audio & video</b> meetings automatically</li>
                        <li style="margin-bottom: 10px;">✅ <b>Generate concise summaries</b> of meeting content</li>
                        <li style="margin-bottom: 10px;">✅ <b>Extract action items</b> and deadlines</li>
                        <li style="margin-bottom: 10px;">✅ <b>Analyze sentiment</b> and key discussion points</li>
                        <li style="margin-bottom: 10px;">✅ <b>See news</b> related to your meeting topics</li>
                        <li style="margin-bottom: 10px;">✅ <b>Toggle between light and dark</b> mode for comfortable viewing</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style="border: 1px solid #2196F3; border-radius: 10px; padding: 20px; background-color: rgba(33, 150, 243, 0.05); height: 100%;">
                    <h2 style="color: #000000; text-align: center;">Pro Features</h2>
                    <ul style="list-style-type: none; padding-left: 10px;">
                        <li style="margin-bottom: 10px;">⭐ <b>Download summaries as PDF</b> for easy sharing</li>
                        <li style="margin-bottom: 10px;">⭐ <b>Translate summaries to 20+ languages</b> for global teams</li>
                        <li style="margin-bottom: 10px;">⭐ <b>Content credibility verification</b> with blockchain</li>
                        <li style="margin-bottom: 10px;">⭐ <b>Advanced sentiment analysis</b> options</li>
                    </ul>
                    
                </div>
                """, unsafe_allow_html=True)

        # Add this function call in the main content area of main() when not authenticated
        if not st.session_state.user_authenticated:
            st.info("👋 Welcome to Poke Summarizer! Please sign in to continue.")
            
            # Display feature cards
            display_features_cards()
                                   
        # Dark mode toggle still available for unauthenticated users
        with st.sidebar:
            st.markdown("### Try Dark Mode")
            st.markdown("You can toggle dark mode even before signing in!")
        
        # Show generic news when not authenticated
        st.subheader("📰 Latest News")
        if news_api_key:
            news_category = "technology"
            latest_news = fetch_latest_news(news_api_key, category=news_category)
            render_news_column(latest_news)

    # Footer and Version Info (Keep at the bottom of main.py)
    st.markdown(
        """
    ---
    <p style='text-align: center;'>Poke Summarizer © 2025 | AI-powered News transcription and summarization tool</p>
    """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.info("Poke Summarizer v1.0.0")

if __name__ == "__main__":
    main()