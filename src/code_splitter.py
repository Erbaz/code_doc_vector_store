from llama_index.core.schema import TextNode
from llama_index.core.text_splitter import CodeSplitter
from report_generator import generate_report


def postprocess_chunks(chunks: list[str], max_lines: int, overlap: int) -> list[str]:
    new_chunks = []
    for chunk in chunks:
        lines = chunk.split('\n')
        for i in range(0, len(lines), max_lines - overlap):
            new_chunk = '\n'.join(lines[i:i + max_lines])
            new_chunks.append(new_chunk)
    return new_chunks


def generate_text_nodes(source_code: str, file_path: str, language: str) -> list[TextNode]:
    chunk_lines = 24
    chunk_lines_overlap = 4
    max_chars = 1024
    code_splitter = CodeSplitter(
        language=language, chunk_lines=chunk_lines, chunk_lines_overlap=chunk_lines_overlap, max_chars=max_chars)

    # Usage:
    ast_chunks = code_splitter.split_text(source_code)
    final_chunks = postprocess_chunks(
        ast_chunks, max_lines=chunk_lines, overlap=chunk_lines_overlap)

    # generate_report(final_chunks, chunk_lines, chunk_lines_overlap, max_chars)

    text_nodes = []

    for i, chunk in enumerate(final_chunks):
        text_node = TextNode(
            text=chunk,
            metadata={
                "file_path": file_path,
                "chunk_index": i + 1,
                "chunk_char_length": len(chunk),
                "chunk_line_length": len(chunk.split('\n')),
                "is_last_chunk": i == len(final_chunks) - 1
            }
        )
        text_nodes.append(text_node)

    return text_nodes
