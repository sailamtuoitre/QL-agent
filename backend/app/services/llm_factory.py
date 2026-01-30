from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatGemini
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from app.core.config import settings

class BaseLLMService(ABC):
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        pass

class OpenAIService(BaseLLMService):
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL
        )

    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        langchain_messages = self._convert_messages(messages)
        response = await self.llm.ainvoke(langchain_messages, **kwargs)
        return response.content

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        converted = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                converted.append(SystemMessage(content=content))
            elif role == "user":
                converted.append(HumanMessage(content=content))
            elif role == "assistant":
                converted.append(AIMessage(content=content))
        return converted

class GeminiService(BaseLLMService):
    def __init__(self):
        # Note: LangChain Gemini integration might vary, using a common pattern
        from langchain_google_genai import ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=settings.GEMINI_API_KEY,
            model="gemini-pro"
        )

    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        langchain_messages = self._convert_messages(messages)
        response = await self.llm.ainvoke(langchain_messages, **kwargs)
        return response.content

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        converted = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                converted.append(SystemMessage(content=content))
            elif role == "user":
                converted.append(HumanMessage(content=content))
            elif role == "assistant":
                converted.append(AIMessage(content=content))
        return converted

class MockService(BaseLLMService):
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        return "This is a mock response from the LLM Factory."

class LLMFactory:
    @staticmethod
    def get_service() -> BaseLLMService:
        provider = settings.LLM_PROVIDER.upper()
        if provider == "OPENAI":
            return OpenAIService()
        elif provider == "GEMINI":
            return GeminiService()
        elif provider == "MOCK":
            return MockService()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
