import streamlit as st
from openai import OpenAI
import PyPDF2
from pydantic import BaseModel
from components.call_gpt import call_gpt
from pages.ask_questions import ask_questions


# Function to extract text from the uploaded PDF
def extract_text_from_pdf(pdf_file):
    """
    Extracts text content from the given PDF file.
    Args:
        pdf_file: The uploaded PDF file from which text is to be extracted.
    Returns:
        A string containing the extracted text from all the pages of the PDF.
    """
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text


# Function to analyze resume details using OpenAI API
def analyse_resume_details(resume_text):
    """
    Analyzes the resume text using the OpenAI API to extract key details.
    Args:
        resume_text: The full resume text extracted from the uploaded PDF.
    Returns:
        A dictionary containing key details extracted from the resume (full name, email, phone, etc.).
    """
    class ResumeAnalysis(BaseModel):
        is_resume: bool
        full_name: str
        email_address: str
        phone_number: str
        years_of_experience: str
        desired_position: str
        current_location: str
        tech_stack: str
        other_details: str

    system_message = {
        "role": "system",
        "content": "Determine if the input is a resume ('is_resume': True/False). Extract details: full name, email, phone, experience, position, location, tech stack, and other relevant info. Use 'None' for missing fields."
    }

    user_message = {
        "role": "user",
        "content": resume_text
    }

    resume_info = call_gpt(system_message, user_message, outputStructure=ResumeAnalysis)

    resume_dict = {
        "full_name": resume_info.full_name,
        "email_address": resume_info.email_address,
        "phone_number": resume_info.phone_number,
        "years_of_experience": resume_info.years_of_experience,
        "desired_position": resume_info.desired_position,
        "current_location": resume_info.current_location,
        "tech_stack": resume_info.tech_stack,
        "other_details": resume_info.other_details
    }
    return resume_dict


# Function to create a concise overview from the resume details
def create_overview(resume_dict):
    """
    Creates a concise overview of the candidate based on the extracted resume details.
    Args:
        resume_dict: A dictionary containing the extracted details from the resume.
    Returns:
        An object containing the overview text summarizing the candidate's profile.
    """
    class Overview(BaseModel):
        overview: str

    system_message = {
        "role": "system",
        "content": "Create a concise overview of the candidate's details using the provided resume information."
    }

    user_message = {
        "role": "user",
        "content": str(resume_dict)
    }

    return call_gpt(system_message, user_message, outputStructure=Overview)


# Function to handle the extraction of details from resume or manual form submission
def extract_details():
    """
    Handles the user interaction for submitting their resume or filling out the form manually.
    Guides the user through uploading their resume, extracting the details, and submitting the form.
    """
    # Initialize session state if it is not set
    overview_text = ""

    if "page" not in st.session_state:
        st.session_state.page = "extract_details"  # Default page

    # Page content for resume extraction or manual form input
    if st.session_state.page == "extract_details":
        st.title("Step 1: Submit Your Details")

        st.markdown("""          
        <br><br>
        <h3 style='text-align: center;'>Upload your resume to let AI extract your details automatically
        """, unsafe_allow_html=True)

        # Upload resume PDF
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

        if uploaded_file is not None:
            # Display loading spinner while analyzing resume
            with st.spinner("Analyzing... This may take a moment."):
                resume_text = extract_text_from_pdf(uploaded_file)

                # Handle case when resume text is too short or too long
                if len(resume_text) < 100:
                    st.error("The uploaded file does not contain enough text to be a valid resume. Please upload a different file.")
                elif len(resume_text) > 10000:
                    st.error("The uploaded file contains too much text to be processed. Please upload a shorter resume.")
                else:
                    # Proceed with analyzing the extracted resume details
                    resume_dict = analyse_resume_details(resume_text)

                    # Show success message after successful analysis
                    st.success("Analysis complete!")
                    
                    # Collect candidate details for display in form
                    full_name = resume_dict["full_name"]
                    email_address = resume_dict["email_address"]
                    phone_number = resume_dict["phone_number"]
                    years_of_experience = resume_dict["years_of_experience"]
                    desired_position = resume_dict["desired_position"]
                    current_location = resume_dict["current_location"]
                    tech_stack = resume_dict["tech_stack"]
                    other_details = resume_dict["other_details"]

                    # Create a form layout to collect further details
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        full_name = st.text_input("Full Name", value=full_name)
                    with col2:
                        email_address = st.text_input("Email Address", value=email_address)
                    with col3:
                        phone_number = st.text_input("Phone Number", value=phone_number)

                    col4, col5 = st.columns([5, 1])
                    with col4:
                        desired_position = st.text_input("Desired Position(s) (comma separated)", value=desired_position)
                    with col5:
                        years_of_experience = st.text_input("Years of Experience", value=years_of_experience)

                    current_location = st.text_input("Current Location", value=current_location)

                    tech_stack = st.text_area("Tech Stack", value=tech_stack)
                    other_details = st.text_area("Other Details", value=other_details)

        else:
            st.markdown("""          
            <br><br>
            <h3 style='text-align: center;'>OR
            </h3>
            <h3 style='text-align: center;'>Fill out the form manually
            </h3>
            """, unsafe_allow_html=True)

            # Manual form for candidate details
            col1, col2, col3 = st.columns(3)
            with col1:
                full_name = st.text_input("Full Name", value="")
            with col2:
                email_address = st.text_input("Email Address", value="")
            with col3:
                phone_number = st.text_input("Phone Number", value="")

            col4, col5 = st.columns([5, 1])
            with col4:
                desired_position = st.text_input("Desired Position(s) (comma separated)", value="")
            with col5:
                years_of_experience = st.text_input("Years of Experience", value="")

            current_location = st.text_input("Current Location", value="")

            tech_stack = st.text_area("Tech Stack", value="")
            other_details = st.text_area("Other Details", value="")

        # Submit button logic
        if st.button("Submit", key="submit_button"):
            if all([full_name.strip(), email_address.strip(), phone_number.strip(), years_of_experience.strip(), desired_position.strip(), current_location.strip(), tech_stack.strip(), other_details.strip()]):
                with st.spinner("Creating Short Overview of your details..."):
                    resume_dict = {
                        "full_name": full_name,
                        "email_address": email_address,
                        "phone_number": phone_number,
                        "years_of_experience": years_of_experience,
                        "desired_position": desired_position,
                        "current_location": current_location,
                        "tech_stack": tech_stack,
                        "other_details": other_details
                    }
                    overview_text = create_overview(resume_dict)
                
                # After submission, store overview in session and rerun to navigate to the next page
                st.session_state.page = "ask_questions"  # Redirect to next step
                st.session_state.overview_text = overview_text.overview  # Store the overview text in session state
                st.rerun()  # Rerun to switch pages
            else:
                st.error("Please fill out all fields before submitting.")
