import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import RawVectorQuery
from openai import AsyncAzureOpenAI


async def get_documents(
    question: str,
    index_name: str,
    num_docs=5,
) -> str:
    #  retrieve documents relevant to the user's question from Cognitive Search
    search_client = SearchClient(
        endpoint=os.environ.get("AZURE_AI_SEARCH_ENDPOINT", ""),
        credential=AzureKeyCredential(os.environ.get("AZURE_AI_SEARCH_KEY", "")),
        index_name=index_name,
    )

    async with AsyncAzureOpenAI(
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
        api_key=os.environ.get("AZURE_OPENAI_KEY", ""),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", ""),
    ) as aclient:

        # generate a vector embedding of the user's question
        embedding = await aclient.embeddings.create(
            input=question, model=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        )
        embedding_to_query = embedding.data[0].embedding

    context = ""
    contexts = []
    async with search_client:
        # use the vector embedding to do a vector search on the index
        vector_query = RawVectorQuery(
            vector=embedding_to_query, k=num_docs, fields="contentVector"
        )
        results = await search_client.search(
            search_text="", vector_queries=[vector_query], select=["id", "content"]
        )

        async for result in results:
            context += f"\n>>> {result['content']}"
            contexts.append(result["content"])

    return context, contexts
