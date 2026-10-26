"""Deterministic workflow regression, not an LLM quality benchmark.
Dependencies: LangChain 1.2.0, requirements.lock.txt.
"""
from importlib import import_module
from langchain_core.messages import AIMessage, ToolMessage

build_agent = import_module("07_agents").build_agent


def evaluate():
    samples = ["VPN 能用吗？", "请检查 VPN 状态", "查询 vpn 服务"]
    records = []
    for query in samples:
        result = build_agent().invoke({"messages":[{"role":"user","content":query}]})
        messages = result["messages"]
        calls = [c for m in messages if isinstance(m, AIMessage) for c in m.tool_calls]
        outputs = [m for m in messages if isinstance(m, ToolMessage)]
        records.append({"query": query,
                        "tool_correct": len(calls) == 1 and calls[0]["name"] == "service_status" and calls[0]["args"] == {"service":"vpn"},
                        "tool_output_correct": len(outputs) == 1 and outputs[0].content == "operational",
                        "model_calls": sum(isinstance(m, AIMessage) for m in messages)})
    score = sum(r["tool_correct"] and r["tool_output_correct"] for r in records) / len(records)
    assert score == 1.0 and all(r["model_calls"] == 2 for r in records)
    print(f"fixture workflow success={score:.0%}; cases={len(records)}; model_calls=2/case")
    print("This does NOT measure live model intent understanding or answer truthfulness.")


if __name__ == "__main__":
    evaluate()
