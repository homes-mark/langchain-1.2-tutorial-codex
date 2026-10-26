"""Dependency and real import check. Run: python examples/01_check_environment.py"""
from importlib.metadata import version
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from common import ScriptedChatModel

EXPECTED = {"langchain": "1.2.0", "langchain-core": "1.2.5", "langgraph": "1.0.5",
            "langgraph-prebuilt": "1.0.5", "langchain-openai": "1.1.6",
            "langchain-text-splitters": "1.1.0"}
for name, expected in EXPECTED.items():
    actual = version(name)
    assert actual == expected, f"{name}: expected {expected}, got {actual}"
    print(f"{name}=={actual}")
agent = create_agent(ScriptedChatModel(responses=[AIMessage(content="environment OK")]), tools=[])
assert agent.invoke({"messages": [{"role": "user", "content": "check"}]})["messages"][-1].content == "environment OK"
print("PASS: imports + a real agent graph invocation")
