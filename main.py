
import streamlit as st
import asyncio
import tempfile
from dotenv import load_dotenv
from client import setup_agent
import pyautogui # your refactored client.py

load_dotenv()

st.set_page_config(page_title="MCP Agent Chat", page_icon="🤖")
st.title(" Meeting Summary Agent (via LLM + MCP Tools)")


# 1. Clear chat history button

if st.button("Clear history"):
    st.session_state.chat_history = []
    pyautogui.press("f5")
    st.rerun() 


# 2. Initialise / restore chat history
#    Format required by chat-ML models: list of {"role", "content"}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []      # empty list on first run


# 3. File-uploader (audio / video for meeting summarisation)

uploaded_file = st.file_uploader(
    "Choose an audio or video file",
    type=["mp3", "wav", "ogg", "m4a", "mp4", "avi", "mov"]
)
u_path: str = ""

def save_uploaded_file(file_obj) -> str | None:
    """Save the uploaded file to a temporary path and return that path."""
    try:
        suffix = "." + file_obj.name.split(".")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_obj.getvalue())
            return tmp.name
    except Exception as exc:
        st.error(f"Failed to save file: {exc}")
        return None

if uploaded_file:
    u_path = save_uploaded_file(uploaded_file) or ""

# 4. Display previous chat turns

for msg in st.session_state.chat_history:
    align  = "right" if msg["role"] == "user" else "left"
    avatar = "🧑"   if msg["role"] == "user" else "🤖"
    st.markdown(
        f"""
        <div style="text-align:{align};
                    padding:10px 15px;
                    margin:10px;
                    border-radius:10px;
                    max-width:80%;
                    float:{align};
                    clear:both;">
            {avatar} {msg["content"]}
        </div>
        """,
        unsafe_allow_html=True
    )


# 5. Chat input box

user_input = st.chat_input("Enter your question")

# 6. Core helper – send *full* history to the MCP agent
async def call_agent(full_history: list[dict]) -> str:
    agent = await setup_agent()                   # (re)create the agent
    response = await agent.ainvoke({"messages": full_history})
    return response["messages"][-1].content       # last assistant turn


# 7. Handle a new user message or uploaded file request
# 
if user_input or u_path:
    # text query OR “summarise this file” prompt
    new_user_msg = user_input if user_input else f"get the summary of {u_path}"

    with st.spinner("Thinking…"):
        # build context = previous turns + this new user message
        context = st.session_state.chat_history + [{"role": "user", "content": new_user_msg}]
        try:
            assistant_reply = asyncio.run(call_agent(context))
        except Exception as e:
            assistant_reply = f"Sorry, something went wrong: {e}"

        # persist the new turn
        st.session_state.chat_history.extend([
            {"role": "user",      "content": new_user_msg},
            {"role": "assistant", "content": assistant_reply},
        ])

        # render assistant reply
        st.success("Agent's Response:")
        st.write(assistant_reply)

