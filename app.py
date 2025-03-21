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

# print(f'curl {BASE_URL} -H "Authorization: Bearer {API_KEY}"')

from client import Client

CLIENT = Client(base_url=BASE_URL, api_key=API_KEY)

ROLE2AVATAR = {
    "assistant": "🦖",
    "user": "🧑‍💻",
}


def new_chat():
    CLIENT.clear_messages()
    CLIENT.post_message(role="assistant", content="How can I help you?")


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

    model = st.selectbox(
        "Model",
        [
            "deepseek-ai/deepseek-r1",
            "deepseek-ai/deepseek-v3",
            "google/gemini-2.0-pro-exp-02-05",
            "google/gemini-2.0-flash-exp",
        ],
        index=0,
        help="Select a model for chat",
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

    # TODO: Support loading default tools
    tools = ["", ""]

    custom = st.toggle(
        "Custom mode",
        help="Enable Custom mode to customize the model parameters",
        disabled=False,
    )

    if custom:
        st.divider()

        st.subheader("Tools")

        tools = st.multiselect(
            "Tools",
            [
                "",
                "",
                "",
                "",
            ],
            default=tools,
            help="Select tools used for the MRKL system",
        )

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
    "Welcome to our AI platform 🪄 ✨!",
    icon="🧙‍♂️",
)

# col1, col2, col3 = st.columns(3)
# with col1:
#     st.info(
#         "How could I update personal information in my account, especially about name change?",
#         icon="💡",
#     )

# with col2:
#     st.info(
#         "What is the most commonly used language in recorded customer calls?",
#         icon="💭",
#     )

# with col3:
#     st.info(
#         "Summarize customer needs or purposes of calling in recorded customer calls.",
#         icon="📌",
#     )

# Chat elements

messages = CLIENT.get_messages()
for message in messages:
    st.chat_message(message["role"], avatar=ROLE2AVATAR[message["role"]]).write(
        message["content"]
    )

if len(messages) % 2 == 1:
    with st.chat_message("user", avatar=ROLE2AVATAR["user"]):
        with st.spinner("Typing ..."):
            # long polling
            query = None
            while query is None:
                messages = CLIENT.get_messages()
                if messages and messages[-1]["role"] == "user":
                    query = messages[-1]["content"]
                time.sleep(1)  # idle to avoid overwhelming the server
        if query is not None:
            st.write(query)

if response := st.chat_input():
    # if not api_key:
    #     st.warning(
    #         "Please enter your OpenRouter API key to continue",
    #         icon="⚠️",
    #     )
    #     st.stop()

    with st.chat_message("assistant", avatar=ROLE2AVATAR["assistant"]):
        CLIENT.post_message(role="assistant", content=response)
        st.write(response)
