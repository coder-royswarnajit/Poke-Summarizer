# wallet_integration.py
import streamlit as st
import hashlib
import json
import os
import time
from web3 import Web3
from eth_account.messages import encode_defunct
from datetime import datetime

class BaseWalletIntegration:
    def __init__(self):
        # Base network RPC URL (Testnet or Mainnet)
        self.base_rpc_url = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
        self.base_chain_id = 8453  # Base mainnet chain ID
        self.base_testnet_chain_id = 84531  # Base testnet chain ID
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(self.base_rpc_url))
        
        # Check connection
        self.is_connected = self.w3.is_connected()
        
        # Session state for wallet connection
        if 'wallet_connected' not in st.session_state:
            st.session_state.wallet_connected = False
        
        if 'wallet_address' not in st.session_state:
            st.session_state.wallet_address = None
            
        if 'wallet_chain_id' not in st.session_state:
            st.session_state.wallet_chain_id = None
    
    def render_wallet_connect_ui(self):
        """Render the wallet connection UI in the sidebar"""
        with st.sidebar:
            st.subheader("🔒 Base Wallet")
            
            if not st.session_state.wallet_connected:
                st.markdown("""
                Connect your wallet to access exclusive features:
                - Store summaries on Base blockchain
                - Pay for Pro features with cryptocurrency
                - Access tokenized communities
                """)
                
                # Wallet connection methods
                connect_method = st.radio(
                    "Connect Method",
                    ["MetaMask", "WalletConnect", "Coinbase Wallet"]
                )
                
                if st.button("Connect Wallet"):
                    # For demo purposes, simulate wallet connection
                    self._simulate_wallet_connection(connect_method)
            else:
                # Show connected wallet info
                st.success(f"✓ Wallet Connected")
                
                # Display wallet address with truncation
                address = st.session_state.wallet_address
                truncated_address = f"{address[:6]}...{address[-4:]}"
                
                st.markdown(f"""
                **Address**: `{truncated_address}`  
                **Network**: {'Base Mainnet' if st.session_state.wallet_chain_id == self.base_chain_id else 'Base Testnet' if st.session_state.wallet_chain_id == self.base_testnet_chain_id else 'Unknown'}  
                **Balance**: {self._get_wallet_balance()} ETH
                """)
                
                # Add option to sign message
                if st.button("Sign Message (Auth)"):
                    self._simulate_signature_request()
                
                # Add option to disconnect wallet
                if st.button("Disconnect Wallet"):
                    st.session_state.wallet_connected = False
                    st.session_state.wallet_address = None
                    st.session_state.wallet_chain_id = None
                    st.rerun()
                
                # Network warning if not on Base
                if st.session_state.wallet_chain_id not in [self.base_chain_id, self.base_testnet_chain_id]:
                    st.warning("Please switch to Base network in your wallet")
    
    def _simulate_wallet_connection(self, connect_method):
        """Simulate wallet connection for demo purposes"""
        with st.spinner(f"Connecting via {connect_method}..."):
            time.sleep(1)  # Simulate connection delay
            
            # Generate a demo wallet address
            sample_addresses = {
                "MetaMask": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                "WalletConnect": "0x7cB57B5A97eAbe94205C07890BE4c1aD31E486A8",
                "Coinbase Wallet": "0x2546BcD3c84621e976D8185a91A922aE77ECEc30"
            }
            
            st.session_state.wallet_address = sample_addresses.get(connect_method)
            st.session_state.wallet_connected = True
            st.session_state.wallet_chain_id = self.base_chain_id  # Assume Base mainnet
            
            st.success(f"Wallet connected successfully")
            st.rerun()
    
    def _simulate_signature_request(self):
        """Simulate a signature request for authentication"""
        with st.spinner("Waiting for signature..."):
            time.sleep(2)  # Simulate signing delay
            
            # In a real implementation, this would verify the signature
            # For demo purposes, we'll just simulate a successful signature
            
            # Link wallet with current user if authenticated
            if st.session_state.get('user_authenticated', False):
                user_id = st.session_state.get('user_id')
                self._link_wallet_to_user(user_id, st.session_state.wallet_address)
                st.success("Wallet linked to your account!")
            else:
                st.info("Please sign in to link your wallet")
    
    def _get_wallet_balance(self):
        """Get wallet balance (simulated for demo)"""
        if not st.session_state.wallet_connected:
            return 0
        
        # In real implementation, use:
        # balance_wei = self.w3.eth.get_balance(st.session_state.wallet_address)
        # return self.w3.from_wei(balance_wei, 'ether')
        
        # For demo purposes, return a fixed value
        return 0.125
    
    def _link_wallet_to_user(self, user_id, wallet_address):
        """Link wallet address to user account"""
        if 'users' in st.session_state and user_id in st.session_state.users:
            if 'wallet_addresses' not in st.session_state.users[user_id]:
                st.session_state.users[user_id]['wallet_addresses'] = []
            
            # Add wallet address if not already linked
            if wallet_address not in st.session_state.users[user_id]['wallet_addresses']:
                st.session_state.users[user_id]['wallet_addresses'].append(wallet_address)
            
            return True
        return False
    
    def authenticate_with_wallet(self, message="Sign this message to authenticate with Poke Summarizer"):
        """Authenticate user via wallet signature"""
        if not st.session_state.wallet_connected:
            return False, "Wallet not connected"
        
        # In real implementation:
        # 1. Create a challenge message with nonce
        # 2. Ask user to sign it
        # 3. Verify the signature
        # 4. Check if wallet is linked to an account
        
        # For demo purposes, return success
        return True, "Authentication successful"
    
    def is_wallet_linked_to_user(self, user_id):
        """Check if the connected wallet is linked to the user"""
        if not st.session_state.wallet_connected:
            return False
            
        if 'users' in st.session_state and user_id in st.session_state.users:
            wallet_addresses = st.session_state.users[user_id].get('wallet_addresses', [])
            return st.session_state.wallet_address in wallet_addresses
            
        return False

    def render_token_balance(self):
        """Render token balance UI"""
        if not st.session_state.wallet_connected:
            return
            
        st.subheader("Token Balance")
        
        # For demo purposes, show some mock token balances
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("POKE Tokens", "150.00")
        
        with col2:
            st.metric("Base Credits", "25.5", delta="↑5.5")
            
        # Add token transaction history
        with st.expander("Transaction History"):
            st.markdown("""
            | Date | Token | Amount | Type |
            | ---- | ----- | ------ | ---- |
            | 2025-04-25 | POKE | +50.0 | Reward |
            | 2025-04-22 | POKE | -25.0 | Premium |
            | 2025-04-20 | Base Credits | +10.0 | Purchase |
            """)
    
    def render_nft_gallery(self):
        """Render NFT gallery for the user"""
        if not st.session_state.wallet_connected:
            return
            
        st.subheader("Your NFT Collection")
        
        # For demo purposes, display mock NFTs
        nft_cols = st.columns(3)
        
        with nft_cols[0]:
            st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/92.png",
                     caption="Gastly #001")
            st.markdown("**Rarity**: Common")
            
        with nft_cols[1]:
            st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/94.png", 
                     caption="Gengar #002")
            st.markdown("**Rarity**: Rare")
            
        with nft_cols[2]:
            st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/93.png", 
                     caption="Haunter #003")
            st.markdown("**Rarity**: Uncommon")
    
    def pay_with_crypto(self, amount, purpose="Pro Subscription"):
        """Process a crypto payment (simulated)"""
        if not st.session_state.wallet_connected:
            return False, "Wallet not connected"
            
        # In a real implementation:
        # 1. Create a transaction request
        # 2. Send request to wallet for signing
        # 3. Submit signed transaction to Base network
        # 4. Wait for confirmation
        
        # For demo purposes, return success
        return True, f"Payment of {amount} ETH for {purpose} successful"

# Helper function to integrate with existing auth
def wallet_auth_ui():
    """Render wallet authentication UI as an alternative login method"""
    wallet_integration = BaseWalletIntegration()
    
    st.subheader("Connect Wallet to Authenticate")
    st.markdown("You can sign in with your Base wallet")
    
    if st.button("Connect Wallet to Sign In"):
        if st.session_state.wallet_connected:
            # Check if this wallet is associated with any user
            linked_user = None
            
            # Search for a user with this wallet address
            for username, user_data in st.session_state.users.items():
                wallet_addresses = user_data.get('wallet_addresses', [])
                if st.session_state.wallet_address in wallet_addresses:
                    linked_user = username
                    break
            
            if linked_user:
                # Log the user in
                st.session_state.user_authenticated = True
                st.session_state.user_id = linked_user
                st.session_state.is_pro = st.session_state.users[linked_user].get('is_pro', False)
                st.success(f"Authenticated as {linked_user}")
                st.rerun()
            else:
                st.warning("No account linked to this wallet. Please sign up first.")
        else:
            st.error("Please connect your wallet first")
            
# Function to render web3 payment UI for pro upgrade
def render_crypto_payment_ui():
    """Render crypto payment UI for pro upgrade"""
    wallet_integration = BaseWalletIntegration()
    
    st.subheader("Upgrade with Crypto")
    
    if st.session_state.wallet_connected:
        eth_price = 0.01  # ETH price for pro upgrade
        usd_equivalent = eth_price * 3050  # Assuming 1 ETH = $3050
        
        st.markdown(f"""
        **Pro Upgrade Price**: {eth_price} ETH (≈ ${usd_equivalent:.2f})
        """)
        
        if st.button("Pay with ETH"):
            success, message = wallet_integration.pay_with_crypto(eth_price, "Pro Upgrade")
            if success:
                # Update user status
                user_id = st.session_state.get('user_id')
                if 'users' in st.session_state and user_id in st.session_state.users:
                    st.session_state.users[user_id]['is_pro'] = True
                    st.session_state.is_pro = True
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    else:
        st.info("Connect your wallet first to pay with crypto")