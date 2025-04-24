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

# Initialize Groq client (moved here)
client = get_groq_client()

def transcribe_with_transformers_whisper(audio_path, whisper_model_size=None, chunk_size=30):
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
            result = transcriber(audio_path, return_timestamps=True, chunk_length_s=chunk_size)
            return result["text"]
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
        return "Summary unavailable in offline mode."

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

def extract_action_items(transcript, client, target_language="English"):
    """Use Groq API to extract action items, responsible persons, and deadlines."""
    if not transcript or len(transcript.strip()) < 50:
        return []
    
    if client is None:
        return "Action items unavailable in offline mode."

    prompt = f"""
    You are an AI that extracts structured action items from meeting transcripts.
    Identify action items, responsible persons, and deadlines where available.

    IMPORTANT: Translate the action descriptions into {target_language} language.

    Return the output as a JSON list with these keys: 'person', 'action', and 'deadline'.
    Keep person names in their original form.

    Ensure the deadline is extracted accurately. If no deadline is mentioned, use "Not specified".

    FORMAT YOUR RESPONSE AS VALID JSON ARRAY ONLY. No explanations before or after the JSON.

    Transcript:
    {transcript}
    """
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}  # Request JSON format
        )
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON response: {e}")
        return []
    except Exception as e:
        st.error(f"Error extracting action items: {e}")
        return []

def extract_deadlines(transcript, client):
    """Use Groq API to extract deadlines from the transcript."""
    if not transcript or len(transcript.strip()) < 50:
        return []
    
    if client is None:
        return "Deadlines unavailable in offline mode."

    prompt = f"""
    Extract all deadlines mentioned in the following meeting transcript.
    Return them as a JSON list of strings in 'YYYY-MM-DD' format.
    If no deadlines are found, return an empty list.

    Transcript:
    {transcript}
    """
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        deadlines = json.loads(response.choices[0].message.content.strip())
        # Parse dates using dateparser
        parsed_deadlines = []
        for deadline in deadlines:
            parsed_date = dateparser.parse(deadline)
            if parsed_date:
                parsed_deadlines.append(parsed_date.strftime("%Y-%m-%d"))
        return parsed_deadlines
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON response: {e}")
        return []
    except Exception as e:
        st.error(f"Error extracting deadlines: {e}")
        return []

def analyze_sentiment(transcript, client):
    """Use Groq API to analyze the sentiment of the transcript."""
    if not transcript or len(transcript.strip()) < 50:
        return "The transcript is too short to analyze sentiment."
    
    if client is None:
        return "Sentiment analysis unavailable in offline mode."

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