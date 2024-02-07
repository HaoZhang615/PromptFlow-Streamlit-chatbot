# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps
import streamlit as st
import requests
import json
import base64
import mimetypes

with st.sidebar:
    # input box for user to enter their PromptFlow endpoint
    if 'PROMPT_FLOW_ENDPOINT' in st.secrets:
        st.success('PromptFlow endpoint already provided!', icon='✅')
        url = st.secrets['PROMPT_FLOW_ENDPOINT']
    else:
        url = st.text_input('Enter PromptFlow endpoint:', type='password')
        if url:
            st.success('Proceed to entering your PromptFlow endpoint key!', icon='👉')
    # input box for user to enter their PromptFlow key
    if 'PROMPT_FLOW_KEY' in st.secrets:
        st.success('PromptFlow key already provided!', icon='✅')
        api_key = st.secrets['PROMPT_FLOW_KEY']
    else:
        api_key = st.text_input('Enter PromptFlow key:', type='password')
        if api_key:
            st.success('Proceed to entering your PromptFlow model name!', icon='👉')
    # input box for user to enter their PromptFlow model name
    if 'PROMPT_FLOW_MODEL_NAME' in st.secrets:
        st.success('PromptFlow model name already provided!', icon='✅')
        model_name = st.secrets['PROMPT_FLOW_MODEL_NAME']
    else:
        model_name = st.text_input('Enter PromptFlow model name:')
        if model_name:
            st.success('You can start chatting now!', icon='👉')

    # File uploader allows user to add their own image
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
    if uploaded_file:
    # Display the uploaded image
        with st.expander("Image", expanded = True):
            st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
    
    # Button to clear chat history
    def clear_chat_history():
        st.session_state.messages = []
        st.session_state.chat_history = []
    if st.button("Restart Conversation :arrows_counterclockwise:"):
        clear_chat_history()


st.title('Chatbot powered by Prompt Flow')  # Add your title

# check if the "messages" session state exists, if not, create it as an empty list
if "messages" not in st.session_state:
    st.session_state.messages = []
# check if the "chat_history" session state exists, if not, create it as an empty list
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
# iterate over the messages in the session state and display them
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user" and len(message["content"]) > 1:
            text_prompt = message["content"][0]
            image_input = message["content"][1]
            st.markdown(text_prompt)
            st.image(image_input, caption="User Image", use_column_width=True)
        elif message["role"] == "user" and len(message["content"]) == 1:
            text_prompt = message["content"][0]
            st.markdown(text_prompt)
        else:
            st.markdown(message["content"]) 
# create an input text box where the user can enter their prompt
if text_prompt := st.chat_input("type your request here..."):
    if uploaded_file:
        # Read the content of the file as bytes
        image_bytes = uploaded_file.getvalue()
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        # Create MIME type variable
        mime_variable = {"data:{};base64".format(mime_type): base64.b64encode(image_bytes).decode()}
        st.session_state.messages.append({"role": "user", "content": [text_prompt,uploaded_file]}) 
    else:
        st.session_state.messages.append({"role": "user", "content": [text_prompt]})
    with st.chat_message("user"):
        st.markdown(text_prompt)
        if uploaded_file:
            st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        if uploaded_file:
            data = {
                "chat_input": [text_prompt,mime_variable],
                "chat_history": st.session_state.chat_history
            }
        else:
            data = {
                "chat_input": [text_prompt],
                "chat_history": st.session_state.chat_history
            }
        body = json.dumps(data)
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': model_name }
        response = requests.post(url, data=body, headers=headers)
        response_json = response.json()
        message_placeholder.markdown(response_json.get("chat_output"))  # Render markdown with images
        if uploaded_file:
            data["chat_history"].append(
                {
                    "inputs": {
                        "chat_input": [text_prompt,mime_variable]
                    },
                    "outputs": {
                        "chat_output": response_json.get("chat_output"),
                    }
                }
            )

        else:
            data["chat_history"].append(
                {
                    "inputs": {
                        "chat_input": [text_prompt]
                    },
                    "outputs": {
                        "chat_output": response_json.get("chat_output"),
                    }
                }
            )
        st.session_state.chat_history = data["chat_history"]
        # st.write(st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response_json.get("chat_output")})
