# user_auth.py
import streamlit as st
import hashlib
from datetime import datetime

class BaseSDK:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.base.com/v1"  # Replace with actual Base API URL
        self.user_data = None

    def sign_up(self, username, password):
        """Register a new user"""
        if username in st.session_state.users:
            return False, "Username already exists"
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        st.session_state.users[username] = {
            "password": hashed_password,
            "is_pro": False,
            "created_at": datetime.now().isoformat()
        }
        return True, "User registered successfully"

    def sign_in(self, username, password):
        """Authenticate user with username and password"""
        if username not in st.session_state.users:
            return False, "User not found"
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if st.session_state.users[username]["password"] != hashed_password:
            return False, "Invalid password"
        self.user_data = {
            "username": username,
            "is_pro": st.session_state.users[username]["is_pro"]
        }
        return True, "Authentication successful"

    def check_subscription(self, username):
        """Check if user has active subscription"""
        return st.session_state.users.get(username, {}).get("is_pro", False)

    def upgrade_to_pro(self, username):
        """Upgrade user to Pro tier"""
        if username in st.session_state.users:
            st.session_state.users[username]["is_pro"] = True
            return True
        return False

def render_auth_ui():
    """Render the authentication UI"""
    with st.sidebar:
        st.subheader("👤 Authentication")
        
        # Initialize demo account if it doesn't exist
        if 'users' in st.session_state and 'demo' not in st.session_state.users:
            import hashlib
            st.session_state.users['demo'] = {
                "password": hashlib.sha256("password".encode()).hexdigest(),
                "is_pro": True,
                "created_at": datetime.now().isoformat()
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
                            base_client = BaseSDK(st.session_state.get("BASE_API_KEY")) # Safely access BASE_API_KEY
                            success, message = base_client.sign_in(username, password)

                            if success:
                                st.session_state.user_authenticated = True
                                st.session_state.user_id = username
                                st.session_state.is_pro = base_client.check_subscription(username)
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
                            base_client = BaseSDK(st.session_state.get("BASE_API_KEY"))  # Safely access BASE_API_KEY
                            success, message = base_client.sign_up(new_username, new_password)

                            if success:
                                st.success(f"{message}. Please sign in.")
                            else:
                                st.error(message)

            st.markdown("---")
            st.caption("Demo Account: `demo` / `password`")

def render_user_profile():
    """Render the user profile section"""
    if not st.session_state.get('user_authenticated', False):
        return
        
    with st.sidebar:
        st.subheader(f"Welcome, {st.session_state.user_id}!")
        if st.session_state.is_pro:
            st.success("Pro Subscription Active ✓")
        else:
            st.warning("Free Tier")
            if st.button("Upgrade to Pro"):
                base_client = BaseSDK(st.session_state.get("BASE_API_KEY")) # Safely access BASE_API_KEY
                if base_client.upgrade_to_pro(st.session_state.user_id):
                    st.session_state.is_pro = True
                    st.success("Upgraded to Pro successfully!")
                    st.rerun()

        if st.button("Sign Out"):
            st.session_state.user_authenticated = False
            st.session_state.user_id = None
            st.session_state.is_pro = False
            st.rerun()