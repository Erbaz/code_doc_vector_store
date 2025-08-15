from code_splitter import generate_text_nodes
from milvus import milvus_config, set_milvus_index
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings

from typing import List, Dict

from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)
import os
from dotenv import load_dotenv

load_dotenv()


# File extension to type mapping
FILE_TYPE_MAPPING = {
    '.py': 'python',
    '.js': 'javascript'
}


def read_code_files(folder_path: str) -> List[Dict]:
    """
    Reads .py and .js files from a folder and returns a list of dictionaries with:
    - source_code: Full content of the file
    - file_path: Full path to the file
    - file_type: Language based on extension
    - tot_lines: Total lines in file
    - tot_chars: Total characters in file
    - chunks: List of chunks from generate_text_nodes()
    """
    file_dicts = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in FILE_TYPE_MAPPING:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()

                    file_dicts.append({
                        'source_code': source_code,
                        'file_path': file_path,
                        'file_type': FILE_TYPE_MAPPING[ext],
                        'tot_lines': len(source_code.splitlines()),
                        'tot_chars': len(source_code),
                        'chunks': generate_text_nodes(source_code, file_path, language=FILE_TYPE_MAPPING[ext])
                    })
                except Exception as e:
                    print(f"Skipping {file_path} due to error: {e}")

    return file_dicts


def main():
    # Step 1: load a file source code as text

    file_path = r"C:\Users\pc\Desktop\llama-index-code-splitter\code-splitter-poetic\target\source.py"

    with open(file_path, 'r', encoding='utf-8') as file:
        source_code = file.read()

    # Step 2: use CodeSplitter to split the code
    text_nodes = generate_text_nodes(source_code, file_path)

    ctx = milvus_config()

    index = set_milvus_index(ctx)

    query_engine = index.as_retriever(similarity_top_k=2)

    print("Index created successfully! Query engine is ready.")
    user_query = input("Enter your query: ")

    res = query_engine.retrieve(user_query)

    for node in res:
        print(f"Relevance: {node.score:.2f}")
        print(node.text + "\n---")


if __name__ == "__main__":
    # llm = Gemini(
    #     model="models/gemini-1.5-flash",
    #     # uses GOOGLE_API_KEY env var by default
    #     api_key=os.getenv("GEMINI_API_KEY"),
    # )
    # Settings.llm = llm
    # main()
    files_data = read_code_files(
        r"C:\Users\pc\Desktop\llama-index-code-splitter\code-splitter-poetic\target")
    for file_data in files_data:
        print(f"Processed {file_data['file_path']}")
        print(f"Type: {file_data['file_type']}")
        print(f"Lines: {file_data['tot_lines']}")
        print(f"Chars: {file_data['tot_chars']}")
        print(f"Chunks: {len(file_data['chunks'])}")
