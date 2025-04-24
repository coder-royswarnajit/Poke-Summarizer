import requests
import streamlit as st
import json
from datetime import datetime
import os
from config import DEPLOYER_PRIVATE_KEY, MONAD_RPC_URL, MONAD_CHAIN_ID, MONAD_EXPLORER_URL

# Groq Client (moved function here)
def get_groq_client():
    try:
        import groq
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key or api_key == "YOUR_GROQ_API_KEY":
            st.warning("Groq API key not configured. Some features will be unavailable.")
            return None
        client = groq.Client(api_key=api_key)
        return client
    except ImportError:
        st.error("Groq library not found. Please install it with 'pip install groq'.")
        return None
    except Exception as e:
        st.error(f"Error initializing Groq client: {e}")
        return None

# Monad Blockchain Client
class MonadBlockchainClient:
    def __init__(self):
        self.private_key = DEPLOYER_PRIVATE_KEY
        self.rpc_url = MONAD_RPC_URL
        self.chain_id = MONAD_CHAIN_ID
        self.explorer_url = MONAD_EXPLORER_URL

    def track_data_provenance(self, source, content_hash, metadata=None):
        try:
            # Check if private key is valid before making transaction
            if not self.private_key:
                st.warning("Monad private key not configured. Data provenance tracking skipped.")
                return False, None
                
            try:
                # Web3 setup for Monad blockchain
                from web3 import Web3
                w3 = Web3(Web3.HTTPProvider(self.rpc_url))
                
                if not w3.is_connected():
                    st.error("Cannot connect to Monad blockchain RPC.")
                    return False, None
                
                # Create transaction payload for provenance tracking
                # This is a simplified version - in a real implementation, you would:
                # 1. Create and deploy a smart contract for provenance tracking
                # 2. Call the contract's functions to store the provenance data
                
                # For demo purposes, we'll just show the transaction preparation
                nonce = w3.eth.get_transaction_count(w3.eth.account.from_key(self.private_key).address)
                
                tx_hash = f"0x{content_hash[:40]}"  # Mock transaction hash
                tx_url = f"{self.explorer_url}/tx/{tx_hash}"
                
                return True, tx_hash
            except ImportError:
                st.error("Web3 library not found. Please install with 'pip install web3'.")
                return False, None
            except Exception as e:
                st.error(f"Blockchain transaction error: {str(e)}")
                return False, None
        except Exception as e:
            st.error(f"Blockchain transaction error: {str(e)}")
            return False, None

    def verify_credibility(self, content_hash):
        try:
            # Check if private key is valid before verification
            if not self.private_key:
                st.warning("Monad configuration not set. Credibility verification skipped.")
                return 0, []
                
            try:
                # For demo purposes, we'll just generate a mock verification
                # In a real implementation, you would query the blockchain for verification data
                
                # Mock credibility score between 0 and 100
                import random
                credibility_score = random.randint(70, 95)
                
                # Mock sources
                sources = [
                    f"{self.explorer_url}/tx/0x{content_hash[:40]}",
                    f"{self.explorer_url}/address/0x{content_hash[41:81]}"
                ]
                
                return credibility_score, sources
            except Exception as e:
                st.error(f"Credibility verification error: {str(e)}")
                return 0, []
        except Exception as e:
            st.error(f"Credibility verification error: {str(e)}")
            return 0, []