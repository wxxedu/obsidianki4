#!/usr/bin/env python3
from typing import TextIO

from aqt import mw
from .markdown2 import markdown2
from .markdown2 import markdown2Mathjax
import html


# read and stores the content of the file, process it, and add to anki


def read_file(full_path=str) -> list:
    output = ""
    with open(full_path, mode="r", encoding="utf-8") as file:
        source = file.read()
        temporary_content = markdown2Mathjax.sanitizeInput(source)
        markdown_file = markdown2.markdown(temporary_content[0], extras = ["fenced-code-blocks", "metadata", "strike", "tables", "tag-friendly", "task_list", "break-on-newline", "footnotes"])
        metadata = markdown_file.metadata
        if len(metadata) == 0:
            markdown_file = markdown2.markdown(temporary_content[0], extras = ["fenced-code-blocks", "strike", "tables", "tag-friendly", "task_list", "break-on-newline", "footnotes"])
        for i in range(len(temporary_content[1])):
            temporary_content[1][i] = html.escape(temporary_content[1][i])
            temporary_content[1][i] = temporary_content[1][i].replace("{{", "{ {")
            temporary_content[1][i] = temporary_content[1][i].replace("}}", "} }")
            
        
        output = markdown2Mathjax.reconstructMath(markdown_file, temporary_content[1])
    return output




class File:
    # important parameters
    vault_path = str
    relative_path = str
    full_path = str
    file_content = str

    def __init__(self, vault_path, relative_path):
        self.vault_path = vault_path
        self.relative_path = relative_path
        self.full_path = self.vault_path + "/" + self.relative_path
        temporary_content = read_file(full_path=self.full_path)
        self.file_content = temporary_content[0]
    
    class Metadata:
        # gets the metadata for a file, and then determines how things are processed here in this file.
        def __init__(self, metadata=list):
            metadata
            
        def new_metadata():
            pass
            