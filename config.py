import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Streamlit page configuration
st.set_page_config(page_title="AI Meetings and News Summarizer", layout="wide", page_icon="📝")

# Environment variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY")  # Replace with your API key
BASE_API_KEY = os.environ.get("BASE_API_KEY", "YOUR_BASE_API_KEY")  # Replace with your API key
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "YOUR_NEWS_API_KEY")  # News API key

# Monad blockchain configuration
DEPLOYER_PRIVATE_KEY = os.environ.get("DEPLOYER_PRIVATE_KEY", "")
MONAD_RPC_URL = os.environ.get("MONAD_RPC_URL", "https://testnet-rpc.monad.xyz/")
MONAD_CHAIN_ID = os.environ.get("MONAD_CHAIN_ID", "10143")
MONAD_EXPLORER_URL = os.environ.get("MONAD_EXPLORER_URL", "https://testnet.monadexplorer.com/")

# Language support dictionary
LANGUAGES = {
    "English": "English",
    "Spanish": "Spanish (Español)",
    "French": "French (Français)",
    "German": "German (Deutsch)",
    "Italian": "Italian (Italiano)",
    "Portuguese": "Portuguese (Português)",
    "Vietnamese": "Vietnamese (Tiếng Việt)",
    "Indonesian": "Indonesian (Bahasa Indonesia)",
    "Dutch": "Dutch (Nederlands)",
    "Swedish": "Swedish (Svenska)",
    "Norwegian": "Norwegian (Norsk)",
    "Danish": "Danish (Dansk)",
    "Finnish": "Finnish (Suomi)"
}

# Initialize session state variables
if 'user_authenticated' not in st.session_state:
    st.session_state.user_authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'is_pro' not in st.session_state:
    st.session_state.is_pro = False
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'news_articles' not in st.session_state:
    st.session_state.news_articles = []