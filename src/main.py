from milvus import milvus_config, set_milvus_index, insert_data
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from classes.Milvus import Milvus
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
from typing import List, Dict

from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)
import os
import asyncio
from dotenv import load_dotenv
from file_management import generate_file_nodes
from agent.code_doc_agent import CodeDocumentationReActAgent

load_dotenv()



def project_init():
    """
    Initialize the collection and index and insert documents without pre-checks
    Only run this for a new collection or when you want to reset everything.
    """
    ctx = milvus_config(overwrite=True)  # Overwrite existing collection
    index = set_milvus_index(ctx)
    folder_path = os.getenv("FILE_PATH")
    file_nodes = generate_file_nodes(folder_path)
    ctx = milvus_config()
    index = set_milvus_index(ctx)
    insert_data(file_data=file_nodes, index=index)


async def main():
    # Initialize the Gemini Agent
    agent_app = CodeDocumentationReActAgent()

    agent_app.connect_milvus(milvus_instance)
    agent_app.initialize_agent()

    project_init()

    while True:
        user_query = input("Enter your query (or 'exit' to quit): ")
        if user_query.lower() == 'exit':
            break

        file_path = input(
            "Enter the file path (optional, press Enter to skip): ")
        file_path = file_path if file_path else None

        # Invoke the agent with the user query and optional file path
        response = await agent_app.invoke(user_query, file_path)


milvus_instance = Milvus()
if __name__ == "__main__":
    print("Use Ollama?")
    user_input = input("Enter 'y' for yes or 'n' for no: ")
    use_ollama = user_input.lower() == 'y'

    if use_ollama:
        llm = Ollama(
            model="qwen3:4b",
            request_timeout=120.0,
            context_window=8000,
        )
        embed_model = OllamaEmbedding(
            model_name="qwen3-embedding:latest",
            base_url="http://localhost:11434",
        )
    else:
        llm = Gemini(
            model="models/gemini-2.0-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
        )
        embed_model = GeminiEmbedding(
            model_name="models/embedding-001",
            api_key=os.getenv("GEMINI_API_KEY"),
        )

    # ✅ Assign to Settings first
    Settings.llm = llm
    Settings.embed_model = embed_model

    # ✅ Now create Milvus and connect
    milvus_instance.connect()

    print("----- LLM Initialized -----")
    asyncio.run(main())
