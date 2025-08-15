from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.schema import TextNode
from dotenv import load_dotenv
import os

load_dotenv()


def milvus_config():
    print("Connecting to Milvus...")
    vector_store = MilvusVectorStore(
        uri="https://in03-890cd99e122622e.serverless.aws-eu-central-1.cloud.zilliz.com",
        token=os.getenv("MILVUS_TOKEN"),
        collection_name="code_collection",
        dim=768,  # Vector dimension depends on the embedding model
        overwrite=False,  # Drop collection if exists
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    return storage_context


def set_milvus_index(storage_context: StorageContext, nodes: list[TextNode] | None = None):
    print("Setting up Milvus index...")
    embed_model = GeminiEmbedding(
        model_name="models/embedding-001",  # Default Gemini embedding model
        api_key=os.getenv("GEMINI_API_KEY")
    )
    index = VectorStoreIndex.from_vector_store(
        nodes=nodes,
        vector_store=storage_context.vector_store,
        embed_model=embed_model
    )

    print("Index generated.")
    return index
