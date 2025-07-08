
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import cast, Any
import os
import asyncio
 
# ✅ Load environment variables
load_dotenv()
 
groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise EnvironmentError("❌ GROQ_API_KEY is missing or empty in your .env file.")
os.environ["GROQ_API_KEY"] = groq_key
 
# ✅ Function to setup the agent
async def setup_agent():
    connections = {
       "summary": {
            "url":"https://mcpserver-iwbq.onrender.com/mcp",
            "transport":"streamable_http"
        }

 
    client = MultiServerMCPClient(connections)
    tools = await client.get_tools()
    model = ChatGroq(model="qwen-qwq-32b")
    agent = create_react_agent(model, tools,prompt=f"""if mention any path in the prompt  then Summarize this meeting transcript. as follow:
        -what is objective this summary
        - What it specifies
        - Summary
        - Action Items
        - Key Decisions""")
    return agent
 
