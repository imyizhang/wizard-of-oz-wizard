import json
import os
import time

import streamlit as st

# import dotenv

# dotenv.load_dotenv()
# print("WARNING: Using environment variables in development mode")


BASE_URL = os.getenv("CLIENT_BASE_URL")
API_KEY = os.getenv("CLIENT_API_KEY")

if not BASE_URL or not API_KEY:
    BASE_URL = "http://localhost:8000"
    API_KEY = "API_KEY"
    print("WARNING: Using API key in development mode")

# example curl command
# print(f'curl {BASE_URL} -H "Authorization: Bearer {API_KEY}"')

from client import Client

CLIENT = Client(base_url=BASE_URL, api_key=API_KEY)

ASSISTANT = "assistant"
USER = "user"

ROLE2AVATAR = {
    ASSISTANT: "🦖",
    USER: "🧑‍💻",
}

START = "<s>"
END = "</s>"

SYMBOL2CONTENT = {
    START: "How can I help you today?",
    END: "Thank you for choosing our service! Your feedback matters, please take a moment to rate your experience.",
}


def new_chat():
    CLIENT.clear_messages()
    CLIENT.post_message(role=ASSISTANT, content=START)


# Page settings

st.set_page_config(
    page_title="Wizard of Oz",
    page_icon="🧙‍♂️",
    layout="centered",
    initial_sidebar_state="auto",
)

# Sidebar elements

with st.sidebar:
    st.sidebar.button(
        "New chat",
        on_click=new_chat,
        help="Clear chat history and start a new chat",
        disabled=False,
    )

    st.header("Settings")

    # api_key = st.text_input(
    #     "OpenRouter API key",
    #     key="api_key",
    #     type="password",
    #     placeholder="Enter your API key",
    #     help="[Get your OpenRouter API key](https://openrouter.ai)",
    # )

    # TODO: Support loading default model
    model = st.selectbox(
        "Model",
        [
            "deepseek/deepseek-r1",
            "google/gemini-2.0-flash-exp",
        ],
        index=0,
        help="Select a model for chat",
        disabled=True,
    )

    # TODO: Support loading default tools
    tools = st.multiselect(
        "Tools",
        [
            "Deep Research",
            "Web Search",
            "Computer Use",
        ],
        default=["Web Search"],
        help="Select tools for the multi-agent system (MAS)",
        disabled=True,
    )

    # TODO: Support loading default model parameters
    if model:
        sampling = True
        temperature = 0.6
        top_p = 0.9
        top_k = 50
        random_seed = 0
        repetition_penalty = 1.0
        min_new_tokens = 0
        max_new_tokens = 1024

    custom = st.toggle(
        "Custom mode",
        help="Enable Custom mode to customize the model parameters",
        disabled=False,
    )

    if custom:
        st.divider()

        st.subheader("Model parameters")

        sampling = st.toggle(
            "Sampling decoding",
            value=sampling,
            help="Enable Sampling decoding to customize the variability in how tokens are selected",
        )

        if sampling:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=temperature,
                help="Higher values lead to greater variability",
            )  # float

            top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=top_p,
                help="Unless you change the value, this setting is not used",
            )  # float

            top_k = st.slider(
                "Top K",
                min_value=0,
                max_value=100,
                value=top_k,
                help="Higher values lead to greater variability",
            )  # int

            random_seed = st.number_input(
                "Random seed",
                min_value=0,
                max_value=4294967295,
                value=random_seed,
                help="To produce repeatable results, set the same random seed value every time; to disable reproducibility, set to 0",
            )  # int

        repetition_penalty = st.slider(
            "Repetition penalty",
            min_value=1.0,
            max_value=2.0,
            value=repetition_penalty,
            help="The higher the penalty, the less likely it is that the result will include repeated text",
        )  # float

        min_new_tokens = st.number_input(
            "Min tokens",
            min_value=0,
            value=min_new_tokens,
            help="Control the maximum number of tokens in the generated tokens, which must be less than or equal to Max tokens",
        )  # int

        # TODO: The maximum number of tokens that are allowed in the output differs by model
        max_new_tokens = st.number_input(
            "Max tokens",
            min_value=min_new_tokens,
            max_value=16384,
            value=max_new_tokens,
            help="Control the maximum number of tokens in the generated tokens",
        )  # int

    "[Learn more](https://openrouter.ai)"

# Title elements

st.title("💬 Chat")
st.caption("Powered by OpenRouter")

# Info elements

st.info(
    "Welcome to our AI system! Meet your personal travel agent 🪄 ✨!",
    icon="🧙‍♂️",
)

# Chat elements

messages = CLIENT.get_messages()
for index, message in enumerate(messages):
    role = message.get("role")
    content = message.get("content")
    with st.chat_message(role, avatar=ROLE2AVATAR[role]):
        if role == ASSISTANT:
            # write reasoning
            reasoning = message.get("reasoning")
            if reasoning is not None:
                with st.status("Thoughts", state="complete") as status:
                    st.write(reasoning)
            # write content
            if content == START:
                st.write(SYMBOL2CONTENT[START])
            elif content == END:
                st.write(SYMBOL2CONTENT[END])
            else:
                st.write(content)
            # write feedback
            feedback = message.get("feedback")
            st.session_state[f"feedback_{index}"] = feedback
            if content == START:
                pass
            elif content == END:
                st.feedback("stars", key=f"feedback_{index}", disabled=True)
            else:
                st.feedback("thumbs", key=f"feedback_{index}", disabled=True)
        elif role == USER:
            # write files
            files = message.get("files")
            if files:
                with st.status("Files", state="complete") as status:
                    for file in files:
                        st.write(f"📄 {file}")
            # write content
            st.write(content)
        else:
            print(f"ERROR: Unexpected role '{role}'")

if messages and messages[-1].get("role") == ASSISTANT:
    with st.chat_message(USER, avatar=ROLE2AVATAR[USER]):
        with st.spinner("Typing ..."):
            # query = "..."

            # communicate with the server using long polling
            query = None
            while query is None:
                messages = CLIENT.get_messages()
                if messages and messages[-1].get("role") == USER:
                    query = messages[-1]
                time.sleep(1)  # idle to avoid overwhelming the server

        if query is not None:
            # st.write(query)

            content = query.get("content")
            # write files
            files = query.get("files")
            if files:
                with st.status("Files", state="complete") as status:
                    for file in files:
                        st.write(f"📄 {file}")
            # write content
            st.write(content)

if response := st.chat_input():
    # if not api_key:
    #     st.warning(
    #         "Please enter your OpenRouter API key to continue",
    #         icon="⚠️",
    #     )
    #     st.stop()

    with st.chat_message(ASSISTANT, avatar=ROLE2AVATAR[ASSISTANT]):
        # st.write(response)

        # parse response
        response = json.loads(response)
        content = response.get("content")
        reasoning = response.get("reasoning")
        feedback = response.get("feedback")
        # write reasoning
        if reasoning is not None:
            with st.status("Thinking...", expanded=True) as status:
                st.write(reasoning)
                status.update(
                    label="Thoughts", state="complete", expanded=False
                )
        # write content
        st.write(content)
        # write feedback
        if content == START:
            print("ERROR: Unexpected content")
        elif content == END:
            st.feedback("stars", key=f"feedback_{index}", disabled=True)
        else:
            st.feedback("thumbs", key=f"feedback_{index}", disabled=True)
        # send message to the server
        print(f'INFO: Sending message to the server\n"{response}"')
        CLIENT.post_message(
            role=ASSISTANT, content=content, reasoning=reasoning
        )
