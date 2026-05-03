"""
Trovly - Authentication
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

import streamlit as st

logger = logging.getLogger("trovly.auth")


def hash_password(password):
    salt = "trovly_2026"
    return hashlib.sha256("{}:{}".format(salt, password).encode()).hexdigest()


def check_credentials(username, password):
    users_path = Path("users.json")
    if users_path.exists():
        try:
            all_users = json.loads(users_path.read_text())
            if username in all_users:
                stored_hash = all_users[username].get("password_hash", "")
                return hash_password(password) == stored_hash
        except Exception as e:
            logger.error("Error reading users.json: {}".format(e))
    return False


def register_user(username, password, email=""):
    users_path = Path("users.json")
    if users_path.exists():
        all_users = json.loads(users_path.read_text())
    else:
        all_users = {}

    if username in all_users:
        return False, "Username already exists"

    all_users[username] = {
        "password_hash": hash_password(password),
        "email": email,
        "created_at": datetime.now().isoformat(),
        "resume": "",
        "queries": [],
        "threshold": 0.55,
    }

    users_path.write_text(json.dumps(all_users, indent=2))
    return True, "Account created"


def get_user_data(username):
    users_path = Path("users.json")
    if users_path.exists():
        all_users = json.loads(users_path.read_text())
        return all_users.get(username, {})
    return {}


def save_user_data(username, data):
    users_path = Path("users.json")
    if users_path.exists():
        all_users = json.loads(users_path.read_text())
    else:
        all_users = {}

    if username in all_users:
        all_users[username].update(data)
    else:
        all_users[username] = data

    users_path.write_text(json.dumps(all_users, indent=2))


def login_page():
    if "authenticated" in st.session_state and st.session_state.authenticated:
        return st.session_state.username

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 2rem 0 1rem;'>
            <div style='width: 64px; height: 64px; margin: 0 auto 16px; background: linear-gradient(135deg, #fde047 0%, #fbbf24 30%, #f97316 65%, #ec4899 100%); border-radius: 16px; display: flex; align-items: center; justify-content: center; color: #0d1117; font-family: Outfit, sans-serif; font-weight: 700; font-size: 36px; box-shadow: 0 8px 24px rgba(251, 191, 36, 0.3);'>T</div>
            <h1 style='font-family: Outfit, sans-serif; font-weight: 700; font-size: 36px; margin: 0; background: linear-gradient(135deg, #fbbf24 0%, #ec4899 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;'>Trovly</h1>
            <p style='color:#cbd5e1; margin-top: 8px; letter-spacing: 0.05em;'>AI JOB INTELLIGENCE</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        tab_login, tab_register = st.tabs(["Log in", "Sign up"])

        with tab_login:
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")

            if st.button("Log in", type="primary", use_container_width=True):
                if check_credentials(login_user, login_pass):
                    st.session_state.authenticated = True
                    st.session_state.username = login_user
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        with tab_register:
            reg_user = st.text_input("Choose a username", key="reg_user")
            reg_email = st.text_input("Email", key="reg_email")
            reg_pass = st.text_input("Choose a password", type="password", key="reg_pass")
            reg_pass2 = st.text_input("Confirm password", type="password", key="reg_pass2")

            if st.button("Create account", type="primary", use_container_width=True):
                if not reg_user or not reg_pass:
                    st.error("Username and password are required")
                elif len(reg_pass) < 8:
                    st.error("Password must be at least 8 characters")
                elif reg_pass != reg_pass2:
                    st.error("Passwords don't match")
                else:
                    success, msg = register_user(reg_user, reg_pass, reg_email)
                    if success:
                        st.success("Account created. Log in above.")
                    else:
                        st.error(msg)

    return None


def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()
