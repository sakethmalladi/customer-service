import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.rag_agent import search_knowledge_base
from agents.order_agent import get_order_status
from agents.prompts import ORCHESTRATOR_SYSTEM_MESSAGE, RAG_AGENT_SYSTEM_MESSAGE, ORDER_AGENT_SYSTEM_MESSAGE
from agents.helpers import create_agent, register_tools


def create_agents():
    """Create and configure all AutoGen agents."""
    orchestrator = create_agent("Orchestrator", ORCHESTRATOR_SYSTEM_MESSAGE)
    rag_agent = create_agent("RAG_Agent", RAG_AGENT_SYSTEM_MESSAGE)
    order_agent = create_agent("Order_Agent", ORDER_AGENT_SYSTEM_MESSAGE)

    # Define all tools in one place — easy to add new ones
    tools = [
        {
            "name": "search_knowledge_base",
            "description": "Search the company knowledge base (FAQs and policies) for relevant information.",
            "func": search_knowledge_base,
            "executor": rag_agent,
        },
        {
            "name": "get_order_status",
            "description": "Look up a customer order by order ID to get status, tracking, and details.",
            "func": get_order_status,
            "executor": order_agent,
        },
    ]

    register_tools(orchestrator, tools)

    return orchestrator, rag_agent, order_agent


def extract_order_id(query: str) -> str | None:
    """Extract order ID from a user query."""
    match = re.search(r"#?(\d{4,})", query)
    return match.group(1) if match else None


async def handle_customer_query(query: str) -> str:
    orchestrator, rag_agent, order_agent = create_agents()

    order_id = extract_order_id(query)
    gathered_context = []

    if order_id:
        order_info = get_order_status(order_id)
        gathered_context.append(f"ORDER DATA:\n{order_info}")

    kb_results = search_knowledge_base(query)
    gathered_context.append(f"KNOWLEDGE BASE:\n{kb_results}")

    context = "\n\n---\n\n".join(gathered_context)
    prompt = f"""Customer Query: {query}

Here is the information gathered from our systems:

{context}

Based on the above information, compose a helpful and accurate response to the customer.
Be friendly, concise, and professional. Only use the information provided above."""

    result = await orchestrator.a_generate_reply(
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract the response text
    if isinstance(result, dict):
        return result.get("content", str(result))
    return str(result)
