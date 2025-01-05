from typing import List
from pydantic import BaseModel
import streamlit as st
from components.call_gpt import call_gpt, call_gpt_vision
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from io import BytesIO
import base64


# Function to render a drawing canvas for the user
def draw_canvas():
    """
    Creates a canvas component where the user can draw using different tools. 
    It returns the base64-encoded image of the drawing.
    """
    # Creating three columns for user input
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # Drawing tool selection
    with col1:
        drawing_mode = st.selectbox(
            "Drawing tool:", 
            ("point", "freedraw", "line", "rect", "circle", "transform"), 
            index=1
        )
    
    # Stroke width selection
    with col2:
        stroke_width = st.slider("Stroke width: ", 1, 25, 3)
    
    # Point display radius for 'point' drawing mode
    point_display_radius = 0
    if drawing_mode == 'point':
        point_display_radius = st.slider("Point display radius: ", 1, 25, 3)

    # Create the canvas component
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        background_color="#eee",
        update_streamlit=True,
        height=300,
        drawing_mode=drawing_mode,
        point_display_radius=point_display_radius,
        key="canvas",
    )

    # If drawing exists, convert it to base64 string and return
    if canvas_result.image_data is not None:
        # Convert the image to bytes
        buffered = BytesIO()
        img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        
        # Encode the image bytes into base64 format
        img_base64 = base64.b64encode(img_bytes).decode()
        
        return img_base64


# Function to generate a list of questions based on user's overview
def get_all_questions(overview_text: str):
    """
    Generates relevant questions for the user based on their technical stack and experience.
    Includes a series of easy, medium, and hard questions, along with a debugging question 
    and an architecture question with drawing.
    """

    class Questions(BaseModel):
        questions: List[str]
    
    # List to hold all questions
    all_questions = []

    # First set of questions related to user's tech stack and experience
    system_message = {
        "role": "system",
        "content": "You are an interviewer. You need to analyse the User's profile and ask relvent questions about their tech_stack field."
    }

    user_message = {
        "role": "user",
        "content": "Using the given overview text, ask 3 questions to the user based on the user's tech_stack and experience. Try making those question in the sequence of easy, medium, and hard. Overview:"+overview_text
    }

    all_questions.extend(call_gpt(system_message, user_message, outputStructure=Questions).questions)

    # Debugging question related to user's tech stack
    system_message = {
        "role": "system",
        "content": "Analyze the user's overview to determine their programming proficiency and generate a debugging question based on their tech stack. Create a code snippet with **exactly one intentional bug** for the user to identify and fix. The bug should be a common and easy-to-identify coding mistake in the user's tech stack. Make sure you add everything in a single string so that the question: List[str] has only one value. Do not provide any additional explanation or information in your response, just the question and code."
    }

    user_message = {
        "role": "user",
        "content": "Based on the user's overview, create a debugging question with **one intentional bug** in the code. Make sure the bug is clearly identifiable. The output should contain only a single string: the question and the code snippet. The question should ask the user to identify and fix the bug. Make sure you add everything in a single string so that the question: List[str] has only one value. User's overview: " + overview_text
    }

    all_questions.append(call_gpt(system_message, user_message, outputStructure=Questions).questions[0])

    # Architecture question related to drawing skills
    system_message = {
        "role": "system",
        "content": "Analyze the user's overview to assess their programming proficiency and generate an architecture question focused on drawing skills based on their tech stack."
    }

    user_message = {
        "role": "user",
        "content": f"Ask the user to draw a short and simple architecture question based on the user's overview tech_stack and explain it briefly. Example: 'draw and explain Linked List'. \nUser's overview: {overview_text}"
    }

    all_questions.append(call_gpt(system_message, user_message, outputStructure=Questions).questions[0])

    return all_questions


# Function to get the response for the user based on their answer
def get_response(question: str, user_answer: str, chat_length: int):
    """
    Generates the response based on user's answer. The response will either guide them further
    or move to the next question depending on whether clarification is needed.
    """
    class Response(BaseModel):
        next_question: bool
        response: str

    # If it's the 4th question, proceed to the next question without hints
    if chat_length == 4:
        system_message = {
            "role": "system",
            "content": "You are a technical interviewer. React to the user's answer briefly without hints or answers."
        }
        user_message = {
            "role": "user",
            "content": f"Question: {question}\nUser's answer: {user_answer}\nAlways set next_question to True with a brief reaction."
        }
    else:
        system_message = {
            "role": "system",
            "content": "You are a technical interviewer. React to the user's answer. Do not provide hints or answers. "
                       "Keep it short, and elaborate only if the user asks for clarification."
        }
        user_message = {
            "role": "user",
            "content": f"Question: {question}\nUser's answer: {user_answer}\nIf the user asks for clarification, elaborate "
                       f"and set next_question to False. Otherwise, set next_question to True and prompt to move to the next question."
        }

    return call_gpt(system_message, user_message, outputStructure=Response)


# Main function to handle the interview process and manage the session
def ask_questions(overview_text: str):
    """
    Manages the question flow in the interview, tracks session state, and displays user interactions
    with each question.
    """
    if "page" not in st.session_state:
        st.session_state.page = "ask_questions"

    if st.session_state.page != "ask_questions":
        st.write("Please complete the previous step before continuing.")

    if st.session_state.page == "ask_questions":
        st.title("Step 2: Brief AI Interview")

        # Initialize session variables for chat history and question flow
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            st.session_state.total_chat_history = []
            st.session_state.imagebase64 = None

        if "question_no" not in st.session_state:
            st.session_state.question_no = -1
            st.session_state.questions = []
            st.session_state.next_question = False

        # Initial page setup
        if st.session_state.question_no == -1:
            st.write("Your Overview: ", overview_text)

            # Instructions for the interview stages
            st.markdown("""<h4 style='text-align: center;'>Answer the following questions based on your resume to help us understand your skills and experience better.
                    </h4>""", unsafe_allow_html=True)

            st.markdown("""<h4 style='text-align: center;'>Interview Stages:
                    </h4>""", unsafe_allow_html=True)
            
            st.markdown("<h5 style='text-align: center;'>First 3 questions will be based on your tech stack and experience</h4>", unsafe_allow_html=True)
            st.markdown("<h5 style='text-align: center;'>Next question will be a debugging question, where you need to find the bug in the code</h4>", unsafe_allow_html=True)
            st.markdown("<h5 style='text-align: center;'>Last question will be an architecture question, where you need to draw and explain the architecture</h4>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns([5, 5, 1])
            with col2:
                if st.button("Start Interview"):
                    with st.spinner("Generating Questions..."):
                        st.session_state.questions = get_all_questions(overview_text)
                    st.session_state.update(question_no=0)
                    st.rerun()

        if st.session_state.question_no > -1:
            if st.session_state.question_no < len(st.session_state.questions):
                # Chat display logic
                if st.session_state.next_question:
                    messages = st.container(height=400)
                    with messages:
                        for role, msg in st.session_state.chat_history:
                            messages.chat_message(role).write(msg)

                    # Proceed to the next question
                    if st.button("Next Question"):
                        st.session_state.next_question = False
                        st.session_state.question_no += 1
                        st.session_state.total_chat_history.append(st.session_state.chat_history)
                        st.session_state.chat_history = []
                        st.rerun()

                else:
                    if st.session_state.question_no == len(st.session_state.questions) - 1:
                        chatcol1, chatcol2= st.columns([1, 1])
                        with chatcol1:
                            messages = st.container(height=400)
                        with chatcol2:
                            img = draw_canvas()
                            if type(img) == str:
                                st.session_state.imagebase64 = img

                    else:
                        messages = st.container(height=400)

                    # Initial question display
                    if len(st.session_state.chat_history) == 0:
                        st.session_state.chat_history.append(("assistant", st.session_state.questions[st.session_state.question_no]))

                    # User input for answer
                    if prompt := st.chat_input("Your answer...", max_chars=1000):
                        st.session_state.chat_history.append(("user", prompt))
                        with st.spinner("Generating Response..."):
                            image_analysis = ""
                            if st.session_state.question_no == len(st.session_state.questions) - 1:
                                image_analysis = "Analyze the user's drawn architecture based on the explanation provided."
                                image_analysis += call_gpt_vision(st.session_state.imagebase64, st.session_state.questions[st.session_state.question_no])

                            response = get_response(st.session_state.questions[st.session_state.question_no], image_analysis + prompt, len(st.session_state.chat_history))

                        st.session_state.chat_history.append(("assistant", f"Echo: {response.response}"))

                        # Move to the next question
                        if response.next_question:
                            st.session_state.next_question = True
                            st.rerun()

                    # Display chat history
                    with messages:
                        for role, msg in st.session_state.chat_history:
                            messages.chat_message(role).write(msg)

                        # Automatically move to the next question after 5 messages
                        if len(st.session_state.chat_history) == 5:
                            st.session_state.next_question = True
                            st.rerun()

            elif st.session_state.question_no >= len(st.session_state.questions):
                if st.button("Finish Chat"):
                    st.session_state.page = "report"
                    st.rerun()
