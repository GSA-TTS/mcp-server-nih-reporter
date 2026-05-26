import asyncio
import os 
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from pprint import pprint

# Phoenix imports for standalone server
from openinference.instrumentation.langchain import LangChainInstrumentor
from phoenix.otel import register

load_dotenv()

api_key = os.getenv("USAI_API_KEY")
base_url = os.getenv("USAI_BASE_URL")

async def main():
    # Connect to standalone Phoenix server
    print("🔥 Connecting to Phoenix server...")
    tracer_provider = register(
        project_name="nih-reporter-agent",  # Name your project
        endpoint="http://localhost:4317",   # Phoenix OpenTelemetry endpoint
    )
    
    # Instrument LangChain to send traces to Phoenix
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
    print("✅ LangChain instrumentation enabled")
    print("📊 Phoenix UI: http://localhost:6006\n")
    
    print("Initializing client...")
    client = MultiServerMCPClient(
        {
            "reporter_server": {
                    "transport": "stdio",
                    "command": "uv",
                    "args": ["run", "src/reporter/app.py"],
                }
        }
    )

    print("Getting tools...")
    tools = await client.get_tools()

    print("Initializing model...")
    model = ChatOpenAI(
        model="claude_4_5_sonnet",
        base_url=base_url + "/api/v1",
        api_key=api_key,
        temperature=0,
    )

    print("Creating agent...")
    agent = create_agent(
        model=model,
        tools=tools,
    )

    config = {"configurable": {"thread_id": "1"}}

    print("Invoking agent...")
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content="How many R01s did NIMHD award in 2024?")]},
        config=config
    )

    pprint(response)
    
    print(f"\n🔍 View your traces at: http://localhost:6006")


if __name__ == "__main__":
    asyncio.run(main())