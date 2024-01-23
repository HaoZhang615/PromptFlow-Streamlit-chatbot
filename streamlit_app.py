# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps
import streamlit as st
import urllib.request
import json

# Add the path to your local image file

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
    def clear_chat_history():
        st.session_state.messages = []
        st.session_state.chat_history = []
    if st.button("Restart Conversation :arrows_counterclockwise:"):
        clear_chat_history()


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
# iterate over the messages in the session state and display them
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)  # Render markdown with images
# create an input text box where the user can enter their prompt
if prompt := st.chat_input("type your request here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)  # Render markdown with images
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        data = {
            "chat_input": prompt,
            "chat_history": st.session_state.chat_history
        }
        body = str.encode(json.dumps(data))
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': model_name }
        req = urllib.request.Request(url, body, headers)

        response_data = urllib.request.urlopen(req).read()
        response_json = json.loads(response_data.decode('utf-8'))
        message_placeholder.markdown(response_json.get("chat_output") + "▌", unsafe_allow_html=True)  # Render markdown with images
        data["chat_history"].append(
            {
                "inputs": {
                    "chat_input": prompt
                },
                "outputs": {
                    "chat_output": response_json.get("chat_output"),
                }
            }
        )
        st.session_state.chat_history = data["chat_history"]
        message_placeholder.markdown(response_json.get("chat_output"), unsafe_allow_html=True)  # Render markdown with images
    st.session_state.messages.append({"role": "assistant", "content": response_json.get("chat_output")})
