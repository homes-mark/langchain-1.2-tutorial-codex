"""LCEL 链。依赖：langchain==1.2.0；完整版本见 requirements.lock.txt。"""
import asyncio

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel


def main() -> None:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "用一句话解答 IT 问题。"),
        ("human", "{question}"),
    ])
    model = FakeListChatModel(responses=["请通过服务台完成身份验证。"])
    chain = prompt | model | StrOutputParser()

    # dict -> ChatPromptValue -> AIMessage -> str
    answer = chain.invoke({"question": "如何重置密码？"})
    assert isinstance(answer, str)
    print("单条：", answer)

    inputs = [{"question": "问题 A"}, {"question": "问题 B"}]
    answers = chain.batch(inputs, config={"max_concurrency": 2})
    assert len(answers) == 2
    print("批量结果数：", len(answers))

    # 两个独立分支收到同一输入；其中只有 answer 分支调用模型。
    with_question = RunnableParallel(
        answer=chain,
        question=RunnableLambda(lambda item: item["question"]),
    )
    result = with_question.invoke({"question": "如何重置密码？"})
    assert result["question"] == "如何重置密码？"
    print("保留问题：", result)

    async_answer = asyncio.run(chain.ainvoke({"question": "异步调用如何返回？"}))
    assert isinstance(async_answer, str)
    print("异步：", async_answer)


if __name__ == "__main__":
    main()
