import streamlit as st

def render_base_blockchain_info():
    """Display information about Base blockchain integration"""
    
    st.subheader("🔗 Base Blockchain Integration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### About Base Blockchain
        
        Base is an Ethereum L2 (Layer 2) blockchain that offers fast, secure, and low-cost cryptocurrency transactions. 
        It's developed by Coinbase, one of the world's leading cryptocurrency exchanges.
        
        **Benefits of our Base integration:**
        - **Low fees**: Pay for Pro upgrades with minimal gas fees
        - **Fast transactions**: Confirmation in seconds instead of minutes
        - **Security**: All transactions are secured by Ethereum's robust security model
        - **Transparency**: All payments are verifiable on the blockchain
        
        ### How It Works
        
        1. When you create an account, we automatically generate a Base-compatible wallet for you
        2. Add funds to your wallet (for demo purposes, use the "Add ETH" button)
        3. Use your wallet to pay for Pro subscription with just one click
        4. Your transaction is recorded on the Base blockchain and your account is upgraded instantly
        
        For help with Base wallet integration, please contact our support team.
        """)
    
    with col2:
        st.image("https://raw.githubusercontent.com/ethereum-optimism/brand-kit/main/assets/svg/Base-Symbol.svg", width=150)
        
        st.markdown("### Base Chain Explorer")
        st.markdown("[View transactions on Base Explorer](https://goerli.basescan.org/)")
        
        st.markdown("### Current Gas Prices")
        st.markdown("🟢 **Low**: 0.0001 ETH")
        st.markdown("🟡 **Medium**: 0.0002 ETH")
        st.markdown("🔴 **High**: 0.0005 ETH")

def render_payment_form():
    """Render a cryptocurrency payment form"""
    
    with st.form("crypto_payment_form"):
        st.subheader("💰 Make a Crypto Payment")
        
        payment_amount = st.number_input("Amount (ETH)", min_value=0.001, max_value=1.0, value=0.01, step=0.001)
        payment_purpose = st.selectbox("Payment Purpose", ["Pro Subscription (1 month)", "Pro Subscription (1 year)", "One-time Donation"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Network Fee")
            st.markdown("Estimated fee: 0.0001 ETH")
        
        with col2:
            st.markdown("#### Total")
            st.markdown(f"**{payment_amount + 0.0001:.4f} ETH**")
        
        st.markdown("---")
        submit_button = st.form_submit_button("Confirm Payment")
        
        if submit_button:
            if not st.session_state.get('user_authenticated', False):
                st.error("Please sign in to make a payment")
                return
                
            wallet = st.session_state.get('user_wallet', {})
            if not wallet:
                st.error("No wallet found for your account")
                return
                
            if wallet.get('balance', 0) < (payment_amount + 0.0001):
                st.error(f"Insufficient balance. You need at least {payment_amount + 0.0001:.4f} ETH")
                return
                
            # Process payment
            from wallet_integration import BaseWalletSDK
            wallet_sdk = BaseWalletSDK()
            success, result = wallet_sdk.process_payment(wallet.get('address'), payment_amount)
            
            if success:
                st.success("Payment successful!")
                st.balloons()
                
                # Update user to Pro if this was a subscription payment
                if "Pro Subscription" in payment_purpose:
                    from wallet_integration import upgrade_to_pro_with_crypto
                    upgrade_success, upgrade_message = upgrade_to_pro_with_crypto(st.session_state.user_id, 0)
                    if upgrade_success:
                        st.session_state.is_pro = True
                        st.success(upgrade_message)
                    
                # Update wallet in session state
                st.session_state.user_wallet = st.session_state.users[st.session_state.user_id]['wallet']
                st.rerun()
            else:
                st.error(f"Payment failed: {result.get('error', 'Unknown error')}")