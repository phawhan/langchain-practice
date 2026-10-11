"""Command-line chat with JobPilot. Prints routing and tool calls so you can watch the agents think.

Run: uv run jobpilot
"""
from langgraph.errors import GraphRecursionError

from jobpilot.agents.career_coach_agent import build_career_coach_agent
from jobpilot.agents.job_search_agent import build_job_search_agent
from jobpilot.agents.router import OFF_TOPIC_REPLY, classify_intent
from jobpilot.config import settings
from jobpilot.dependencies import UserContext


def recent_turns(messages: list, limit: int = 4) -> list[dict]:
    """Last few user/assistant text turns (tool traffic removed) - enough context for the router."""
    turns = []
    for m in messages:
        role, content = (m["role"], m["content"]) if isinstance(m, dict) else ({"human": "user", "ai": "assistant"}.get(m.type), m.content)
        if role in ("user", "assistant") and content:
            turns.append({"role": role, "content": content})
    return turns[-limit:]


def print_trace(new_messages: list) -> None:
    for message in new_messages:
        if message.type == "ai" and message.tool_calls:
            for call in message.tool_calls:
                print(f"  [tool call]   {call['name']}({call['args']})")
        elif message.type == "tool":
            print(f"  [tool result] {str(message.content)[:150]}")
        elif message.type == "ai":
            print(f"\njobpilot> {message.content}")


def main() -> None:
    specialists = {"job_search": build_job_search_agent(), "career_coach": build_career_coach_agent()}
    context = UserContext(candidate_id="CAND-001")  # in a real app this comes from login
    messages: list = []  # conversation so far = short-term memory, shared by all specialists
    print("JobPilot - your job-search assistant. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("\nyou> ").strip()
        except EOFError:
            break
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})

        decision = classify_intent(recent_turns(messages))
        print(f"  [router]      {decision.route} - {decision.reason}")
        if decision.route == "off_topic":  # answered by code: no agent, no tools, no cost
            print(f"\njobpilot> {OFF_TOPIC_REPLY}")
            messages.append({"role": "assistant", "content": OFF_TOPIC_REPLY})
            continue

        try:
            result = specialists[decision.route].invoke(
                {"messages": messages},
                config={"recursion_limit": settings.max_agent_steps},  # safety stop for runaway loops
                context=context,
            )
        except GraphRecursionError:
            print("\njobpilot> Sorry, I couldn't finish that. Please try rephrasing.")
            messages.pop()
            continue
        print_trace(result["messages"][len(messages):])  # only what the agent added this turn
        messages = result["messages"]


if __name__ == "__main__":
    main()
