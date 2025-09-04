import asyncio
import os

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import GoogleAugmentedLLM

app = MCPApp(name="hello_world_agent")

async def example_usage():
    async with app.run() as mcp_agent_app:
        logger = mcp_agent_app.logger
        # This agent can read the filesystem or fetch URLs
        finder_agent = Agent(
            name="Lumi-test",
            instruction="""You are a helpful assistant""",
             #server_names=["fetch", "filesystem"], # MCP servers this Agent can use
        )

        async with finder_agent:
            # Automatically initializes the MCP servers and adds their tools for LLM use
            #tools = await finder_agent.list_tools()
            #logger.info(f"Tools available:", data=tools)
            llm = await finder_agent.attach_llm(GoogleAugmentedLLM)

            # This will perform a file lookup and read using the filesystem server
            result = await llm.generate_str(
                message="Why is the sky blue? Explain in two sentences."
            )
            logger.info(f"Response: {result}")


if __name__ == "__main__":
    asyncio.run(example_usage())
