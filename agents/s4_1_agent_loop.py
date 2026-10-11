"""4.1 What is an agent - an LLM in a loop that picks tools until the job is done.

The LLM is SCRIPTED here (no API key): it returns the steps a real LLM would choose.
The loop, the tools, and the safety stop are real and work the same with a real LLM.
Run: python3 agents/s4_1_agent_loop.py   (no libraries needed)
"""
import json
from datetime import date

# ---- TOOLS: plain Python functions the agent is allowed to call ----
ORDERS = {"A123": {"item": "Acme laptop", "delivered": "2026-09-20", "opened": True}}
POLICIES = {
    "opened electronics": "Opened laptops, phones, and tablets can be returned within 15 days. "
                          "A 10% restocking fee applies unless the item is defective.",
    "warranty": "All Acme products include a 1-year warranty covering manufacturing defects.",
}


def get_order(order_id: str) -> dict:
    return ORDERS.get(order_id, {"error": f"No order {order_id}. Ask the customer to check the ID."})


def days_since(day: str) -> int:
    return (date(2026, 10, 10) - date.fromisoformat(day)).days  # fixed "today" so output repeats


def search_policy(topic: str) -> str:
    return POLICIES.get(topic, f"No policy found for '{topic}'. Try: {list(POLICIES)}")


TOOLS = {"get_order": get_order, "days_since": days_since, "search_policy": search_policy}

# A real LLM API also receives a description of each tool, so it knows WHEN to use it:
GET_ORDER_SCHEMA = {
    "name": "get_order",
    "description": "Look up a customer's order by its ID. Returns item, delivery date, opened flag.",
    "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]},
}


def scripted_llm(messages: list[dict]) -> dict:
    """Stands in for a real LLM call: returns either a tool call or a final answer."""
    used = [m["tool"] for m in messages if m["role"] == "tool"]
    if "get_order" not in used:
        return {"thought": "I need the order details first.", "tool": "get_order", "args": {"order_id": "A123"}}
    if "days_since" not in used:
        return {"thought": "How long ago was it delivered?", "tool": "days_since", "args": {"day": "2026-09-20"}}
    if "search_policy" not in used:
        return {"thought": "What is the rule for opened laptops?", "tool": "search_policy",
                "args": {"topic": "opened electronics"}}
    return {"answer": "Sorry, opened laptops can be returned within 15 days of delivery. Yours arrived "
                      "20 days ago, so a return isn't possible. If it's faulty, you can file a warranty claim."}


def run_agent(question: str, llm=scripted_llm, max_steps: int = 5) -> str:
    messages = [{"role": "user", "content": question}]  # short-term memory: everything so far
    print(f"USER: {question}")
    for step in range(1, max_steps + 1):
        decision = llm(messages)  # 1. THINK: the LLM decides the next move
        if "answer" in decision:
            print(f"\nFINAL ANSWER: {decision['answer']}")
            return decision["answer"]
        print(f"\nstep {step}  THINK: {decision['thought']}\n         ACT  : {decision['tool']}({decision['args']})")
        try:
            result = TOOLS[decision["tool"]](**decision["args"])  # 2. ACT: our code runs the tool
        except Exception as e:
            result = {"error": str(e)}  # errors go back to the LLM so it can try something else
        print(f"         SEE  : {json.dumps(result)[:140]}")
        messages.append({"role": "tool", "tool": decision["tool"], "content": result})  # 3. OBSERVE
    return "Stopped: too many steps. Handing over to a human."  # safety stop


if __name__ == "__main__":
    run_agent("I opened my laptop from order A123. Can I still return it?")
