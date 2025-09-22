import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import time
import random
import os
from pathlib import Path
import hashlib
import base64
import math
from PIL import Image
import io
import cv2
from streamlit_drawable_canvas import st_canvas
from streamlit_lottie import st_lottie
import requests

# ====================
# Utility Functions
# ====================

def load_lottieurl(url: str):
    """Load Lottie animation from URL"""
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ====================
# Page Configuration
# ====================

st.set_page_config(
    page_title="Rural EduGamify Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================
# Database Setup
# ====================

def init_db():
    conn = sqlite3.connect('edu_game.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  user_type TEXT,
                  grade INTEGER,
                  school TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Game progress table
    c.execute('''CREATE TABLE IF NOT EXISTS game_progress
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  game_name TEXT,
                  subject TEXT,
                  score INTEGER,
                  level INTEGER,
                  time_spent INTEGER,
                  completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')

    conn.commit()
    conn.close()

# Initialize database
init_db()

# ====================
# Authentication
# ====================

def create_user(username, password, user_type, grade, school):
    conn = sqlite3.connect('edu_game.db')
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password, user_type, grade, school) VALUES (?, ?, ?, ?, ?)",
                  (username, hashed_password, user_type, grade, school))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def verify_user(username, password):
    conn = sqlite3.connect('edu_game.db')
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user


# ====================
# CSS + Animations
# ====================

def local_css():
    st.markdown("""
    <style>
    /* Wiggle effect */
    @keyframes wiggle {
      0% { transform: rotate(0deg); }
      25% { transform: rotate(3deg); }
      50% { transform: rotate(-3deg); }
      75% { transform: rotate(2deg); }
      100% { transform: rotate(0deg); }
    }
    /* Glow-hover */
    .option-animated:hover {
      animation: wiggle 0.4s ease-in-out;
      box-shadow: 0 0 15px #4CAF50;
      transform: scale(1.05);
      transition: transform 0.3s, box-shadow 0.3s;
    }
    /* Fade In */
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(20px);}
        to {opacity: 1; transform: translateY(0);}
    }
    .fade-in {
        animation: fadeIn 0.8s ease-in;
    }
    /* Card Style */
    .card {
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        background-color: #f0f4f7;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Load CSS
local_css()

# ====================
# Save Game Progress
# ====================

def save_game_progress(user_id, game_name, subject, score, level, time_spent):
    conn = sqlite3.connect('edu_game.db')
    c = conn.cursor()
    c.execute("INSERT INTO game_progress (user_id, game_name, subject, score, level, time_spent) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, game_name, subject, score, level, time_spent))
    conn.commit()
    conn.close()

def get_user_progress(user_id):
    conn = sqlite3.connect('edu_game.db')
    c = conn.cursor()
    c.execute("SELECT game_name, subject, score, level, completed_at FROM game_progress WHERE user_id = ? ORDER BY completed_at DESC", (user_id,))
    progress = c.fetchall()
    conn.close()
    return progress

# ====================
# Main App
# ====================

def main():
    if 'user' not in st.session_state:
        st.session_state.user = None

    # Sidebar
    st.sidebar.title("🎓 Rural EduGamify")
    if st.session_state.user is None:
        auth_option = st.sidebar.radio("Choose:", ["Login", "Sign Up"])
        if auth_option == "Login":
            usern = st.sidebar.text_input("Username")
            passw = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                user = verify_user(usern, passw)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.sidebar.error("Invalid credentials")
        else:  # Signup
            uname = st.sidebar.text_input("New Username")
            pwd = st.sidebar.text_input("New Password", type="password")
            utype = st.sidebar.selectbox("Type", ["student", "teacher"])
            grade = st.sidebar.selectbox("Grade", list(range(6,13))) if utype == "student" else None
            school = st.sidebar.text_input("School")
            if st.sidebar.button("Register"):
                if create_user(uname, pwd, utype, grade, school):
                    st.sidebar.success("Account created. Please login.")
                else:
                    st.sidebar.error("Username taken!")

    else:
        user_id, username, _, user_type, grade, school, _ = st.session_state.user
        st.sidebar.success(f"Welcome, {username} 🙌")
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.rerun()

        menu = st.sidebar.radio("Menu", ["Dashboard", "Educational Games", "My Progress"])

        if menu == "Dashboard":
            st.title("🏠 Dashboard")
            st.write("Welcome to **Rural EduGamify** – where learning meets fun! 🎮")

            col1, col2 = st.columns(2)
            with col1:
                # Lottie Animations
                lottie_math = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_3rwasyjy.json")
                st_lottie(lottie_math, height=200, key="math_anim")
                st.markdown("<div class='card option-animated fade-in'><h3>🧮 Practice Math</h3></div>", unsafe_allow_html=True)

            with col2:
                lottie_science = load_lottieurl("https://assets7.lottiefiles.com/packages/lf20_jcikwtux.json")
                st_lottie(lottie_science, height=200, key="sci_anim")
                st.markdown("<div class='card option-animated fade-in'><h3>🔬 Explore Science</h3></div>", unsafe_allow_html=True)

        elif menu == "Educational Games":
            st.title("🎮 Games")
            st.markdown("<p class='fade-in'>Select a subject game to start!</p>", unsafe_allow_html=True)

            # Example game button with animation
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("<div class='card option-animated fade-in'>🔌 Circuit Builder</div>", unsafe_allow_html=True)
                if st.button("Play Circuit Builder"):
                    st.success("Imagine dragging and dropping components here...🔋💡")

            with col2:
                st.markdown("<div class='card option-animated fade-in'>🌍 Geography Explorer</div>", unsafe_allow_html=True)
                if st.button("Play Geography Explorer"):
                    st.success("Question: Capital of Japan? 🎌 (Tokyo!)")

            with col3:
                st.markdown("<div class='card option-animated fade-in'>🧪 Chemistry Lab</div>", unsafe_allow_html=True)
                if st.button("Play Chemistry Lab"):
                    st.success("Created Water! 💧 (H₂O)")

        elif menu == "My Progress":
            st.title("📊 My Learning Progress")
            progress = get_user_progress(user_id)
            if progress:
                df = pd.DataFrame(progress, columns=["Game", "Subject", "Score", "Level", "Date"])
                st.dataframe(df)
                st.bar_chart(df.groupby("Subject")["Score"].mean())
            else:
                st.info("No progress yet!")

if __name__ == "__main__":
    main()
