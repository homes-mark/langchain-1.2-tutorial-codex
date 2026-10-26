"""Shared teaching models. Dependencies: requirements.lock.txt (LangChain 1.2.0)."""
import os
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class ScriptedChatModel(BaseChatModel):
    """Deterministic protocol fixture; does NOT reason or infer tool arguments.

    Use a fresh instance for every independent run. Not concurrency-safe.
    Real LangChain messages, graph, tools and middleware still execute.
    """

    responses: list[AIMessage]
    cursor: int = 0

    @property
    def _llm_type(self) -> str:
        return "tutorial-scripted-model"

    def bind_tools(self, tools: Any, *, tool_choice: Any = None, **kwargs: Any):
        return self

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None,
                  **kwargs: Any) -> ChatResult:
        if self.cursor >= len(self.responses):
            raise RuntimeError("Script exhausted: inspect unexpected model iterations")
        response = self.responses[self.cursor].model_copy(deep=True)
        self.cursor += 1
        return ChatResult(generations=[ChatGeneration(message=response)])


def live_model():
    """Optional network path. Credentials are never stored in tutorial files."""
    from langchain_openai import ChatOpenAI

    if not os.getenv("OPENAI_API_KEY") or not os.getenv("OPENAI_MODEL"):
        raise SystemExit("Set OPENAI_API_KEY and OPENAI_MODEL to an available chat model.")
    return ChatOpenAI(model=os.environ["OPENAI_MODEL"], timeout=30, max_retries=2)
