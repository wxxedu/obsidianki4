#!/usr/bin/env python3
from typing import TextIO

from aqt import mw
from .markdown2 import markdown2
from .markdown2 import markdown2Mathjax
from . import processor
import html

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
        temporary_content = processor.read_file(full_path=self.full_path)
        self.file_content = temporary_content[0]
    
    class Metadata:
        # gets the metadata for a file, and then determines how things are processed here in this file.
        def __init__(self, metadata=list):
            metadata
            
        def new_metadata():
            pass
            