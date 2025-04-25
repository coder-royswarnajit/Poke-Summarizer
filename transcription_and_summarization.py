import streamlit as st
import re
import os
from datetime import datetime
import dateparser
import json
from external_apis import get_groq_client  # Import the client function
from config import LANGUAGES  # Import the LANGUAGES dictionary

# Define default model size if not in session state
if 'whisper_model_size' not in st.session_state:
    st.session_state.whisper_model_size = "base"  # Set a default value

# Initialize sentiment analysis approach if not in session state
if 'sentiment_analysis_approach' not in st.session_state:
    st.session_state.sentiment_analysis_approach = "standard"  # Default to standard

# Initialize Groq client (moved here)
client = get_groq_client()

def transcribe_with_transformers_whisper(audio_path, whisper_model_size=None):
    """Transcribe audio using Transformers Whisper model."""
    try:
        import torch
        from transformers import pipeline

        # Use the parameter if provided, otherwise fall back to session state or default
        if whisper_model_size is None:
            whisper_model_size = st.session_state.get("whisper_model_size", "base")

        with st.spinner(f"Transcribing audio using Whisper {whisper_model_size} model..."):
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model_name = f"openai/whisper-{whisper_model_size}"
            transcriber = pipeline("automatic-speech-recognition", model=model_name, device=device)
            
            # Handle different return types based on model version
            result = transcriber(audio_path, return_timestamps=True)
            
            # Check if result is a dictionary or string
            if isinstance(result, dict):
                return result.get("text", "")
            elif isinstance(result, str):
                return result
            else:
                # If chunks, join them
                if isinstance(result, list) and result and "text" in result[0]:
                    return " ".join(chunk["text"] for chunk in result)
                return str(result)
    except ImportError:
        st.error("Required packages not installed. Please install torch and transformers.")
        return "Transcription failed: Missing dependencies."
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return f"Transcription failed: {str(e)}"
    
def preprocess_audio(audio_path):
    """Enhance audio quality before transcription."""
    try:
        import librosa
        import soundfile as sf

        with st.spinner("Preprocessing audio for improved quality..."):
            y, sr = librosa.load(audio_path, sr=16000)
            y_denoised = librosa.effects.preemphasis(y)
            y_normalized = librosa.util.normalize(y_denoised)
            processed_path = audio_path.replace('.', '_enhanced.')
            sf.write(processed_path, y_normalized, sr)
            return processed_path
    except Exception as e:
        st.warning(f"Audio preprocessing skipped: {e}")
        return audio_path

def translate_to_english(text):
    """Use Groq API to translate non-English text to English."""
    if not text or len(text.strip()) < 10:
        return text

    prompt = f"""
    Translate the following text to English.
    If the text is already in English, return it unchanged.
    Only provide the translation without any explanations or comments.

    Text to translate:
    {text}
    """
    try:
        if client is None:
            return text  # Return original text if client is unavailable
            
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error translating text: {e}")
        return text  # Return original text if translation fails

def detect_language(text):
    """Use Groq API to detect the language of the transcript."""
    if not text or len(text.strip()) < 10:
        return "English"  # Default to English for empty or very short texts

    prompt = f"""
    Based on the following text, detect the language it's written in.
    Return only the language name in English (e.g., "English", "Spanish", "Japanese", etc.).

    Text:
    {text[:1000]}  # Using just the first 1000 characters for efficiency
    """
    try:
        if client is None:
            return "English"  # Default to English if client is unavailable
            
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=50  # Limit response to just the language name
        )
        detected = response.choices[0].message.content.strip()
        # Handle case where response might include more text than just the language name
        for language in LANGUAGES.keys():
            if language.lower() in detected.lower():
                return language
        return detected
    except Exception as e:
        st.error(f"Error detecting language: {e}")
        return "English"  # Default to English if detection fails

def improve_transcript_quality(transcript):
    """Use Groq API to improve transcript quality by fixing errors, punctuation, and formatting."""
    if not transcript or len(transcript.strip()) < 50:
        return transcript

    prompt = f"""
    You are an expert transcriptionist. Improve the following meeting transcript by:
    1. Fixing spelling and grammar errors
    2. Adding proper punctuation and capitalization
    3. Separating speakers clearly if multiple speakers are present
    4. Formatting into clear paragraphs
    5. Removing filler words, repetitions, and disfluencies
    6. Preserving the original meaning and all important content

    Original transcript:
    {transcript}

    Return only the improved transcript without explanations.
    """
    try:
        if client is None:
            return transcript  # Return original transcript if client is unavailable
            
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error improving transcript: {e}")
        return transcript  # Return original transcript if improvement fails

def summarize_text_groq(transcript, client, target_language="English"):
    """Use Groq API to summarize the meeting transcript."""
    if not transcript or len(transcript.strip()) < 50:
        return "The transcript is too short to summarize."
    
    if client is None:
        return "Summary unavailable. API client not initialized."

    prompt = f"""
    Summarize the following meeting transcript in a concise and informative way.
    Highlight the key discussion points, decisions made, and important takeaways.

    IMPORTANT: Your summary must be written in {target_language} language.

    Transcript:
    {transcript}
    """
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error summarizing text: {e}")
        return "Summary failed to generate."


def analyze_sentiment(transcript, client):
    """Use Groq API to analyze the sentiment of the transcript."""
    if not transcript or len(transcript.strip()) < 50:
        return "The transcript is too short to analyze sentiment."
    
    if client is None:
        return "Sentiment analysis unavailable. API client not initialized."
        
    # Check which sentiment analysis approach to use
    sentiment_approach = st.session_state.get("sentiment_analysis_approach", "standard")
    
    if sentiment_approach == "standard":
        return analyze_standard_sentiment(transcript, client)
    elif sentiment_approach == "detailed":
        return analyze_detailed_sentiment(transcript, client)
    elif sentiment_approach == "emotional":
        return analyze_emotional_sentiment(transcript, client)
    else:
        return analyze_standard_sentiment(transcript, client)  # Default fallback


def analyze_standard_sentiment(transcript, client):
    """Standard sentiment analysis providing basic positive/negative/neutral classification."""
    prompt = f"""
    Analyze the overall sentiment of the following meeting transcript.
    Return the sentiment as one of the following: "Positive", "Negative", or "Neutral".

    Transcript:
    {transcript}
    """
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error analyzing sentiment: {e}")
        return "Sentiment analysis failed."


def analyze_detailed_sentiment(transcript, client):
    """Advanced sentiment analysis with confidence scores and reasoning."""
    prompt = f"""
    Perform an advanced sentiment analysis of the following meeting transcript.
    Provide:
    1. Overall sentiment classification (Positive, Negative, or Neutral)
    2. Confidence score (1-10)
    3. Brief explanation of key factors influencing the sentiment
    4. Any shifts in sentiment throughout the meeting
    5. Most emotionally charged topics or moments

    Format your response as a structured analysis with these sections.

    Transcript:
    {transcript}
    """
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error analyzing detailed sentiment: {e}")
        return "Detailed sentiment analysis failed."


def analyze_emotional_sentiment(transcript, client):
    """Emotional sentiment analysis focusing on specific emotions present."""
    prompt = f"""
    Analyze the emotional content of the following meeting transcript.
    Identify the primary emotions present (such as joy, frustration, enthusiasm, concern, etc.)
    and provide examples from the transcript that demonstrate these emotions.
    
    Also note any emotional patterns between different speakers if multiple people are present.
    
    Format your response as a clear emotional analysis of the meeting.

    Transcript:
    {transcript}
    """
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error analyzing emotional sentiment: {e}")
        return "Emotional sentiment analysis failed."
    
def translate_to_language(text, target_language="English", client=None):
    """Use Groq API to translate text to the specified language."""
    if not text or len(text.strip()) < 10 or target_language.lower() == "english":
        return text

    prompt = f"""
    Translate the following text to {target_language}.
    Only provide the translation without any explanations or comments.

    Text to translate:
    {text}
    """
    try:
        if client is None:
            return text  # Return original text if client is unavailable
            
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error translating text: {e}")
        return text  # Return original text if translation fails