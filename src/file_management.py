import os
from classes.FileNode import FileNode


# For the purposes of this project, make sure only code files are processed. Do not allow other file types like images and text files.
FILE_TYPE_MAPPING = {
    '.py': 'python',
    '.js': 'javascript'
}


def generate_file_nodes(folder_path: str) -> list[FileNode]:

    nodes: list[FileNode] = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in FILE_TYPE_MAPPING:
                file_path = os.path.join(root, file)
                try:
                    file_node = FileNode(file_path)
                    nodes.append(file_node)
                except Exception as e:
                    print(f"Skipping {file_path} due to error: {e}")

    return nodes
