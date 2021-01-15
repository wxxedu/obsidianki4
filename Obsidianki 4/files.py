#!/usr/bin/env python3
from aqt import mw
from aqt.utils import showInfo
from . import processor

def gen_obsidian_url(vault_name, file_url):
    vault_url = "obsidian://open?vault=" + my_encode(vault_name)
    file_url = "&file=" + my_encode(file_url)
    return vault_url + file_url


def my_encode(string:str):
    string = str(string.encode("utf-8"))
    string = string.replace("\\x", "%")
    string = string.replace(" ", "%20")
    string = string.replace("/", "%2F")
    string = string.lstrip("\'b")
    string = string.rstrip("\'")
    string = capitalize_unicode(string)
    return string


def capitalize_unicode(string):
    new = []
    position = -5
    for index in range(0, len(string)):
        if string[index] == "%":
            position = index
            new.append(string[index])
        elif index == position + 1 or index == position + 2:
            new.append(string[index].capitalize())
        else:
            new.append(string[index])
    return "".join(new)


class File:
    # important parameters
    file_name = ""
    vault_path = ""
    relative_path = ""
    full_path = ""
    uid = ""
    file_content = ""
    cloze_or_basic = True
    obsidian_url = ""
    metadata = {}

    def __init__(self, vault_path, relative_path):
        self.vault_path = vault_path
        self.relative_path = relative_path
        self.full_path = self.vault_path + "/" + self.relative_path
        tmp = processor.read_file(self.full_path)
        self.uid = tmp[0]
        self.file_content = tmp[1]
        self.cloze_or_basic = tmp[2]
        self.metadata = tmp[3]
        self.obsidian_url = self.generate_obsidian_url()
        self.file_name = self.generate_file_name()
        
    
    def get_deck_name(self):
        root_name = self.vault_path.split("/")[-1]
        sublevel_name_segments = self.relative_path.split("/")[:-1]
        sublevel_name = "::".join(sublevel_name_segments)
        deck_name = root_name + sublevel_name
        return deck_name
    
    def get_file_root_folder(self):
        tmp = self.relative_path.lstrip("/")
        root_folder = tmp.split("/")[0]
        return root_folder
    
    def get_file_full_path(self):
        return self.full_path
    
    
    def generate_obsidian_url(self):
        vault_name = self.vault_path.split("/")[-1]
        file_url_segments = self.relative_path.split(".")[:-1]
        file_url = ".".join(file_url_segments)
        return gen_obsidian_url(vault_name, file_url)
    
    
    def get_obsidian_url(self):
        return self.obsidian_url
    
    
    def generate_file_name(self):
        file_name = self.relative_path.split("/")[-1]
        file_name_segments = file_name.split(".")[:-1]
        file_name = ".".join(file_name_segments)
        return file_name
    
    
    def get_file_name(self):
        return self.file_name
    
    
    def get_file_name_with_url(self):
        url = self.get_obsidian_url()
        name = self.get_file_name()
        name_with_url = "<a href =\""+ url + "\">" + name + "</a>"
        return name_with_url
    
    
    def get_file_uid(self):
        return self.uid
    
    
    def get_cloze_or_basic(self):
        return self.cloze_or_basic
    
    
    def set_file_content(self, file_content):
        self.file_content = file_content
        
    
    def get_file_content(self):
        return self.file_content
    
    
    def get_tags(self):
        tag_line = "[]"
        try:
            tag_line = self.metadata["tags"]
        except:
            pass
        tag_line = tag_line.lstrip("[")
        tag_line = tag_line.rstrip("]")
        if tag_line.find("/"):
            tag_line = tag_line.replace("/", "::")
        tags = tag_line.split(",")
        for i in range(0, len(tags)):
            tags[i] = tags[i].lstrip(" ")
            tags[i] = tags[i].rstrip(" ")
            tags[i] = tags[i].replace(" ", "_")
        return tags