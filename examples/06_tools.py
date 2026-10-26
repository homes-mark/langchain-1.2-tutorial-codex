"""工具调用闭环。依赖：langchain==1.2.0；完整版本见 requirements.lock.txt。

离线：python examples/06_tools.py
在线：python examples/06_tools.py --live（模型须支持 tool calling）
"""
import json
import sys

from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from common import ScriptedChatModel


class TotalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    quantity: int = Field(ge=1, le=1000, strict=True, description="采购数量")
    unit_price_cents: int = Field(
        ge=0, le=1000000, strict=True, description="单价，单位为分"
    )


@tool(args_schema=TotalInput)
def calculate_total(quantity: int, unit_price_cents: int) -> dict:
    """计算采购总价，使用整数分；仅计算，不下单或付款。"""
    return {"total_cents": quantity * unit_price_cents, "currency": "CNY"}


def main() -> None:
    if "--live" in sys.argv:
        from common import live_model

        model = live_model()
    else:
        # 固定模型计划，只验证协议与执行逻辑，不评价真实模型选工具能力。
        model = ScriptedChatModel(responses=[
            AIMessage(content="", tool_calls=[{
                "name": "calculate_total",
                "args": {"quantity": 3, "unit_price_cents": 1990},
                "id": "purchase-1",
                "type": "tool_call",
            }]),
            AIMessage(content="总价 5970 分，即 59.70 元；尚未下单。"),
        ])
    bound = model.bind_tools([calculate_total])
    messages = [HumanMessage(content="请调用工具计算 3 件单价 1990 分的总价。")]
    proposal = bound.invoke(messages)
    messages.append(proposal)
    if not proposal.tool_calls:
        raise RuntimeError("模型没有提出工具调用；检查模型能力、提示与工具描述")

    allowed_tools = {calculate_total.name: calculate_total}
    for call in proposal.tool_calls:
        if call["name"] not in allowed_tools:
            raise ValueError("模型提出了未授权的工具名")
        result = allowed_tools[call["name"]].invoke(call["args"])
        messages.append(ToolMessage(
            content=json.dumps(result, ensure_ascii=False),
            name=call["name"],
            tool_call_id=call["id"],
        ))
    answer = bound.invoke(messages)
    if answer.tool_calls:
        raise RuntimeError("本章只演示一轮工具调用；多轮循环见 Agent 章节")
    print("工具结果：", messages[-1].content)
    print("最终回复：", answer.content)
    assert calculate_total.invoke({"quantity": 3, "unit_price_cents": 1990})[
        "total_cents"
    ] == 5970
    try:
        calculate_total.invoke({"quantity": -1, "unit_price_cents": 1990})
    except ValidationError:
        print("负数数量：已正确拒绝")
    else:
        raise AssertionError("工具必须在执行前校验输入")


if __name__ == "__main__":
    main()
