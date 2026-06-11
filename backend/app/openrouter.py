from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

from .config import get_settings


def get_llm():
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")

    return OpenAI(
        api_key=settings.openrouter_api_key,
        api_base=settings.openrouter_base_url,
        model=settings.openrouter_model,
        temperature=0.2,
    )


def get_embedding_model() -> OpenAIEmbedding:
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")

    return OpenAIEmbedding(
        api_key=settings.openrouter_api_key,
        api_base=settings.openrouter_base_url,
        model=settings.openrouter_embedding_model,
    )
