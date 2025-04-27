import streamlit as st
import hashlib
import requests
import json
from datetime import datetime

class BaseWalletSDK:
    def __init__(self, api_key=None):
        self.api_key = api_key or st.session_state.get("BASE_API_KEY")
        self.base_url = "https://api.base.org/v1"  # Base API endpoint
        
    def generate_wallet(self, username):
        """Create a new wallet for user"""
        # In a real implementation, this would make an API call to Base
        # For demo purposes, we're generating a simulated wallet address
        wallet_seed = f"{username}-{datetime.now().timestamp()}"
        wallet_address = "0x" + hashlib.sha256(wallet_seed.encode()).hexdigest()[:40]
        return {
            "address": wallet_address,
            "created_at": datetime.now().isoformat(),
            "balance": 0.0,
            "currency": "ETH"
        }
    
    def get_wallet_balance(self, wallet_address):
        """Get current balance for wallet"""
        # In production, this would query the Base blockchain
        # For demo purposes, we'll return the stored balance
        users = st.session_state.get("users", {})
        for username, user_data in users.items():
            if user_data.get("wallet", {}).get("address") == wallet_address:
                return user_data.get("wallet", {}).get("balance", 0.0)
        return 0.0
    
    def process_payment(self, wallet_address, amount, recipient="app_treasury"):
        """Process crypto payment from user wallet"""
        # Simulate a blockchain transaction
        users = st.session_state.get("users", {})
        for username, user_data in users.items():
            if user_data.get("wallet", {}).get("address") == wallet_address:
                wallet = user_data.get("wallet", {})
                if wallet.get("balance", 0) >= amount:
                    # Update balance after payment
                    st.session_state.users[username]["wallet"]["balance"] -= amount
                    
                    # Record the transaction
                    if "transactions" not in st.session_state.users[username]:
                        st.session_state.users[username]["transactions"] = []
                    
                    transaction = {
                        "hash": "0x" + hashlib.sha256(f"{wallet_address}-{amount}-{datetime.now().timestamp()}".encode()).hexdigest(),
                        "from": wallet_address,
                        "to": recipient,
                        "amount": amount,
                        "currency": "ETH",
                        "timestamp": datetime.now().isoformat(),
                        "status": "confirmed"
                    }
                    
                    st.session_state.users[username]["transactions"].append(transaction)
                    return True, transaction
                else:
                    return False, {"error": "Insufficient balance"}
        
        return False, {"error": "Wallet not found"}
    
    def add_funds_to_wallet(self, wallet_address, amount):
        """Add funds to wallet (for testing purposes)"""
        users = st.session_state.get("users", {})
        for username, user_data in users.items():
            if user_data.get("wallet", {}).get("address") == wallet_address:
                current_balance = user_data.get("wallet", {}).get("balance", 0)
                st.session_state.users[username]["wallet"]["balance"] = current_balance + amount
                return True
        return False

def upgrade_to_pro_with_crypto(username, amount=0.01):
    """Upgrade user to Pro using cryptocurrency payment"""
    if username not in st.session_state.users:
        return False, "User not found"
    
    wallet = st.session_state.users[username].get("wallet")
    if not wallet:
        return False, "No wallet associated with this account"
    
    wallet_sdk = BaseWalletSDK()
    success, result = wallet_sdk.process_payment(wallet["address"], amount)
    
    if success:
        # Upgrade user to Pro
        st.session_state.users[username]["is_pro"] = True
        st.session_state.users[username]["pro_since"] = datetime.now().isoformat()
        return True, "Payment successful! Your account has been upgraded to Pro."
    else:
        return False, f"Payment failed: {result.get('error', 'Unknown error')}"