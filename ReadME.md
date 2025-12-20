## Goal

This project uses Llama-index, to build a ReAct agentic orchestration to build a simple AI assistant that helps to query the source code using RAG and answer user question. Can be used for code review, to provide suggestions, or understanding the source code.
This project uses Zilliz cloud as the vector database for RAG.
LLMs supported: Gemini, and any local Ollama model

## Setup
- Use `poetry install` to install dependencies. 
- Create `.env` to set environment variables - use `.env.sample` to set it up
- The project has a sample target folder. To use it, you should set complete system path to the target folder into `FILE_PATH` but if you set the `FILE_PATH` variable to another desired folder, then the project will use that path as the target.
- run the main.py to start 

Note: Only Javascript and Python files will be chunked and embedded to the vector store. No other file types are supported.

## Demo



https://github.com/user-attachments/assets/80ae608c-5668-45ab-9fc5-6e76247c3bd3


