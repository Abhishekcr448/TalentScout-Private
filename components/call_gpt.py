from openai import OpenAI
import streamlit as st

def call_gpt(system_message, user_message, outputStructure):
    # print("API Key: ", (st.session_state.api_key).strip())
    client = OpenAI(api_key=st.session_state.api_key)

    # Send the request to OpenAI API using chat completion
    completion = client.beta.chat.completions.parse(
        model = "gpt-4o-mini",
        messages = [system_message, user_message],
        response_format = outputStructure
    )

    # Parse the response and extract details as a dictionary
    return completion.choices[0].message.parsed

def check_gpt(OPENAI_API_KEY):

    st.session_state.api_key = OPENAI_API_KEY
    
    if OPENAI_API_KEY == "":
        return False

    def mini_call_gpt(system_message, user_message):
        client = OpenAI(api_key=st.session_state.api_key)

        try:
            # Send the request to OpenAI API using chat completion
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[system_message, user_message],
            )
            # If the request is successful, return True
            return True
        except Exception as e:
            # If there is an error, print the error and return False
            print(f"Error: {e}")
            return False
        
    try:
        if mini_call_gpt({"role": "system", "content": "Test"}, {"role": "user", "content": "Test"}):
            return True
    except Exception as e:
        st.error(f"Error calling GPT: {e}")
        return False
    
def call_gpt_vision(base64_image, question):
    client = OpenAI(api_key=st.session_state.api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "As an Interviewer, analyse the architecture drawn in the image and explain the image. Do not add your own explaination. Stick to what the user has drawn. If the user has drawn nothing or bad in knowledge, mention it. Questions: "+ question,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )

    return response.choices[0].message.content