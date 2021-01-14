#!/usr/bin/env python3
import os
import aqt
import pickle
from aqt.qt import *
from aqt import AnkiQt, gui_hooks
from aqt.utils import tooltip
from PyQt5 import QtWidgets, QtCore

default_settings = {
    "vault path": "/Users/xiuxuan/Knowledge Base",
    "mode": "heading",
    "type": "cloze",
    "bold": "True",
    "italics": "True",
    "image": "True",
    "quote": "False", # FIXME: fix the conflict of Quote with other clozes
    "QA": "True",
    "list": "True",
    "inline code": "True",
    "block code": "False",
    "highlight": "False"
}

SETTINGS_PATH = os.path.expanduser("~/.obsidianki4.settings")


def save_settings(settings, path=SETTINGS_PATH):
    with open(path, "wb") as fd:
        pickle.dump(settings, fd)


def load_settings(path=SETTINGS_PATH):
    if os.path.isfile(path):
        with open(path, "rb") as fd:
            return pickle.load(fd)
    return default_settings

def get_settings():
    settings = load_settings()
    return settings




