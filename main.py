import streamlit as st
import os
import hashlib
from config import LANGUAGES, GROQ_API_KEY  # Import constants
from user_auth import render_auth_ui, render_user_profile
from datetime import datetime
from external_apis import get_groq_client, MonadBlockchainClient
from processing import extract_text_from_file, preprocess_audio
from pdf_utils import create_summary_pdf, get_pdf_download_link
from news_api import get_news_client, fetch_related_news, fetch_latest_news, render_news_column
from transcription_and_summarization import (
    transcribe_with_transformers_whisper,
    translate_to_english,
    translate_to_language,
    detect_language,
    improve_transcript_quality,
    summarize_text_groq,
    analyze_sentiment,
)  # Import all functions

# Initialize session state for whisper model size if not already set
if 'whisper_model_size' not in st.session_state:
    st.session_state.whisper_model_size = "base"

# Initialize session state for summary language
if 'summary_language' not in st.session_state:
    st.session_state.summary_language = "English"

# Initialize clients
client = get_groq_client()
news_api_key = get_news_client()

# Initialize Monad blockchain client with error handling
try:
    monad_client = MonadBlockchainClient()
except Exception as e:
    st.warning(f"Failed to initialize Monad blockchain client: {e}")
    monad_client = None

def add_copy_button(text, button_label="Copy to clipboard"):
    """Add a button that copies text to clipboard when clicked"""
    import json
    # Generate a unique key for this button
    key = f"copy_button_{hash(text)}"
    
    if st.button(button_label, key=key):
        # Use expandable container with st.code for easier copying
        with st.expander("Copy this text", expanded=True):
            st.code(text)
            st.success("Text ready to copy! Use the copy button in the top-right corner of the code block.")

def main():
    # Always render the authentication UI in the sidebar
    render_auth_ui()
    
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
            
            # Add language selection
            st.session_state.summary_language = st.selectbox(
                "Summary Language",
                list(LANGUAGES.keys()),
                index=0  # Default to English
            )
        
        # Main content area (full width)
        uploaded_file = st.file_uploader("Upload meeting notes, audio, or video", type=["txt", "pdf", "docx", "mp3", "wav", "mp4", "avi", "mov"])

        if uploaded_file:
            file_path_or_text = extract_text_from_file(uploaded_file)

            if uploaded_file.type.startswith("audio/") or uploaded_file.type.startswith("video/"):
                if file_path_or_text:  # Only proceed if audio extraction was successful
                    enhanced_audio_path = preprocess_audio(file_path_or_text)
                    transcript = transcribe_with_transformers_whisper(
                        enhanced_audio_path,
                        st.session_state.whisper_model_size,
                    )
                    text_to_summarize = translate_to_english(transcript)

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

                if monad_client:
                    try:
                        # Track data provenance using Monad blockchain
                        monad_success, tx_hash = monad_client.track_data_provenance(
                            source="MeetingNotes", content_hash=content_hash
                        )
                        if monad_success:
                            st.success(f"Data provenance tracked on Monad blockchain with transaction hash: {tx_hash}")
                            st.info(f"View on Monad Explorer: {monad_client.explorer_url}/tx/{tx_hash}")

                        # Verify credibility using Monad blockchain
                        credibility_score, sources = monad_client.verify_credibility(content_hash)
                        st.info(f"Content credibility score: {credibility_score}")
                        if sources:
                            st.info(f"Credibility verification sources: {sources}")
                    except Exception as e:
                        st.error(f"Error with Monad blockchain services: {e}")

                # Summarization and Analysis
                with st.spinner("Summarizing with AI..."):
                    if client:
                        # Generate summary in English first
                        summary_english = summarize_text_groq(text_to_summarize, client)
                        sentiment_english = analyze_sentiment(text_to_summarize, client)
                        
                        # Translate to target language if not English
                        target_lang = st.session_state.summary_language
                        if target_lang != "English":
                            summary = translate_to_language(summary_english, target_lang, client)
                            sentiment = translate_to_language(sentiment_english, target_lang, client)
                        else:
                            summary = summary_english
                            sentiment = sentiment_english
                    else:
                        summary = "Summary unavailable. API client not initialized."
                        sentiment = "Sentiment analysis unavailable. API client not initialized."

                # Display the summary and sentiment
                st.subheader("Summary")
                st.info(summary)
                # Add copy button for summary
                add_copy_button(summary, "Copy Summary")

                st.subheader("Sentiment Analysis")
                st.info(sentiment)
                # Add copy button for sentiment
                add_copy_button(sentiment, "Copy Sentiment Analysis")
                
                # Create PDF download link with the improved function
                with st.spinner("Generating PDF..."):
                    pdf_path = create_summary_pdf(summary, sentiment)
                    
                    # Use Streamlit's native download button instead of HTML link
                    with open(pdf_path, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                    
                    st.download_button(
                        label="📄 Download Summary as PDF",
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
                
                # Fetch and display related news AFTER summary is created
                if news_api_key and client:
                    with st.spinner("Fetching related news..."):
                        # Use summary_english for related news search (better keywords)
                        related_news = fetch_related_news(summary_english, news_api_key)
                        st.session_state.news_articles = related_news
                    
                    # Show related news after summary
                    st.subheader("📰 Related News")
                    if related_news:
                        render_news_column(related_news)
                    else:
                        st.info("No related news found. Showing latest technology news instead.")
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
        # Show welcome message when not authenticated
        st.info("👋 Welcome to Poke Summarizer! Please sign in to continue.")
        st.markdown("""
        ### Features:
        - Automatically transcribe audio and video meetings
        - Generate concise summaries of meeting content
        - Extract action items and deadlines
        - Analyze sentiment and key discussion points
        - Download summaries as PDF
        - Copy results to clipboard with one click
        - Translate summaries to 20+ languages
        - See news related to your meeting topics
        
        Sign in with the demo account or create your own to get started!
        """)
        
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
    <p style='text-align: center;'>Poke Summarizer © 2025 | AI-powered meeting transcription and summarization tool</p>
    """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.info("Poke Summarizer v1.0.0")

if __name__ == "__main__":
    main()