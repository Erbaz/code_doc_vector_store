from milvus import milvus_config, set_milvus_index, insert_data
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from classes.Milvus import Milvus

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
from agent.gemin_code_doc_agent import GeminiCodeDocumentationReActAgent

load_dotenv()


milvus_instance = Milvus()
milvus_instance.connect()


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
    agent_app = GeminiCodeDocumentationReActAgent()

    agent_app.connect_milvus(milvus_instance)
    agent_app.initialize_agent(model_name="models/gemini-1.5-flash")

    while True:
        user_query = input("Enter your query (or 'exit' to quit): ")
        if user_query.lower() == 'exit':
            break

        file_path = input(
            "Enter the file path (optional, press Enter to skip): ")
        file_path = file_path if file_path else None

        # Invoke the agent with the user query and optional file path
        response = await agent_app.invoke(user_query, file_path)


if __name__ == "__main__":
    llm = Gemini(
        model="models/gemini-1.5-flash",
        # uses GOOGLE_API_KEY env var by default
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    print("----- Gemini LLM Initialized -----")
    Settings.llm = llm
    asyncio.run(main())
