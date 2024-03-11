import os

from azure.ai.generative.index import build_index
from azure.ai.resources.client import AIClient
from azure.ai.resources.operations._index_data_source import (
    ACSOutputConfig,
    LocalSource,
)
from azure.identity import DefaultAzureCredential


def build_cogsearch_index(
    index_name: str,
    path_to_data: str,
    chunk_size: int,
    chunk_overlap: int,
    azure_ai_search_endpoint: str,
    azure_ai_search_key: str,
    azure_ai_cognitive_search_connection_name: str,
    azure_openai_embedding_deployment: str,
    azure_openai_embedding_model: str,
    vector_store: str = "azure_cognitive_search",
    data_source_url: str = None,
):
    # Set up environment variables for cog search SDK
    os.environ["AZURE_COGNITIVE_SEARCH_TARGET"] = azure_ai_search_endpoint
    os.environ["AZURE_COGNITIVE_SEARCH_KEY"] = azure_ai_search_key

    client = AIClient.from_config(DefaultAzureCredential())

    print(
        "Azure AI Search Connection name: ", azure_ai_cognitive_search_connection_name
    )
    default_aoai_connection = client.get_default_aoai_connection()
    default_aoai_connection.set_current_environment()

    default_acs_connection = client.connections.get(
        azure_ai_cognitive_search_connection_name
    )
    default_acs_connection.set_current_environment()

    # Use the same index name when registering the index in AI Studio
    index = build_index(
        output_index_name=index_name,
        vector_store=vector_store,
        embeddings_model="azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002-2",
        data_source_url=data_source_url,
        index_input_config=LocalSource(input_data=path_to_data),
        acs_config=ACSOutputConfig(
            acs_index_name=index_name,
        ),
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    # register the index so that it shows up in the project
    cloud_index = client.indexes.create_or_update(index)

    print(f"Created index '{cloud_index.name}'")
    print(f"Local Path: {index.path}")
    print(f"Cloud Path: {cloud_index.path}")
