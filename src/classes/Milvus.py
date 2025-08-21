import os
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core.schema import TextNode
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)
import json


class Milvus():
    def __init__(self):
        print("---- Milvus Initialization ----")
        self.storage_ctx = None
        self.vector_store = None
        self.index = None
        self.embed_model = None

    def connect(self):
        self.vector_store = MilvusVectorStore(
            uri=os.getenv("MILVUS_URI"),
            token=os.getenv("MILVUS_TOKEN"),
            collection_name="source_code_collection",
            dim=768,  # Vector dimension depends on the embedding model
            overwrite=False,  # Drop collection if exists
        )
        self.storage_ctx = StorageContext.from_defaults(
            vector_store=self.vector_store)

        self.embed_model = GeminiEmbedding(
            model_name="models/embedding-001",  # Default Gemini embedding model
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.storage_context.vector_store,
            embed_model=self.embed_model,
            transformations=[],  # do not apply any transformations
            show_progress=True
        )

        print("----- Milvus Connected And Index Set Up-----")

    def retrieve_nodes(self, query: str = None, file_path: str = None) -> list[TextNode]:

        if (query is None and file_path is None):
            return []
        if (query is None):
            # query all nodes for the file
            nodes = self._get_all_nodes_of_file(file_path)
            return nodes
        filters = None
        if (file_path is None):
            filters = MetadataFilters(
                filters=[
                    MetadataFilter(
                        key="file_path", value=file_path, operator=FilterOperator.EQ
                    )  # file_path = file path
                ]
            )

        retriever = self.index.as_retriever(
            similarity_top_k=10, filters=filters)

        nodes = retriever.retrieve()

        print(f"Retrieved {len(nodes)} nodes for file: {file_path}")

        return nodes

    def _get_all_nodes_of_file(self, file_path: str) -> list[TextNode]:
        client = self.vector_store.client
        print("---- Querying Directly From Milvus Collection ----")
        print("Running query:")
        print(
            f'file_path == "{file_path}"')
        results = client.query(
            collection_name="source_code_collection",
            filter=f'file_path == "{file_path}"',
            output_fields=["text", "_node_content"],
            limit=1000
        )
        if not results:
            print(f"No results found for file: {file_path}")
            return []
        print(f"Found {len(results)} results for file: {file_path}")

        # Convert to TextNode objects
        text_nodes = [
            TextNode(
                text=(nc := json.loads(r["_node_content"]))["text"],
                metadata=nc["metadata"]
            )
            for r in results
        ]

        return text_nodes
