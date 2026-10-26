"""提示模板。依赖：langchain==1.2.0；完整版本见 requirements.lock.txt。"""
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate


def main() -> None:
    text_prompt = PromptTemplate.from_template(
        "为{department}解释{topic}；输出示例格式：{{\"title\": \"标题\"}}"
    )
    text = text_prompt.format(department="财务部", topic="双因素认证")
    assert '{"title": "标题"}' in text
    print("文本模板：", text)

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是{department}的 IT 助手。只根据已提供资料回答。"),
        MessagesPlaceholder("history", optional=True),
        ("human", "用户问题：{question}"),
    ]).partial(department="财务部")

    # 注入值中的花括号不会被二次解释为模板变量。
    question = "配置里出现 {unknown_key} 应怎么办？"
    prompt_value = chat_prompt.invoke({
        "question": question,
        "history": [
            HumanMessage(content="我在安装财务客户端。"),
            AIMessage(content="请提供具体报错信息。"),
        ],
    })
    messages = prompt_value.to_messages()
    assert len(messages) == 4
    assert messages[-1].content == f"用户问题：{question}"
    assert set(chat_prompt.input_variables) == {"question"}
    print("聊天角色：", [message.type for message in messages])
    print("当前问题：", messages[-1].content)

    try:
        chat_prompt.invoke({})
    except KeyError:
        print("缺失 question：已正确拒绝")
    else:
        raise AssertionError("缺少必填模板变量时应失败")


if __name__ == "__main__":
    main()
