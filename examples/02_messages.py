"""消息与模型。依赖：langchain==1.2.0；完整版本见 requirements.lock.txt。

离线：python examples/02_messages.py
在线：python examples/02_messages.py --live（先配置模型环境变量）
"""
import sys

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def main() -> None:
    messages = [
        SystemMessage(content="你是企业 IT 助手。用中文简短回答。"),
        HumanMessage(content="密码重置前应先完成什么？"),
    ]
    if "--live" in sys.argv:
        from common import live_model

        model = live_model()
    else:
        # 真正运行 LangChain 接口，但回答是固定测试数据，不具有推理能力。
        model = FakeListChatModel(responses=["先完成身份验证。"])

    response = model.invoke(messages)
    assert isinstance(response, AIMessage)
    print("消息角色：", [message.type for message in messages])
    print("模型回复：", response.content)

    # 模型对象不会替你保留聊天历史；下一次调用应显式传入历史。
    history = [*messages, response, HumanMessage(content="为什么？")]
    assert len(history) == 4
    print("下一轮消息数：", len(history))

    # 仅演示离线流式接口，避免在线例子额外计费。
    streaming_model = FakeListChatModel(responses=["身份验证"])
    text = "".join(chunk.content for chunk in streaming_model.stream(messages))
    assert text == "身份验证"
    print("流式合并：", text)


if __name__ == "__main__":
    main()
