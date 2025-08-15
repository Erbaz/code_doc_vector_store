import datetime
from typing import List


def create_report_file() -> str:
    """Creates a new markdown report file with timestamped name.
    Returns the file path of the created file."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"report_{timestamp}.md"


def generate_report(chunks: List[str], chunk_lines: int, chunk_lines_overlap: int, max_chars: int) -> str:
    """Generates a markdown report of code chunks with parameters."""
    filename = create_report_file()

    with open(filename, 'w', encoding='utf-8') as f:
        # Write header with parameters
        f.write(f"# Code Splitter Report\n\n")
        f.write(f"## Parameters\n")
        f.write(f"- Chunk lines: {chunk_lines}\n")
        f.write(f"- Chunk lines overlap: {chunk_lines_overlap}\n")
        f.write(f"- Max chars: {max_chars}\n")
        f.write(f"- Total chunks: {len(chunks)}\n\n")

        # Write each chunk
        f.write("## Chunks\n\n")
        for i, chunk in enumerate(chunks, 1):
            # Calculate number of lines in this chunk
            line_count = len(chunk.split('\n'))
            char_count = len(chunk)
            f.write(
                f"### CHUNK {i} ({line_count} lines and {char_count} characters)\n```python\n{chunk}\n```\n\n")

    return filename
