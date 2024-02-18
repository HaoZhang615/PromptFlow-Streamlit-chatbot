# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps
import streamlit as st
import requests
import json
import base64
import mimetypes

st.set_page_config(
    page_title="Chatbot powered by Prompt Flow",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    # input box for user to enter their PromptFlow endpoint
    if 'PROMPT_FLOW_ENDPOINT' in st.secrets:
        st.success('PromptFlow endpoint already provided!', icon='✅')
        url = st.secrets['PROMPT_FLOW_ENDPOINT']
    else:
        url = st.text_input('Enter PromptFlow endpoint:', type='password')

    # input box for user to enter their PromptFlow key
    if 'PROMPT_FLOW_KEY' in st.secrets:
        st.success('PromptFlow key already provided!', icon='✅')
        api_key = st.secrets['PROMPT_FLOW_KEY']
    else:
        api_key = st.text_input('Enter PromptFlow key:', type='password')

    # input box for user to enter their PromptFlow model name
    if 'PROMPT_FLOW_MODEL_NAME' in st.secrets:
        st.success('PromptFlow model name already provided!', icon='✅')
        model_name = st.secrets['PROMPT_FLOW_MODEL_NAME']
    else:
        model_name = st.text_input('Enter PromptFlow model name:')

    # input box for user to enter their key name of chat_input in PromptFlow
    if 'PROMPT_FLOW_CHAT_INPUT_KEY_NAME' in st.secrets:
        st.success('PromptFlow chat_input key name already provided!', icon='✅')
        chat_input_key_name = st.secrets['PROMPT_FLOW_CHAT_INPUT_KEY_NAME']
    else:
        chat_input_key_name = st.text_input('Enter your chat_input key name: e.g. chat_input or question')

    # input box for user to enter their key name of chat_history in PromptFlow
    if 'PROMPT_FLOW_CHAT_HISTORY_KEY_NAME' in st.secrets:
        st.success('PromptFlow chat_history key name already provided!', icon='✅')
        chat_history_key_name = st.secrets['PROMPT_FLOW_CHAT_HISTORY_KEY_NAME']
    else:
        chat_history_key_name = st.text_input('Enter PromptFlow chat_history key name: e.g. chat_history or history')

    # input box for user to enter their key name of chat_output in PromptFlow
    if 'PROMPT_FLOW_CHAT_OUTPUT_KEY_NAME' in st.secrets:
        st.success('PromptFlow model chat_output key name already provided!', icon='✅')
        chat_output_key_name = st.secrets['PROMPT_FLOW_CHAT_OUTPUT_KEY_NAME']
    else:
        chat_output_key_name = st.text_input('Enter PromptFlow chat_output key name: e.g. chat_output or response')


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

# create a container with fixed height and scroll bar for conversation history
conversation_container = st.container(height = 600, border=False)

# create an input text box where the user can enter their prompt
if text_prompt := st.chat_input("type your request here..."):
    with conversation_container:
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

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            if uploaded_file:
                data = {
                    chat_input_key_name: [text_prompt,mime_variable],
                    chat_history_key_name: st.session_state.chat_history
                }
            else:
                data = {
                    chat_input_key_name: [text_prompt],
                    chat_history_key_name: st.session_state.chat_history
                }
            body = json.dumps(data)
            headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': model_name }
            response = requests.post(url, data=body, headers=headers,stream=True)
            response_json = response.json()
            message_placeholder.markdown(response_json.get(chat_output_key_name))  # Render markdown with images
        if uploaded_file:
            data[chat_history_key_name].append(
                {
                    "inputs": {
                        chat_input_key_name: [text_prompt,mime_variable]
                    },
                    "outputs": {
                        chat_output_key_name: response_json.get(chat_output_key_name),
                    }
                }
            )

        else:
            data[chat_history_key_name].append(
                {
                    "inputs": {
                        chat_input_key_name: [text_prompt]
                    },
                    "outputs": {
                        chat_output_key_name: response_json.get(chat_output_key_name),
                    }
                }
            )
        st.session_state.chat_history = data[chat_history_key_name]

    st.session_state.messages.append({"role": "assistant", "content": response_json.get(chat_output_key_name)})



