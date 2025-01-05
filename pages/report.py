from typing import List
from pydantic import BaseModel
import streamlit as st
from components.call_gpt import call_gpt

def conversation_analysis(conversation):
    class Summary(BaseModel):
        summary: str

    system_message = {
        "role": "system",
        "content": "Analyze the user's conversation and provide a very small brief summary on the basis of communication and technical skills objectively."
    }

    user_message = {
        "role": "user",
        "content": "Analyze the following conversation. Provide a very small summary on the basis of communication and technical skills based on the content.\n\n" + conversation
    }

    return call_gpt(system_message, user_message, outputStructure=Summary).summary

def overall_analysis(conversations_analysis):
    class Summary(BaseModel):
        summary: str
        communication_skills: int
        technical_skills: int
        key_takeaways: List[str]

    system_message = {
        "role": "system",
        "content": "Analyze the following sub-summaries. Provide an overall summary with very short list of points for key takeaways from all the sub-summaries. Include ratings for communication skills and technical skills based on clarity, problem-solving, and technical knowledge. Make sure the key takeaways highlight the important aspects for instant judgment of the candidate's strengths and weaknesses."
    }

    user_message = {
        "role": "user",
        "content": "Provide an overall summary by analyzing the following sub-summaries. Include very short list of points for key takeaways for instant judgment, and provide ratings for communication skills and technical skills based on clarity, problem-solving, and technical knowledge.\n\n" + "\n\n".join(conversations_analysis)
    }

    return call_gpt(system_message, user_message, outputStructure=Summary)

def report(total_chat_history):
    if "page" not in st.session_state:
        st.session_state.page = "report"

    if st.session_state.page != "report":
        st.write("Please complete the previous step before continuing.")

    if st.session_state.page == "report":
        st.title("Interview Summary Report")
        all_summaries = []

        with st.spinner("Analyzing Conversations..."):
            for i, conversation in enumerate(total_chat_history):
                conversation_text = ""
                for role, msg in conversation:
                    conversation_text += f"{role}: {msg}\n"
                all_summaries.append("Conversation"+str(i+1)+": "+conversation_analysis(conversation_text))

            overall_summary = overall_analysis("\n\n".join(all_summaries))
            overall_summary_text = overall_summary.summary
            communication_skills = overall_summary.communication_skills
            technical_skills = overall_summary.technical_skills
            key_takeaways = overall_summary.key_takeaways

        st.subheader("Key Takeaways:")
        for takeaway in key_takeaways:
            st.write(f"- {takeaway}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Communication Skills: {communication_skills}/10")
        with col2:
            st.write(f"Technical Skills: {technical_skills}/10")
        st.subheader("Overall Summary")
        st.write(overall_summary_text)

        st.subheader("Detailed Conversation Analysis:")
        for i, conversation in enumerate(total_chat_history):
            conversation_text = ""
            for role, msg in conversation:
                conversation_text += f"{role}: {msg}\n"
            with st.expander(f"Conversation {i+1} Summary: {all_summaries[i]}"):
                st.write("Conversation:")
                st.text(conversation_text)
