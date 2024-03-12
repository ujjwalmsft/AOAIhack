import asyncio
from typing import List

import nest_asyncio
from openai import AzureOpenAI

nest_asyncio.apply()
import os

from .retrieve_documents import get_documents


def build_message(user_prompt: str, system_role: str) -> List[dict]:
    return [
        {"role": "system", "content": system_role},
        {"role": "user", "content": user_prompt},
    ]


def chat_completion(
    question: str,
    system_role: str,
    user_prompt: str,
    index_name: str,
    num_docs: int = 5,
    temperature: float = 0.7,
    max_tokens: int = 800,
):
    # get search documents for the last user message in the conversation
    context, contexts = asyncio.run(
        get_documents(
            question=question,
            index_name=index_name,
            num_docs=num_docs,
        )
    )

    # TODO: Add context to user message
    user_prompt = user_prompt.format(question=question, context=context)
    message = build_message(user_prompt=user_prompt, system_role=system_role)

    with AzureOpenAI(
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
        api_key=os.environ.get("AZURE_OPENAI_KEY", ""),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", ""),
    ) as client:

        # call Azure OpenAI with the system prompt and user's question
        chat_completion = client.chat.completions.create(
            model=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            messages=message,
            temperature=temperature,
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
        "contexts": contexts,
        "num_docs": num_docs,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    response["choices"][0]["context"] = context_dict
    return response
