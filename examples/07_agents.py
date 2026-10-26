"""LangChain 1.2.0; full versions: requirements.lock.txt. Optional: --live."""
import argparse
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, ToolMessage
from common import ScriptedChatModel, live_model


@tool
def service_status(service: str) -> str:
    """Read a demo service status. Supported service: vpn. No external IO."""
    return {"vpn": "operational"}.get(service.lower(), "unknown service")


def build_agent(live=False):
    model = live_model() if live else ScriptedChatModel(responses=[
        AIMessage(content="", tool_calls=[{"name": "service_status", "args": {"service": "vpn"}, "id": "status-1", "type": "tool_call"}]),
        AIMessage(content="VPN 服务运行正常（operational）。"),
    ])
    return create_agent(model, tools=[service_status], system_prompt="用中文回答。服务状态必须查询工具；未知服务说明无法确认。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    result = build_agent(args.live).invoke(
        {"messages": [{"role": "user", "content": "请查询 VPN 服务是否正常。"}]},
        config={"recursion_limit": 12},
    )
    for message in result["messages"]:
        print(message.type, message.content, getattr(message, "tool_calls", ""))
    if not args.live:
        assert [m.type for m in result["messages"]] == ["human", "ai", "tool", "ai"]
        assert next(m for m in result["messages"] if isinstance(m, ToolMessage)).content == "operational"
        # New model instance: scripted responses are consumed, not reusable data.
        steps = list(build_agent().stream({"messages": [{"role":"user", "content":"VPN?"}]}, stream_mode="updates"))
        assert [list(x)[0] for x in steps] == ["model", "tools", "model"]
        print("PASS: tool loop and stream updates = model -> tools -> model")
