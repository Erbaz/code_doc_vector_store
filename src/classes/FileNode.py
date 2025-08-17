from llama_index.core.schema import TextNode
from llama_index.core.text_splitter import CodeSplitter
import os


FILE_TYPE_MAPPING = {
    '.py': 'python',
    '.js': 'javascript'
}


class FileNode():

    def __init__(self, file_path: str) -> None:
        print("---- FileNode Initialization ----")
        file_path = file_path.replace("\\", "/")
        print(f"Processing file: {file_path}")
        self.file_path = file_path
        self.file_type = ""
        self.tot_lines = 0
        self.tot_chars = 0
        self.nodes: list[TextNode] = []
        self._generate_text_nodes(file_path)
        self.file_last_updated_at = os.path.getmtime(file_path)
        self.number_of_nodes = len(self.nodes)

    def _generate_text_nodes(self, file_path: str) -> list[TextNode]:
        try:
            print("---- Generating Text Nodes for File ----")
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in FILE_TYPE_MAPPING:
                raise ValueError(f"Unsupported file type: {ext}")
            source_code = ''
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            text_nodes: list[TextNode] = []

            chunk_lines = 24
            chunk_lines_overlap = 4
            max_chars = 1024

            code_splitter = CodeSplitter(
                language=FILE_TYPE_MAPPING[ext], chunk_lines=chunk_lines, chunk_lines_overlap=chunk_lines_overlap, max_chars=max_chars)

            # Usage:
            ast_chunks = code_splitter.split_text(source_code)

            final_chunks = []
            for chunk in ast_chunks:
                lines = chunk.split('\n')
                for i in range(0, len(lines), chunk_lines - chunk_lines_overlap):
                    new_chunk = '\n'.join(lines[i:i + chunk_lines])
                    final_chunks.append(new_chunk)

            for i, chunk in enumerate(final_chunks):
                text_node = TextNode(
                    text=chunk,
                    metadata={
                        "file_path": file_path,
                        "chunk_index": i + 1,
                        "chunk_char_length": len(chunk),
                        "chunk_line_length": len(chunk.split('\n')),
                        "is_last_chunk": i == len(final_chunks) - 1,
                        "file_last_updated_at": os.path.getmtime(file_path)
                    }
                )
                text_nodes.append(text_node)

        except Exception as e:
            print(f"Error processing document {i}: {e}")
            raise Exception("Error in File Node generation") from e

        self.nodes = text_nodes
        self.file_type = FILE_TYPE_MAPPING[ext]
        self.tot_lines = len(source_code.split('\n'))
        self.tot_chars = len(source_code)
