import asyncio
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from pprint import pprint

load_dotenv()

async def main():
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

    print("Creating agent...")
    agent = create_agent(
        model="gpt-5-nano",
        tools=tools,
    )

    config = {"configurable": {"thread_id": "1"}}

    print("Invoking agent...")
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content="How many R01s did NIMHD award in 2024?")]},
        config=config
    )

    pprint(response)


if __name__ == "__main__":
    asyncio.run(main())

