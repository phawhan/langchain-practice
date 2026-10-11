"""Command-line chat with JobPilot. Prints routing and tool calls so you can watch the agents think.

Run:
  uv run jobpilot                    # router mode: router -> one specialist (or the job comparison orchestrator)
  uv run jobpilot --mode supervisor  # supervisor mode: delegates to workers; conversation saved (resume later)
  uv run jobpilot --mode supervisor --thread job-hunt-oct   # start or resume a named conversation
  uv run jobpilot --show-memories    # what JobPilot remembers about you (long-term memory)
"""
import argparse
import asyncio

from langgraph.errors import GraphRecursionError

from jobpilot.agents.career_coach_agent import build_career_coach_agent
from jobpilot.agents.job_comparison_orchestrator import compare_jobs
from jobpilot.agents.job_search_agent import build_job_search_agent
from jobpilot.agents.router import OFF_TOPIC_REPLY, classify_intent
from jobpilot.agents.supervisor_agent import build_supervisor_agent
from jobpilot.config import settings
from jobpilot.dependencies import UserContext
from jobpilot.memory.long_term import format_memories
from jobpilot.memory.stores import get_memory_store


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


def run_agent_turn(agent, messages: list, context: UserContext) -> list:
    """Run one agent turn, print what it did, and return the updated conversation."""
    try:
        result = agent.invoke(
            {"messages": messages},
            config={"recursion_limit": settings.max_agent_steps},  # safety stop for runaway loops
            context=context,
        )
    except GraphRecursionError:
        print("\njobpilot> Sorry, I couldn't finish that. Please try rephrasing.")
        return messages[:-1]
    print_trace(result["messages"][len(messages):])  # only what the agent added this turn
    return result["messages"]


def reply_without_agent(messages: list, text: str) -> list:
    print(f"\njobpilot> {text}")
    return [*messages, {"role": "assistant", "content": text}]


def run_supervisor_turn(supervisor, user_input: str, config: dict, context: UserContext) -> None:
    """Send only the NEW message: the checkpointer loads the rest of the conversation by thread_id."""
    try:
        result = supervisor.invoke({"messages": [{"role": "user", "content": user_input}]}, config=config, context=context)
    except GraphRecursionError:
        print("\njobpilot> Sorry, I couldn't finish that. Please try rephrasing.")
        return
    messages = result["messages"]
    last_user_index = max(i for i, m in enumerate(messages) if m.type == "human")
    print_trace(messages[last_user_index + 1:])  # only what the agent added this turn


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with JobPilot")
    parser.add_argument("--mode", choices=["router", "supervisor"], default="router")
    parser.add_argument("--thread", default="main", help="Conversation id (supervisor mode). Same id = resume it.")
    parser.add_argument("--show-memories", action="store_true", help="Print what JobPilot remembers about you")
    args = parser.parse_args()

    context = UserContext(candidate_id="CAND-001")  # in a real app this comes from login
    if args.show_memories:
        print(format_memories(get_memory_store(), context.candidate_id) or "No memories yet.")
        return

    if args.mode == "supervisor":
        supervisor = build_supervisor_agent()
        config = {
            "configurable": {"thread_id": f"{context.candidate_id}:{args.thread}"},  # one id per user + chat
            "recursion_limit": settings.max_agent_steps,
        }
        saved = supervisor.get_state(config).values.get("messages", [])
        print(f"JobPilot (supervisor mode, thread '{args.thread}'). Type 'exit' to quit.")
        if saved:
            print(f"Resuming this conversation: {len(saved)} saved messages.")
        while (user_input := _read_input()) is not None:
            run_supervisor_turn(supervisor, user_input, config, context)
        return

    specialists = {"job_search": build_job_search_agent(), "career_coach": build_career_coach_agent()}
    messages: list = []  # router mode keeps the conversation in RAM only (lost on exit)
    print("JobPilot (router mode) - your job-search assistant. Type 'exit' to quit.")
    while (user_input := _read_input()) is not None:
        messages.append({"role": "user", "content": user_input})
        decision = classify_intent(recent_turns(messages))
        print(f"  [router]      {decision.route} - {decision.reason}")
        if decision.route == "off_topic":  # answered by code: no agent, no tools, no cost
            messages = reply_without_agent(messages, OFF_TOPIC_REPLY)
        elif decision.route == "job_comparison":  # orchestrator: split -> parallel subagents -> combine
            messages = reply_without_agent(messages, asyncio.run(compare_jobs(user_input, context)))
        else:
            messages = run_agent_turn(specialists[decision.route], messages, context)


def _read_input() -> str | None:
    """Next non-empty user line, or None when the user exits."""
    while True:
        try:
            user_input = input("\nyou> ").strip()
        except EOFError:
            return None
        if user_input.lower() in {"exit", "quit"}:
            return None
        if len(user_input) > settings.max_input_chars:  # input guardrail: no giant pastes (cost, injection surface)
            print(f"\njobpilot> That message is too long. Please keep it under {settings.max_input_chars} characters.")
            continue
        if user_input:
            return user_input


if __name__ == "__main__":
    main()
