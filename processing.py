# processing.py
import streamlit as st
import tempfile
import os
from PyPDF2 import PdfReader
from docx import Document
from moviepy.video.io.VideoFileClip import VideoFileClip

def extract_text_from_file(uploaded_file):
    """Extract text from TXT, PDF, DOCX, audio, or video files."""

    if uploaded_file is None:
        return None

    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")

    elif uploaded_file.type == "application/pdf":
        try:
            pdf_reader = PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            if not text.strip():
                return "No extractable text found in PDF."
            return text
        except Exception as e:
            st.error(f"Error extracting text from PDF: {e}")
            return "Failed to extract text from PDF file."

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            doc = Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs if para.text])
            return text
        except Exception as e:
            st.error(f"Error extracting text from DOCX: {e}")
            return "Failed to extract text from DOCX file."

    elif uploaded_file.type.startswith("audio/"):
        with st.spinner("Processing audio file and transcribing..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                audio_path = tmp_file.name
            return audio_path  # Return audio path for transcription in separate function

    elif uploaded_file.type.startswith("video/"):
        with st.spinner("Extracting audio from video..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_video:
                    tmp_video.write(uploaded_file.getvalue())
                    video_path = tmp_video.name

                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
                try:
                    video = VideoFileClip(video_path)
                    video.audio.write_audiofile(audio_path, logger=None)
                    video.close()
                except Exception as e:
                    st.error(f"Error extracting audio: {e}")
                    return None  # Indicate failure

                return audio_path  # Return audio path for transcription
            except ImportError:
                st.error("MoviePy not installed. Please install with: pip install moviepy")
                return None
            except Exception as e:
                st.error(f"Error processing video: {str(e)}")
                return None
    return None


def preprocess_audio(audio_path):
    """Enhance audio quality before transcription."""
    try:
        import librosa
        import soundfile as sf
        
        with st.spinner("Preprocessing audio for improved quality..."):
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000)
            
            # Noise reduction
            y_denoised = librosa.effects.preemphasis(y)
            
            # Normalize audio
            y_normalized = librosa.util.normalize(y_denoised)
            
            # Save preprocessed audio
            processed_path = audio_path.replace('.', '_enhanced.')
            sf.write(processed_path, y_normalized, sr)
            
            return processed_path
    except Exception as e:
        st.warning(f"Audio preprocessing skipped: {e}")
        return audio_path