"""结构化输出。依赖：langchain==1.2.0；完整版本见 requirements.lock.txt。

离线：python examples/05_structured.py
在线：python examples/05_structured.py --live
"""
import sys
from typing import Literal

from langchain_core.exceptions import OutputParserException
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, ConfigDict, Field


class TicketSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=80, description="简短工单标题")
    priority: Literal["low", "medium", "high"]
    affected_users: int = Field(ge=1, le=100000, strict=True)


def main() -> None:
    parser = PydanticOutputParser(pydantic_object=TicketSummary)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "提取工单，不编造字段。{format_instructions}"),
        ("human", "{description}"),
    ]).partial(format_instructions=parser.get_format_instructions())
    description = "财务部 12 人无法登录系统，请按 high 优先级记录。"

    if "--live" in sys.argv:
        from common import live_model

        # 集成层处理结构化输出。需要所选提供商/模型支持该功能。
        extractor = live_model().with_structured_output(TicketSummary)
        result = extractor.invoke(description)
    else:
        fake = FakeListChatModel(responses=[
            '{"title":"财务系统登录失败","priority":"high","affected_users":12}'
        ])
        result = (prompt | fake | parser).invoke({"description": description})
        assert result.affected_users == 12
    assert isinstance(result, TicketSummary)
    print(result.model_dump_json())

    invalid = '{"title":"登录失败","priority":"urgent","affected_users":0}'
    try:
        parser.parse(invalid)
    except OutputParserException:
        print("非法枚举与人数：已正确拒绝")
    else:
        raise AssertionError("不满足业务 schema 的 JSON 不应通过")


if __name__ == "__main__":
    main()
