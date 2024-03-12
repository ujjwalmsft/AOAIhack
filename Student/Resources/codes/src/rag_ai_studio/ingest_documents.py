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
    data_source_url: str = None,
):
    # Set up environment variables for cog search SDK
    os.environ["AZURE_COGNITIVE_SEARCH_TARGET"] = os.environ.get(
        "AZURE_AI_SEARCH_ENDPOINT", ""
    )
    os.environ["AZURE_COGNITIVE_SEARCH_KEY"] = os.environ.get("AZURE_AI_SEARCH_KEY", "")

    client = AIClient.from_config(DefaultAzureCredential())

    default_aoai_connection = client.get_default_aoai_connection()
    default_aoai_connection.set_current_environment()

    default_acs_connection = client.connections.get(
        os.environ.get("AZURE_COGNITIVE_SEARCH_CONNECTION_NAME", "")
    )
    default_acs_connection.set_current_environment()

    # Use the same index name when registering the index in AI Studio
    index = build_index(
        output_index_name=index_name,
        vector_store=os.environ.get("VECTOR_STORE", ""),
        embeddings_model=f"azure_open_ai://deployment/{os.environ.get('AZURE_OPENAI_EMBEDDING_DEPLOYMENT')}/model/{os.environ.get('AZURE_OPENAI_EMBEDDING_MODEL')}",
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
