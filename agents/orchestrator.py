import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from autogen import ConversableAgent

from agents.rag_agent import search_knowledge_base, RAG_AGENT_SYSTEM_MESSAGE
from agents.order_agent import get_order_status, ORDER_AGENT_SYSTEM_MESSAGE

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

def create_agents():
    orchestrator = ConversableAgent(
        name="Orchestrator",
        system_message="""You are the Orchestrator of a customer support system.
Your job is to understand the customer's query and coordinate with specialized agents.

Follow these steps:
1. Analyze the customer query to determine what information is needed.
2. If the query is about policies, FAQs, shipping, or general info → call search_knowledge_base.
3. If the query mentions an order number → call get_order_status.
4. If both are needed, call both functions.
5. After gathering information, compose a helpful, friendly, and accurate response.

Always be polite and professional. Base your answers ONLY on the information returned
by the tools. If information is insufficient, let the customer know and suggest
contacting support directly.""",
        llm_config=LLM_CONFIG,
        human_input_mode="NEVER",
    )

    # --- RAG Agent ---
    rag_agent = ConversableAgent(
        name="RAG_Agent",
        system_message=RAG_AGENT_SYSTEM_MESSAGE,
        llm_config=LLM_CONFIG,
        human_input_mode="NEVER",
    )

    # --- Order Agent ---
    order_agent = ConversableAgent(
        name="Order_Agent",
        system_message=ORDER_AGENT_SYSTEM_MESSAGE,
        llm_config=LLM_CONFIG,
        human_input_mode="NEVER",
    )

    # --- Register tools with the orchestrator ---
    orchestrator.register_for_llm(
        name="search_knowledge_base",
        description="Search the company knowledge base (FAQs and policies) for relevant information.",
    )(search_knowledge_base)

    orchestrator.register_for_llm(
        name="get_order_status",
        description="Look up a customer order by order ID to get status, tracking, and details.",
    )(get_order_status)

    # Register tool execution with the respective agents
    rag_agent.register_for_execution(name="search_knowledge_base")(search_knowledge_base)
    order_agent.register_for_execution(name="get_order_status")(get_order_status)

    return orchestrator, rag_agent, order_agent


def extract_order_id(query: str) -> str | None:
    """Extract order ID from a user query."""
    match = re.search(r"#?(\d{4,})", query)
    return match.group(1) if match else None


async def handle_customer_query(query: str) -> str:
    orchestrator, rag_agent, order_agent = create_agents()

    # Determine which agent(s) to involve
    order_id = extract_order_id(query)
    gathered_context = []

    # Step 1: If there's an order ID, fetch order details
    if order_id:
        order_info = get_order_status(order_id)
        gathered_context.append(f"ORDER DATA:\n{order_info}")

    # Step 2: Search knowledge base for relevant policies/FAQs
    kb_results = search_knowledge_base(query)
    gathered_context.append(f"KNOWLEDGE BASE:\n{kb_results}")

    # Step 3: Send everything to the orchestrator for a final response
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
