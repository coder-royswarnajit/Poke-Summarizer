import streamlit as st
import os
import hashlib
from config import LANGUAGES, GROQ_API_KEY  # Import constants
from user_auth import render_auth_ui, render_user_profile
from datetime import datetime
from external_apis import get_groq_client, MonadBlockchainClient, KafkaStreamer
from processing import extract_text_from_file, preprocess_audio
from pdf_utils import create_summary_pdf, get_pdf_download_link
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

# Initialize session state for chunk size if not already set
if 'chunk_size' not in st.session_state:
    st.session_state.chunk_size = 30

# Initialize session state for summary language
if 'summary_language' not in st.session_state:
    st.session_state.summary_language = "English"

# Initialize Groq client (moved here)
if not st.session_state.get('offline_mode', False):
    client = get_groq_client()
else:
    client = None

# Initialize Monad blockchain client and Kafka clients with error handling
try:
    monad_client = MonadBlockchainClient()
except Exception as e:
    st.warning(f"Failed to initialize Monad blockchain client: {e}")
    monad_client = None

try:
    kafka_bootstrap_server = os.environ.get("KAFKA_BOOTSTRAP_SERVER", "localhost:9092")
    kafka_streamer = KafkaStreamer(kafka_bootstrap_server, os.environ.get("KAFKA_TOPIC"))
except Exception as e:
    st.warning(f"Failed to initialize Kafka streamer: {e}")
    kafka_streamer = None

def add_copy_button(text, button_label="Copy to clipboard"):
    """Add a button that copies text to clipboard when clicked"""
    # Generate a unique key for this button
    key = f"copy_button_{hash(text)}"
    if st.button(button_label, key=key):
        try:
            # Using JavaScript to copy text to clipboard
            js_code = f"""
            <script>
                navigator.clipboard.writeText({text});
                // Show a tooltip or some indication it was copied
                alert('Copied to clipboard!');
            </script>
            """
            st.components.v1.html(js_code, height=0)
            st.success("Copied to clipboard!")
        except Exception as e:
            st.error(f"Failed to copy: {e}")

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
            st.session_state.chunk_size = st.slider(
                "Audio Chunk Size (seconds)", 
                min_value=10, 
                max_value=60, 
                value=30
            )
            st.session_state.offline_mode = st.checkbox("Offline Mode")
            
            # Add language selection
            st.session_state.summary_language = st.selectbox(
                "Summary Language",
                list(LANGUAGES.keys()),
                index=0  # Default to English
            )

        # Main content area
        uploaded_file = st.file_uploader("Upload meeting notes, audio, or video", type=["txt", "pdf", "docx", "mp3", "wav", "mp4", "avi", "mov"])

        if uploaded_file:
            file_path_or_text = extract_text_from_file(uploaded_file)

            if uploaded_file.type.startswith("audio/") or uploaded_file.type.startswith("video/"):
                if file_path_or_text:  # Only proceed if audio extraction was successful
                    enhanced_audio_path = preprocess_audio(file_path_or_text)
                    transcript = transcribe_with_transformers_whisper(
                        enhanced_audio_path,
                        st.session_state.whisper_model_size,
                        st.session_state.chunk_size,
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

                if not st.session_state.get('offline_mode', False) and monad_client:
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
                    if not st.session_state.get('offline_mode', False) and client:
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
                        summary = "Summary unavailable in offline mode."
                        sentiment = "Sentiment analysis unavailable in offline mode."

                st.subheader("Summary")
                st.info(summary)
                # Add copy button for summary
                add_copy_button(summary, "Copy Summary")


                st.subheader("Sentiment Analysis")
                st.info(sentiment)
                # Add copy button for sentiment
                add_copy_button(sentiment, "Copy Sentiment Analysis")
                
                # Create PDF download link
                with st.spinner("Generating PDF..."):
                    pdf_path = create_summary_pdf(summary,sentiment)
                    pdf_link = get_pdf_download_link(pdf_path)
                    st.markdown(pdf_link, unsafe_allow_html=True)

                # Streaming (Kafka) - Example with error handling
                if not st.session_state.get('offline_mode', False) and kafka_streamer:
                    try:
                        kafka_data = {
                            "summary": summary,
                            "sentiment": sentiment,
                            "timestamp": datetime.now().isoformat(),
                            "language": st.session_state.summary_language
                        }
                        if kafka_streamer.connect():
                            kafka_streamer.stream_data(kafka_data)
                            st.success("Summary streamed to Kafka!")
                    except Exception as e:
                        st.error(f"Kafka streaming error: {e}")
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
        
        Sign in with the demo account or create your own to get started!
        """)

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