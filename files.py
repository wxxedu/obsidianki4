#!/usr/bin/env python3
from aqt import mw
from . import processor

class File:
    # important parameters
    vault_path = ""
    relative_path = ""
    full_path = ""
    uid = ""
    file_content = ""
    cloze_or_basic = True
    

    def __init__(self, vault_path, relative_path):
        self.vault_path = vault_path
        self.relative_path = relative_path
        self.full_path = self.vault_path + "/" + self.relative_path
        tmp = processor.read_file(self.full_path)
        self.uid = tmp[0]
        self.file_content = tmp[1]
        self.cloze_or_basic = tmp[2]
    
    def get_deck_name(vault_path, relative_path):
        
        pass
        
        
    
            