import os
from dotenv import load_dotenv
from autogen import ConversableAgent

load_dotenv()

LLM_CONFIG = {
    "config_list": [
        {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    ],
    "temperature": 0.3,
}


def create_agent(name: str, system_message: str) -> ConversableAgent:
    """Create a ConversableAgent with standard config."""
    return ConversableAgent(
        name=name,
        system_message=system_message,
        llm_config=LLM_CONFIG,
        human_input_mode="NEVER",
    )


def register_tools(orchestrator: ConversableAgent, tool_definitions: list[dict]):
    """
    Register multiple tools with the orchestrator from a list of definitions.

    Each definition dict should have:
        - name: tool function name
        - description: what the tool does
        - func: the callable function
        - executor: the agent that executes this tool
    """
    for tool in tool_definitions:
        orchestrator.register_for_llm(
            name=tool["name"], description=tool["description"]
        )(tool["func"])
        tool["executor"].register_for_execution(
            name=tool["name"]
        )(tool["func"])
