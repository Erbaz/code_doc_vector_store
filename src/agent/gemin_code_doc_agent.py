
from llama_index.core.tools import FunctionTool
from llama_index.llms.gemini import Gemini
import os
from agent.sys_prompt import SYS_PROMPT
from llama_index.core.agent.workflow import ReActAgent, AgentStream, ToolCallResult
from llama_index.core.workflow import Context
from classes.Milvus import Milvus


class GeminiCodeDocumentationReActAgent():
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.milvus = None
        self.agent = None
        self.ctx = None

    def connect_milvus(self, milvus: Milvus):
        self.milvus = milvus
        self.milvus.connect()

    def initialize_agent(self, model_name: str):
        print("----- Initializing Gemini Code Documentation Agent -----")

        def _retrieve_codes_from_vector_database(query: str = None, file_path: str = None):
            print(f"Params: {query}, {file_path}")
            text_nodes = self.milvus.retrieve_nodes(
                query=query, file_path=file_path)
            codes = ""
            for i, node in enumerate(text_nodes):
                codes += f"Node # {i + 1}\n{node.text}\n {node.metadata} \n"

            print(f"---- List Of Codes ----")
            print(f"{codes}")

            return codes

        self.agent = ReActAgent(
            system_prompt=SYS_PROMPT,
            llm=Gemini(
                model=model_name,
                api_key=self.api_key,
            ),
            tools=[
                FunctionTool.from_defaults(
                    fn=_retrieve_codes_from_vector_database,
                    name="retrieve_codes_from_vector_database",
                    description="""
                        pass one of or both of input params - query, and file_path. 
                        You must provide one of the params. 
                        If only file_path is provided, all code for that file is retrieved. 
                        If query is provided, a vector search is performed.
                        If both are provided, then a vector search is performed with the query and file_path as a filter.
                    """)
            ]
        )
        self.ctx = Context(self.agent)

    async def invoke(self, user_query: str = None, file_path: str = None):
        """
            User query will include either the file path, or the function name or semantic words.
            The agent will need to deduce based on user query as to which tool to use to retrieve the relevant nodes.
        """

        formatted_query = f"User query: {user_query}\nFile path: {file_path}" if file_path else f"User query: {user_query}"

        handler = self.agent.run(user_msg=formatted_query, ctx=self.ctx)

        async for ev in handler.stream_events():
            # if isinstance(ev, ToolCallResult):
            #     print(f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}")
            if isinstance(ev, AgentStream):
                print(f"{ev.delta}", end="", flush=True)

        response = await handler

        print(str(response))

        return response
