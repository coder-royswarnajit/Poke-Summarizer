import streamlit as st
import hashlib
from datetime import datetime
from wallet_integration import BaseWalletSDK, upgrade_to_pro_with_crypto

class BaseSDK:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.base.com/v1"  # Replace with actual Base API URL
        self.user_data = None
        self.wallet_sdk = BaseWalletSDK(api_key)

    def sign_up(self, username, password):
        """Register a new user"""
        if 'users' not in st.session_state:
            st.session_state.users = {}
        
        if username in st.session_state.users:
            return False, "Username already exists"
        
        # Create user account
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Generate wallet for the user
        wallet = self.wallet_sdk.generate_wallet(username)
        
        st.session_state.users[username] = {
            "password": hashed_password,
            "is_pro": False,
            "created_at": datetime.now().isoformat(),
            "wallet": wallet,
            "transactions": []
        }
        return True, "User registered successfully"

    def sign_in(self, username, password):
        """Authenticate user with username and password"""
        if 'users' not in st.session_state:
            st.session_state.users = {}
            
        if username not in st.session_state.users:
            return False, "User not found"
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if st.session_state.users[username]["password"] != hashed_password:
            return False, "Invalid password"
        self.user_data = {
            "username": username,
            "is_pro": st.session_state.users[username]["is_pro"],
            "wallet": st.session_state.users[username].get("wallet", {})
        }
        return True, "Authentication successful"

    def check_subscription(self, username):
        """Check if user has active subscription"""
        return st.session_state.users.get(username, {}).get("is_pro", False)

    def upgrade_to_pro(self, username, payment_method="traditional"):
        """Upgrade user to Pro tier"""
        if username in st.session_state.users:
            if payment_method == "crypto":
                return upgrade_to_pro_with_crypto(username)
            else:
                # Traditional payment method
                st.session_state.users[username]["is_pro"] = True
                return True, "Upgraded to Pro successfully"
        return False, "User not found"

def render_auth_ui():
    """Render the authentication UI"""
    with st.sidebar:
        st.subheader("👤 Authentication")
        
        # Initialize users dictionary if it doesn't exist
        if 'users' not in st.session_state:
            st.session_state.users = {}
        
        # Initialize demo account if it doesn't exist
        if 'demo' not in st.session_state.users:
            import hashlib
            wallet_sdk = BaseWalletSDK()
            wallet = wallet_sdk.generate_wallet('demo')
            wallet['balance'] = 0.05  # Give demo account some ETH to play with
            
            st.session_state.users['demo'] = {
                "password": hashlib.sha256("password".encode()).hexdigest(),
                "is_pro": True,
                "created_at": datetime.now().isoformat(),
                "wallet": wallet,
                "transactions": []
            }
        
        # Only show auth tabs if not authenticated
        if not st.session_state.get('user_authenticated', False):
            auth_tab = st.radio("", ["Sign In", "Sign Up"], horizontal=True)
            
            if auth_tab == "Sign In":
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submit_button = st.form_submit_button("Sign In")

                    if submit_button:
                        if not username or not password:
                            st.error("Please enter both username and password")
                        else:
                            base_client = BaseSDK(st.session_state.get("BASE_API_KEY"))
                            success, message = base_client.sign_in(username, password)

                            if success:
                                st.session_state.user_authenticated = True
                                st.session_state.user_id = username
                                st.session_state.is_pro = base_client.check_subscription(username)
                                st.session_state.user_wallet = st.session_state.users[username].get("wallet", {})
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

            else:  # Sign Up tab
                with st.form("signup_form"):
                    new_username = st.text_input("Create Username")
                    new_password = st.text_input("Create Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")
                    submit_button = st.form_submit_button("Sign Up")

                    if submit_button:
                        if not new_username or not new_password:
                            st.error("Please enter both username and password")
                        elif new_password != confirm_password:
                            st.error("Passwords do not match")
                        else:
                            base_client = BaseSDK(st.session_state.get("BASE_API_KEY"))
                            success, message = base_client.sign_up(new_username, new_password)

                            if success:
                                st.success(f"{message}. Please sign in.")
                                st.info("A crypto wallet has been created for your account!")
                            else:
                                st.error(message)

            st.markdown("---")
            st.caption("Demo Account: demo / password")

def render_wallet_ui():
    """Render the wallet interface"""
    if not st.session_state.get('user_authenticated', False):
        return
        
    with st.expander("💰 Crypto Wallet"):
        wallet = st.session_state.get('user_wallet', {})
        if wallet:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Wallet Address")
                st.code(wallet.get('address', 'No wallet'), language="text")
            
            with col2:
                st.subheader("Balance")
                st.metric("ETH", f"{wallet.get('balance', 0):.4f}")
            
            # Fund wallet (for demo purposes)
            if st.button("📥 Add 0.01 ETH (Demo)"):
                wallet_sdk = BaseWalletSDK()
                if wallet_sdk.add_funds_to_wallet(wallet.get('address'), 0.01):
                    # Update session state with new balance
                    st.session_state.user_wallet['balance'] = st.session_state.users[st.session_state.user_id]['wallet']['balance']
                    st.success("Funds added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add funds")
            
            # Show transactions if available
            transactions = st.session_state.users[st.session_state.user_id].get("transactions", [])
            if transactions:
                st.subheader("Transaction History")
                for tx in transactions:
                    st.markdown(f"""
                    **Transaction**: {tx['hash'][:10]}...{tx['hash'][-6:]}  
                    **Amount**: {tx['amount']} {tx['currency']}  
                    **Date**: {tx['timestamp'].split('T')[0]}  
                    **Status**: {tx['status']}
                    ---
                    """)
            else:
                st.info("No transaction history yet")
        else:
            st.warning("No wallet associated with this account")

def render_user_profile():
    """Render the user profile section"""
    if not st.session_state.get('user_authenticated', False):
        return
        
    with st.sidebar:
        st.subheader(f"Welcome, {st.session_state.user_id}!")
        
        # Display wallet information
        render_wallet_ui()
        
        # Subscription status
        if st.session_state.is_pro:
            st.success("Pro Subscription Active ✓")
        else:
            st.warning("Free Tier")
            st.markdown("""
            #### Pro Features:
            - Multiple language summaries
            - PDF download option
            - Content credibility scoring
            - Advanced sentiment analysis
            """)
            
            # Upgrade options
            upgrade_tab = st.radio("Upgrade Method:", ["Credit Card", "Crypto (Base)"], horizontal=True)
            
            if upgrade_tab == "Credit Card":
                if st.button("💳 Upgrade to Pro - $9.99/month"):
                    base_client = BaseSDK(st.session_state.get("BASE_API_KEY"))
                    success, message = base_client.upgrade_to_pro(st.session_state.user_id)
                    if success:
                        st.session_state.is_pro = True
                        st.success("Upgraded to Pro successfully!")
                        st.rerun()
            else:
                # Crypto payment option
                st.markdown("#### Pay with Cryptocurrency")
                st.write("Cost: 0.01 ETH on Base network")
                
                wallet = st.session_state.get('user_wallet', {})
                if wallet:
                    if wallet.get('balance', 0) >= 0.01:
                        if st.button("🔒 Pay with Crypto"):
                            base_client = BaseSDK(st.session_state.get("BASE_API_KEY"))
                            success, message = base_client.upgrade_to_pro(st.session_state.user_id, payment_method="crypto")
                            if success:
                                st.session_state.is_pro = True
                                # Update wallet in session state
                                st.session_state.user_wallet = st.session_state.users[st.session_state.user_id]['wallet']
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.error(f"Insufficient balance: {wallet.get('balance', 0):.4f} ETH")
                        st.info("Use the 'Add ETH' button in your wallet to add test funds")
                else:
                    st.error("No wallet available for payment")

        if st.button("Sign Out"):
            st.session_state.user_authenticated = False
            st.session_state.user_id = None
            st.session_state.is_pro = False
            st.session_state.user_wallet = None
            st.rerun()