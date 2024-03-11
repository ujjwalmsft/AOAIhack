import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import RawVectorQuery
from openai import AsyncAzureOpenAI


async def get_documents(
    question: str,
    num_docs=5,
    azure_ai_search_endpoint: str = None,
    azure_ai_search_key: str = None,
    azure_ai_search_index_name: str = None,
    azure_openai_endpoint: str = None,
    azure_openai_key: str = None,
    azure_openai_api_version: str = None,
    azure_openai_embedding_deployment: str = None,
) -> str:
    #  retrieve documents relevant to the user's question from Cognitive Search
    search_client = SearchClient(
        endpoint=azure_ai_search_endpoint,
        credential=AzureKeyCredential(azure_ai_search_key),
        index_name=azure_ai_search_index_name,
    )

    async with AsyncAzureOpenAI(
        azure_endpoint=azure_openai_endpoint,
        api_key=azure_openai_key,
        api_version=azure_openai_api_version,
    ) as aclient:

        # generate a vector embedding of the user's question
        embedding = await aclient.embeddings.create(
            input=question, model=azure_openai_embedding_deployment
        )
        embedding_to_query = embedding.data[0].embedding

    context = ""
    async with search_client:
        # use the vector embedding to do a vector search on the index
        vector_query = RawVectorQuery(
            vector=embedding_to_query, k=num_docs, fields="contentVector"
        )
        results = await search_client.search(
            search_text="", vector_queries=[vector_query], select=["id", "content"]
        )

        async for result in results:
            context += f"\n>>> From: {result['id']}\n{result['content']}"

    return context
