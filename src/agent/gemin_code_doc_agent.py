
from llama_index.llms.gemini import Gemini
import os
from sys_prompt import SYS_PROMPT
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context
from classes.Milvus import Milvus
from tools import tools


class GeminiCodeDocumentationReActAgent():
    def __init__(self, model_name: str, milvus: Milvus):
        self.model_name = model_name
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.agent = ReActAgent(
            system_prompt=SYS_PROMPT,
            llm=Gemini(
                model=model_name,
                api_key=self.api_key,
            ),
            tools=[tools]
        )
        self.ctx = Context(self.agent)

    def invoke(self, user_query: str, file_path: str = None):
        """
            User query will include either the file path, or the function name or semantic words.
            The agent will need to deduce based on user query as to which tool to use to retrieve the relevant nodes.
        """

        formatted_query = f"User query: {user_query}\nFile path: {file_path}" if file_path else f"User query: {user_query}"

        res = self.agent.run(input=formatted_query, ctx=self.ctx)
