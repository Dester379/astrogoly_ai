# Import necessary libraries
import openai
import streamlit as st
import time

# Set your OpenAI Assistant ID here
assistant_id = 'asst_NpNdh3P1NS7FraHqPDlh54NN'

# Initialize the OpenAI client (ensure to set your API key in the sidebar within the app)
client = openai

# Set up the Streamlit page with a title and icon
st.title("Star Compatibility Chat ⭐️🔮👫")

st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")
if api_key:
    openai.api_key = api_key

if api_key!='':
    # Check if a thread exists in the session state, else create one
    if "thread_id" not in st.session_state or st.session_state.thread_id is None:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    # Initialize the model and messages list if not already in session state
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4-1106-preview"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing messages in the chat
    for message in st.session_state.messages:
        if message["role"]=='assistant':
            with st.chat_message(message["role"], avatar="🔮"):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
    # Chat input for the user
    if prompt := st.chat_input("Message"):
        # Add user message to the state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        # Process the entire conversation history
        conversation_history = "\n".join([m["content"] for m in st.session_state.messages])

        # Add the user's message to the existing thread (including full conversation history)
        user_message = client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=conversation_history
        )

        # Create a run with additional instructions
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
        )

        # Poll for the run to complete and retrieve the assistant's messages
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

        # Retrieve messages added by the assistant
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            response = message.content[0].text.value
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant", avatar="🔮"):
                st.markdown(response, unsafe_allow_html=True)
