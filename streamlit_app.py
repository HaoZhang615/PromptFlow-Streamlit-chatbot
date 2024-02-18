# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps
import streamlit as st
import requests

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


col1, col2, col3 = st.columns([1, 100, 1])

# Add an empty column on either side of the image column to center it
with col1:
    st.write("")
with col2:
    st.title('Chatbot powered by PromptFlow') 
with col3:
    st.write("")




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
        st.session_state.messages.append({"role": "user", "content": text_prompt})
        # iterate over the messages in the session state and display them
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])  # Render markdown with images
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            data = {
                chat_input_key_name: text_prompt,
                chat_history_key_name: st.session_state.chat_history
            }
            headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': model_name}
            response = requests.post(url, json=data, headers=headers, stream=True)

            response_json = response.json()
            message_placeholder.markdown(response_json.get(chat_output_key_name), unsafe_allow_html=True)  # Render markdown with images
            data[chat_history_key_name].append(
                {
                    "inputs": {
                        chat_input_key_name: text_prompt
                    },
                    "outputs": {
                        chat_output_key_name: response_json.get(chat_output_key_name),
                    }
                }
            )
            st.session_state.chat_history = data[chat_history_key_name]
            message_placeholder.markdown(response_json.get(chat_output_key_name), unsafe_allow_html=True)  # Render markdown with images
        st.session_state.messages.append({"role": "assistant", "content": response_json.get(chat_output_key_name)})
