"""LangChain 1.2.0 middleware/limits. Full pins: requirements.lock.txt."""
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, wrap_tool_call
from langchain.tools import tool
from langchain_core.messages import AIMessage, ToolMessage
from common import ScriptedChatModel


@tool
def lookup_service(name: str) -> str:
    """Look up a demo service; only vpn is registered."""
    if name != "vpn":
        raise ValueError("Service is not registered")
    return "available"


@wrap_tool_call
def safe_tool_error(request, handler):
    try:
        return handler(request)
    except ValueError:
        # A known business failure is recoverable. Do not return stack traces/secrets.
        return ToolMessage(content="UNKNOWN_SERVICE: ask the user for a supported service name.",
                           tool_call_id=request.tool_call["id"], status="error")


def run_demo(limit):
    model = ScriptedChatModel(responses=[
        AIMessage(content="", tool_calls=[{"name":"lookup_service", "args":{"name":"unknown"}, "id":"lookup-1", "type":"tool_call"}]),
        AIMessage(content="暂时无法确认该服务，请提供有效的服务名称。"),
    ])
    agent = create_agent(model, tools=[lookup_service], middleware=[
        safe_tool_error, ModelCallLimitMiddleware(run_limit=limit, exit_behavior="end")
    ])
    result = agent.invoke({"messages":[{"role":"user","content":"查询 unknown"}]}, config={"recursion_limit":12})
    assert next(m for m in result["messages"] if isinstance(m, ToolMessage)).status == "error"
    assert model.cursor == min(limit, 2)
    print(f"model_calls={model.cursor}; final={result['messages'][-1].content}")
    return result


if __name__ == "__main__":
    run_demo(3)
    run_demo(1)
    print("PASS: recoverable tool failure + enforced model call budget")
