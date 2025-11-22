#!/usr/bin/env python3

import asyncio
import os

import dotenv
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_google import GoogleAugmentedLLM



dotenv.load_dotenv()

app = MCPApp(name="hello_world_agent")

async def example_usage(question: str):
    async with app.run() as mcp_agent_app:
        logger = mcp_agent_app.logger
        # This agent can read the filesystem or fetch URLs
        finder_agent = Agent(
            name="test",
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
                message=question
            )
            logger.info(f"Response: {result}")
            return result


if __name__ == "__main__":
    asyncio.run(example_usage("Why is the sky blue? Explain in two sentences."))
