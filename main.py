import streamlit as st
from pages.ask_questions import ask_questions
from pages.extract_details import extract_details
from pages.report import report
from components.call_gpt import check_gpt
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up page configuration (no sidebar)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# if "api_key" not in st.session_state:
#     st.session_state.api_key = ""

# if "api_key_valid" not in st.session_state:
#     st.session_state.api_key_valid = False

if "api_key" not in st.session_state:
    st.session_state.api_key = OPENAI_API_KEY

if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = True

if not st.session_state.api_key_valid:
    api_key = st.text_input("Enter your GPT API Key:", type="password")
    if st.button("Submit"):
        if check_gpt(api_key):
            st.session_state.api_key = api_key
            st.session_state.api_key_valid = True
            st.rerun()
        else:
            st.error("Invalid API Key. Please try again.")
else:
    # Initialize session state if it is not set
    if "page" not in st.session_state:
        st.session_state.page = "main"  # Default to the main page

    # Define page styles
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle, rgba(230, 230, 250, 0.8) 70%, rgba(173, 216, 230, 0.5) 90%, rgba(255, 255, 255, 0.5));
        }
        /* Hide the sidebar */
        div[data-testid="stSidebar"] {
            display: none;
        }
        .center-button {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        button:hover {
            background-color: lightgreen;
        }
        button {
            border: 2px solid lightgreen;
            background-color: white;
            padding: 10px 20px;
            font-size: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display content based on session state
    if st.session_state.page == "main":
        # Main page content
        st.markdown("<h1 style='text-align: center;'>Welcome to TalentScout</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center;'>Your Gateway to Technology Placements</h2>", unsafe_allow_html=True)

        st.markdown("""          
        <div style='text-align: center; color: grey;'>
        Hello Candidate, Welcome to TalentScout, your trusted partner in technology placements. Here are the steps you need to follow:
        </div>
        <br><br>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='text-align: center;'>Step 1: Submit Your Details</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; color: grey;'>
        You can submit your details by either uploading your resume or filling out the form manually.
        </div>
        <br><br>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='text-align: center;'>Step 2: Attend a Brief AI Interview</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; color: grey;'>
        Participate in a 15-20 minute AI interview to analyze your skills in depth. This will help our recruiters gain a better understanding of your capabilities.
        </div>
        <br><br>
        """, unsafe_allow_html=True)

        # Button to go to the next page (Extract Details)
        col1, col2, col3 = st.columns([5, 5, 1])

        with col2:
            if st.button("Let's Start"):
                # Set the session state to indicate that the user is on the "extract_details" page
                st.session_state.page = "extract_details"
                st.rerun()  # Rerun to switch to the next page

    elif st.session_state.page == "extract_details":
        # Call the extract_details function when the page state is "extract_details"
        extract_details()

    elif st.session_state.page == "ask_questions":
        # Call the ask_questions function when the page state is "ask_questions"
        ask_questions(st.session_state.overview_text)

    elif st.session_state.page == "report":
        # Call the report function when the page state is "report"
        report(st.session_state.total_chat_history)