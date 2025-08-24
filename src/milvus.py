from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)
from llama_index.core.vector_stores.types import VectorStoreQuery


from dotenv import load_dotenv
import os
from classes.FileNode import FileNode
from pprint import pprint
import json

load_dotenv()


def milvus_config(overwrite: bool = False) -> StorageContext:
    print("----- Connecting to Milvus -----")
    vector_store = MilvusVectorStore(
        uri="https://in03-890cd99e122622e.serverless.aws-eu-central-1.cloud.zilliz.com",
        token=os.getenv("MILVUS_TOKEN"),
        collection_name="source_code_collection",
        dim=768,  # Vector dimension depends on the embedding model
        overwrite=overwrite,  # Drop collection if exists
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    print("----- Milvus Connected - Storage Context Generated -----")
    return storage_context


def set_milvus_index(storage_context: StorageContext):
    print("----- Setting Milvus Index -----")
    embed_model = GeminiEmbedding(
        model_name="models/embedding-001",  # Default Gemini embedding model
        api_key=os.getenv("GEMINI_API_KEY")
    )
    index = VectorStoreIndex.from_vector_store(
        vector_store=storage_context.vector_store,
        embed_model=embed_model,
        transformations=[],  # do not apply any transformations
        show_progress=True
    )

    print("---- Index Generated ----")
    return index


def get_file_nodes(file_path: str, index: VectorStoreIndex) -> list[TextNode]:
    filters = MetadataFilters(
        filters=[
            MetadataFilter(
                key="file_path", value=file_path, operator=FilterOperator.EQ
            )  # file_path = file path
        ]
    )
    vector_store = index.storage_context.vector_store

    nodes = vector_store.query(
        query_vector=None,  # No vector similarity search
        limit=None,  # No limit
        filters=filters  # Apply filters to get specific file chunks
    )

    print(f"Retrieved {len(nodes)} nodes for file: {file_path}")

    return nodes


def find_by_metadata(file: FileNode, index: VectorStoreIndex) -> list[TextNode]:

    client = index.vector_store.client
    print("---- Querying Directly From Milvus Collection ----")
    print("Running query:")
    print(
        f'file_path == "{file.file_path}" AND file_last_updated_at != "{file.file_last_updated_at}"')
    results = client.query(
        collection_name="source_code_collection",
        # No quotes!
        filter=f'file_path == "{file.file_path}" AND file_last_updated_at != {file.file_last_updated_at}',
        output_fields=["text", "_node_content"],
        limit=1000
    )
    if not results:
        print(f"No results found for file: {file.file_path}")
        return []
    pprint(results[0]["_node_content"])
    print(f"Found {len(results)} results for file: {file.file_path}")

    # Convert to TextNode objects
    text_nodes = [
        TextNode(
            text=(nc := json.loads(r["_node_content"]))["text"],
            metadata=nc["metadata"]
        )
        for r in results
    ]

    return text_nodes


def insert_data(file_data: list[FileNode], index: VectorStoreIndex):
    if not file_data:
        print("No files to process")
        return False

    client = index.vector_store.client
    nodes_to_insert = []
    delete_batch = []

    for file in file_data:
        # Single query for both checking and gathering deletable nodes
        results = client.query(
            collection_name="source_code_collection",
            filter=f'file_path == "{file.file_path}"',
            output_fields=["_node_content", "file_last_updated_at"],
            limit=1000
        )

        needs_insert = True
        current_nodes = []

        for r in results:
            node_content = json.loads(r["_node_content"])
            # Check if exact same file version exists
            if float(r["file_last_updated_at"]) == file.file_last_updated_at:
                needs_insert = False
                break
            current_nodes.append(node_content["id_"])

        if needs_insert:
            if current_nodes:
                delete_batch.extend(current_nodes)
            nodes_to_insert.extend(file.nodes)

    # Batch process deletions and inserts
    if delete_batch:
        print("---- Deleting Nodes ----")
        print(f"Deleting {len(delete_batch)} nodes")
        index.delete_nodes(node_ids=delete_batch)
    if nodes_to_insert:
        print("---- Inserting Nodes ----")
        print(f"Inserting {len(nodes_to_insert)} nodes")
        index.insert_nodes(nodes_to_insert)

    return bool(delete_batch or nodes_to_insert)


def is_insertion_required(file_path: str, file_data: list[dict], index: VectorStoreIndex) -> bool:

    # a stored node is a chunk and metadata
    stored_nodes = get_file_nodes(file_path, index)
    new_chunks = []
    for file in file_data:
        if file['file_path'] == file_path:
            for i, chunk in enumerate(file['chunks']):
                new_chunks.append()

    if len(stored_nodes) == len(new_chunks):
        # the lengths are the same, we need to compare each chunk
        for i, stored_node in stored_nodes:
            if (stored_node[i]['chunk'] != new_chunks[i]):
                # there is a difference, we need to update the stored node with the new chunk
                print(f"Updating chunk {i + 1} for file {file_path}")
                index.update_ref_doc()
