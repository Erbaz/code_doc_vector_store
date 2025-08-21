from llama_index.core.schema import TextNode
from llama_index.core.tools import FunctionTool
from classes.Milvus import Milvus
from main import milvus_instance

"""
    Tools for the Gemini agent.
    1. Read file entry point or function based on user query
       For example, if user query is "How to use this function?", then first retrieve from vector store, all places where this function is used.
       If user asks to document a flow, then read the entry file provided by user and construct relevant query to retrieve nodes that help in the documentation.
    2. Read over the nodes and check if information is relevant and sufficient. If not, try to fetch more nodes based on metdata filters, and cleaner queries
    3. Generate a summary based on user query using node metadata and reasoning
"""


def retrieve_codes_from_vector_database(query: str = None, file_path: str = None) -> list[TextNode]:
    """
    Function to retrieve code nodes from the vector database based on user query and/or file path.
    One of the two will need to be provided
    """
    return milvus_instance.retrieve_nodes(query=query, file_path=file_path)


tools = [FunctionTool().from_defaults(
    fn=retrieve_codes_from_vector_database, description="""
    pass one of or both of input params - query, and file_path. 
    You must set provide one of the params. 
    If only file_path is provided, all code for that file is retrieved. 
    If query is provided, a vector search is performed.
    If both are provided, then a vector search is performed with the query and file_path as a filter.
    """)]
