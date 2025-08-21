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
from dotenv import load_dotenv
from file_management import generate_file_nodes

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


def main():

    folder_path = os.getenv("FILE_PATH")

    file_nodes = generate_file_nodes(folder_path)

    ctx = milvus_config()

    index = set_milvus_index(ctx)

    insert_data(file_data=file_nodes, index=index)

    query_engine = index.as_retriever(similarity_top_k=6)

    print("Index created successfully! Query engine is ready.")

    user_query = input("Enter your query: ")

    res = query_engine.retrieve(user_query)

    for node in res:
        print(f"Relevance: {node.score:.2f}")
        print(node.text + "\n---")


if __name__ == "__main__":
    llm = Gemini(
        model="models/gemini-1.5-flash",
        # uses GOOGLE_API_KEY env var by default
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    print("----- Gemini LLM Initialized -----")
    Settings.llm = llm
    main()
