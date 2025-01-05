from typing import List
from pydantic import BaseModel
import streamlit as st
from components.call_gpt import call_gpt, call_gpt_vision
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from io import BytesIO
import base64

def draw_canvas():
    # Create a canvas component
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        drawing_mode = st.selectbox(
            "Drawing tool:", ("point", "freedraw", "line", "rect", "circle", "transform"), index=1
        )
    with col2:
        stroke_width = st.slider("Stroke width: ", 1, 25, 3)
    
    if drawing_mode == 'point':
        point_display_radius = st.slider("Point display radius: ", 1, 25, 3)
    else:
        point_display_radius = 0

    # Create the canvas
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

    # Display the drawn image
    if canvas_result.image_data is not None:
        # Convert the image to bytes
        buffered = BytesIO()
        img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        
        # Encode the bytes to base64
        img_base64 = base64.b64encode(img_bytes).decode()
        
        return img_base64


def get_all_questions(overview_text):
    class Questions(BaseModel):
        questions: List[str]

    all_questions = []
       
    system_message = {
        "role": "system",
        "content": "You are an interviewer. You need to analyse the User's profile and ask relvent questions about their tech_stack field."
    }

    user_message = {
        "role": "user",
        "content": "Using the given overview text, ask 3 questions to the user based on the user's tech_stack and experience. Try making those question in the sequence of easy, medium, and hard. Overview:"+overview_text
    }

    all_questions.extend(call_gpt(system_message, user_message, outputStructure=Questions).questions)

    system_message = {
        "role": "system",
        "content": "Analyze the user's overview to determine their programming proficiency and generate a debugging question based on their tech stack. Include a code snippet with exactly one bug for the user to identify and fix."
    }

    user_message = {
        "role": "user",
        "content": "Based on the user's overview, create a debugging question with a code snippet containing one bug. Ask the user to identify and fix it. \nUser's overview: " + overview_text
    }

    all_questions.append(call_gpt(system_message, user_message, outputStructure=Questions).questions[0])

    system_message = {
        "role": "system",
        "content": "Analyze the user's overview to assess their programming proficiency and generate an architecture question focused on drawing skills based on their tech stack."
    }

    user_message = {
        "role": "user",
        "content": f"Ask the user to draw a short and simple architecture question based on only one easy programming concept of from the user's overview and explain it briefly. Example: 'draw and explain Linked List'. \nUser's overview: {overview_text}"
    }

    all_questions.append(call_gpt(system_message, user_message, outputStructure=Questions).questions[0])

    return all_questions

def get_response(question, user_answer, chat_length):
    class Response(BaseModel):
        next_question: bool
        response: str

    if chat_length == 4:
        system_message = {
            "role": "system",
            "content": "You are a technical interviewer. React to the user's answer without providing hints or answers. Keep it short and prompt to move to the next question."
        }
        user_message = {
            "role": "user",
            "content": f"Question: {question}\nUser's answer: {user_answer}\nAlways set next_question to True with a brief reaction."
        }
    else:
        system_message = {
            "role": "system",
            "content": "You are a technical interviewer. React to the user's answer. Do not provide answers or hints. Keep it short. Elaborate only if the user asks for clarification."
        }
        user_message = {
            "role": "user",
            "content": f"Question: {question}\nUser's answer: {user_answer}\nIf the user asks for clarification, elaborate and set next_question to False. Otherwise, set next_question to True and prompt to move to the next question with a small reaction to the user's answer."
        }

    return call_gpt(system_message, user_message, outputStructure=Response)

# Function to handle the chat interface
def ask_questions(overview_text):
    if "page" not in st.session_state:
        st.session_state.page = "ask_questions"

    if st.session_state.page != "ask_questions":
        st.write("Please complete the previous step before continuing.")

    if st.session_state.page == "ask_questions":
        # Display the title and the instruction
        st.title("Step 2: Brief AI Interview")

        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            st.session_state.total_chat_history = []
            st.session_state.imagebase64 = None

        if "question_no" not in st.session_state:
            st.session_state.question_no = -1
            st.session_state.questions = []
            st.session_state.next_question = False

        if st.session_state.question_no == -1:
            st.markdown("""<h4 style='text-align: center;'>Answer the following questions based on your resume to help us understand your skills and experience better.
                    </h4>""", unsafe_allow_html=True)
            
            # Display the overview text and start the interview
            st.write("Overview: ", overview_text)

            col1, col2, col3 = st.columns([2, 2, 1])
            with col2:
                if st.button("Start Interview"):
                    with st.spinner("Generating Questions..."):
                        st.session_state.questions = get_all_questions(overview_text)
                    st.session_state.update(question_no=0)
                    st.rerun()

        if st.session_state.question_no > -1:
            if st.session_state.question_no < len(st.session_state.questions):
                
                if st.session_state.next_question:
                    messages = st.container(height=400)
                    with messages:
                        for role, msg in st.session_state.chat_history:
                            messages.chat_message(role).write(msg)
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

                    if len(st.session_state.chat_history) == 0:
                        st.session_state.chat_history.append(("assistant", st.session_state.questions[st.session_state.question_no]))

                    if prompt := st.chat_input("Your answer...", max_chars=1000):
                        st.session_state.chat_history.append(("user", prompt))
                        with st.spinner("Generating Response..."):

                            image_analysis = ""
                            if st.session_state.question_no == len(st.session_state.questions) - 1:
                                image_analysis = "Here is the explaination of the user's drawn architechture, analyse it with the user's explanation and compare it with the asked question. If the user's architecture is not good or if improvement required, then mention it."+call_gpt_vision(st.session_state.imagebase64, st.session_state.questions[st.session_state.question_no])
                            response = get_response(st.session_state.questions[st.session_state.question_no], image_analysis + prompt, len(st.session_state.chat_history))

                        st.session_state.chat_history.append(("assistant", f"Echo: {response.response}"))    

                        if response.next_question:
                            st.session_state.next_question = True
                            st.rerun()
                    
                    with messages:
                        for role, msg in st.session_state.chat_history:
                            messages.chat_message(role).write(msg)
                        if len(st.session_state.chat_history) == 5:
                            st.session_state.next_question = True
                            st.rerun()

            elif st.session_state.question_no >= len(st.session_state.questions):
                if st.button("Finish Chat"):
                    st.session_state.page = "report"
                    st.rerun()

