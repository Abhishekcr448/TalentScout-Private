from typing import List
from pydantic import BaseModel
import streamlit as st
from components.call_gpt import call_gpt


# Function to analyze a single conversation and provide a brief summary
def conversation_analysis(conversation: str) -> str:
    """
    Analyzes the user's conversation to provide a very small brief summary based on communication
    and technical skills. The summary is objective and concise.

    Args:
        conversation (str): The conversation to analyze.

    Returns:
        str: A brief summary based on communication and technical skills.
    """
    class Summary(BaseModel):
        summary: str

    # System message instructing the AI to analyze the conversation
    system_message = {
        "role": "system",
        "content": "Analyze the user's conversation and provide a very small brief summary on the basis of communication and technical skills objectively."
    }

    # User message containing the conversation to analyze
    user_message = {
        "role": "user",
        "content": "Analyze the following conversation. Provide a very small summary on the basis of communication and technical skills based on the content.\n\n" + conversation
    }

    # Call the GPT model to generate the summary
    return call_gpt(system_message, user_message, outputStructure=Summary).summary


# Function to provide an overall analysis based on multiple conversation summaries
def overall_analysis(conversations_analysis: List[str]):
    """
    Analyzes multiple sub-summaries (conversation analyses) and provides an overall summary.
    Also rates communication skills and technical skills, and provides key takeaways for each conversation.

    Args:
        conversations_analysis (List[str]): A list of brief summaries for each conversation.

    Returns:
        Summary: The overall summary, communication and technical skills ratings, and key takeaways.
    """
    class Summary(BaseModel):
        summary: str
        communication_skills: int
        technical_skills: int
        key_takeaways: List[str]

    # System message instructing the AI to analyze multiple sub-summaries and provide an overall summary
    system_message = {
        "role": "system",
        "content": "Analyze the following sub-summaries. Provide an overall summary with a very short list of key takeaways from all the sub-summaries. Include ratings for communication skills and technical skills based on clarity, problem-solving, and technical knowledge. Make sure the key takeaways highlight the important aspects for instant judgment of the candidate's strengths and weaknesses."
    }

    # User message containing all the sub-summaries to analyze
    user_message = {
        "role": "user",
        "content": "Provide an overall summary by analyzing the following sub-summaries. Include a very short list of points for key takeaways for instant judgment, and provide ratings for communication skills and technical skills based on clarity, problem-solving, and technical knowledge.\n\n" + "\n\n".join(conversations_analysis)
    }

    # Call the GPT model to generate the overall analysis
    return call_gpt(system_message, user_message, outputStructure=Summary)


# Function to generate and display the interview summary report
def report(total_chat_history: List[List[tuple]]):
    """
    Generates and displays the interview summary report by analyzing all conversations in the chat history.
    It includes the overall summary, key takeaways, ratings for communication and technical skills,
    and detailed conversation analysis.

    Args:
        total_chat_history (List[List[tuple]]): The complete chat history containing the conversations.
    """
    # Initialize session state for page navigation if not already set
    if "page" not in st.session_state:
        st.session_state.page = "report"

    if st.session_state.page != "report":
        st.write("Please complete the previous step before continuing.")
        return

    if st.session_state.page == "report":
        st.title("Interview Summary Report")
        all_summaries = []

        # Display spinner while analyzing conversations
        with st.spinner("Analyzing Conversations..."):
            for i, conversation in enumerate(total_chat_history):
                # Combine all messages in the conversation into a single text string
                conversation_text = ""
                for role, msg in conversation:
                    conversation_text += f"{role}: {msg}\n"
                # Analyze each conversation and store the summary
                all_summaries.append(f"Conversation {i+1}: {conversation_analysis(conversation_text)}")

            # Perform the overall analysis based on the individual conversation summaries
            overall_summary = overall_analysis(all_summaries)
            overall_summary_text = overall_summary.summary
            communication_skills = overall_summary.communication_skills
            technical_skills = overall_summary.technical_skills
            key_takeaways = overall_summary.key_takeaways

        # Display key takeaways and skill ratings
        st.subheader("Key Takeaways:")
        for takeaway in key_takeaways:
            st.write(f"- {takeaway}")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Communication Skills: {communication_skills}/10")
        with col2:
            st.write(f"Technical Skills: {technical_skills}/10")

        # Display the overall summary
        st.subheader("Overall Summary")
        st.write(overall_summary_text)

        # Display detailed conversation analysis with expandable sections
        st.subheader("Detailed Conversation Analysis:")
        for i, conversation in enumerate(total_chat_history):
            conversation_text = ""
            for role, msg in conversation:
                conversation_text += f"{role}: {msg}\n"
            with st.expander(f"Conversation {i+1} Summary: {all_summaries[i]}"):
                st.write("Conversation:")
                st.text(conversation_text)
