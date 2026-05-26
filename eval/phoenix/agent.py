import asyncio
import os 
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

# Phoenix imports for standalone server
from openinference.instrumentation.langchain import LangChainInstrumentor
from phoenix.otel import register

load_dotenv()

api_key = os.getenv("USAI_API_KEY")
base_url = os.getenv("USAI_BASE_URL")

class NIHReporterAgent:
    """Reusable NIH Reporter Agent for Phoenix experiments"""
    
    def __init__(self, project_name="nih-reporter-agent", phoenix_endpoint="http://localhost:4317"):
        self.api_key = api_key
        self.base_url = base_url
        self.project_name = project_name
        self.phoenix_endpoint = phoenix_endpoint
        self.agent = None
        self.client = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize the agent with Phoenix instrumentation"""
        if self._initialized:
            return
            
        # Connect to standalone Phoenix server
        print("🔥 Connecting to Phoenix server...")
        tracer_provider = register(
            project_name=self.project_name,
            endpoint=self.phoenix_endpoint,
        )
        
        # Instrument LangChain to send traces to Phoenix
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
        print("✅ LangChain instrumentation enabled")
        print(f"📊 Phoenix UI: http://localhost:6006\n")
        
        print("Initializing MCP client...")
        self.client = MultiServerMCPClient(
            {
                "reporter_server": {
                    "transport": "stdio",
                    "command": "uv",
                    "args": ["run", "src/reporter/app.py"],
                }
            }
        )

        print("Getting tools...")
        tools = await self.client.get_tools()

        print("Initializing model...")
        model = ChatOpenAI(
            model="claude_4_5_sonnet",
            base_url=self.base_url + "/api/v1",
            api_key=self.api_key,
            temperature=0,
        )

        print("Creating agent...")
        self.agent = create_agent(
            model=model,
            tools=tools,
            system_prompt="""You are an expert NIH research funding analyst with access to the NIH Reporter database.

Your role is to:
- Provide accurate information about NIH grants, projects, and funding
- Use the available tools to query the NIH Reporter API
- Present data in a clear, structured format
- Cite specific grant numbers and funding amounts when relevant
- Help users understand NIH funding trends and patterns

Always verify your data using the tools before responding."""
        )
        
        self._initialized = True
        print("✅ Agent initialized and ready\n")
    
    async def run(self, query: str) -> str:
        """Run a query through the agent and return the response"""
        if not self._initialized:
            await self.initialize()
        
        config = {"configurable": {"thread_id": "1"}}
        
        response = await self.agent.ainvoke(
            {"messages": [("user", query)]},
            config=config
        )
        
        # Extract the final message content
        return response["messages"][-1].content
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            # Add any cleanup needed for MCP client
            pass

# Standalone execution for testing
async def main():
    """Test the agent standalone"""
    agent = NIHReporterAgent()
    await agent.initialize()
    
    print("Invoking agent...")
    response = await agent.run("How many R01s did NIMHD award in 2024?")
    
    print("\n" + "="*80)
    print("RESPONSE:")
    print("="*80)
    print(response)
    print("="*80)
    
    print(f"\n🔍 View your traces at: http://localhost:6006")
    
    await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())