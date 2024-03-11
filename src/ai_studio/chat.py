import asyncio
from typing import List

from openai import AsyncAzureOpenAI

from .retrieve_documents import get_documents
from .utils import add_context_to_streamed_response


def build_message(user_prompt: str, system_role: str) -> List[dict]:
    return [
        {"role": "system", "content": system_role},
        {"role": "user", "content": user_prompt},
    ]


async def chat_completion(
    question: str,
    system_role: str,
    user_prompt: str,
    stream: bool = False,
    num_docs: int = 5,
    temperature: float = 0.7,
    max_tokens: int = 800,
    azure_ai_search_endpoint: str = None,
    azure_ai_search_key: str = None,
    azure_ai_search_index_name: str = None,
    azure_openai_embedding_deployment: str = None,
    azure_openai_endpoint: str = None,
    azure_openai_key: str = None,
    azure_openai_api_version: str = None,
    azure_openai_chat_deployment: str = None,
):
    # get search documents for the last user message in the conversation
    context = await get_documents(
        question=question,
        num_docs=num_docs,
        azure_ai_search_endpoint=azure_ai_search_endpoint,
        azure_ai_search_key=azure_ai_search_key,
        azure_ai_search_index_name=azure_ai_search_index_name,
        azure_openai_endpoint=azure_openai_endpoint,
        azure_openai_key=azure_openai_key,
        azure_openai_api_version=azure_openai_api_version,
        azure_openai_embedding_deployment=azure_openai_embedding_deployment,
    )

    # TODO: Add context to user message
    user_prompt = user_prompt.format(question=question, context=context)
    message = build_message(user_prompt=user_prompt, system_role=system_role)

    async with AsyncAzureOpenAI(
        azure_endpoint=azure_openai_endpoint,
        api_key=azure_openai_key,
        api_version=azure_openai_api_version,
    ) as aclient:

        # call Azure OpenAI with the system prompt and user's question
        chat_completion = await aclient.chat.completions.create(
            model=azure_openai_chat_deployment,
            messages=message,
            temperature=temperature,
            stream=stream,
            max_tokens=max_tokens,
        )

    response = {
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": chat_completion.choices[0].message.content,
                },
            }
        ]
    }

    # add context in the returned response
    context_dict = {
        "context": context,
        "num_docs": num_docs,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if not stream:
        response["choices"][0]["context"] = context_dict
    else:
        response = add_context_to_streamed_response(response, context_dict)
    return response
