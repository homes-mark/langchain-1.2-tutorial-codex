"""依赖：langchain==1.2.0 / langgraph==1.0.5；完整版本见 requirements.lock.txt。
运行：python examples/08_memory.py；无需网络或 API 密钥。
"""

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from common import ScriptedChatModel


def main() -> None:
    saver = InMemorySaver()
    store = InMemoryStore()
    # namespace 由可信应用上下文构造，不能相信用户在聊天中声明的身份。
    namespace = ("acme", "users", "u-001", "preferences")
    store.put(namespace, "reply_style", {"language": "zh", "concise": True})
    model = ScriptedChatModel(responses=[
        AIMessage(content="已收到你的姓名。"),
        AIMessage(content="你叫小林。"),
        AIMessage(content="这个新会话还没有你的姓名。"),
    ])
    agent = create_agent(model=model, tools=[], checkpointer=saver, store=store)
    config_a = {"configurable": {"thread_id": "acme:u-001:session-a"}}
    config_b = {"configurable": {"thread_id": "acme:u-001:session-b"}}
    agent.invoke({"messages": [{"role": "user", "content": "我叫小林"}]}, config_a)
    result = agent.invoke({"messages": [{"role": "user", "content": "我叫什么？"}]}, config_a)
    other = agent.invoke({"messages": [{"role": "user", "content": "我叫什么？"}]}, config_b)

    saved = agent.get_state(config_a).values["messages"]
    assert len(saved) == 4
    assert any(isinstance(msg, HumanMessage) and "小林" in msg.content for msg in saved)
    assert len(other["messages"]) == 2
    assert all("我叫小林" != msg.content for msg in other["messages"])
    profile = store.get(namespace, "reply_style")
    assert profile is not None and profile.value["language"] == "zh"
    assert store.get(("beta", "users", "u-001", "preferences"), "reply_style") is None
    print(result["messages"][-1].content)
    print(f"同一会话消息数：{len(saved)}；新会话消息数：{len(other['messages'])}")
    print("跨会话偏好可读；另一租户命名空间没有该记录：PASS")
    print("注意：模型回复预设；断言验证状态持久化与隔离，不证明模型记忆推理能力。")


if __name__ == "__main__":
    main()
