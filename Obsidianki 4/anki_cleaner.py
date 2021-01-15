#!/usr/bin/env python3
from . import os
from aqt import mw
from anki.cards import Card
from anki.notes import Note
from anki.collection import Collection
from aqt.utils import showInfo

deleted_files_folder_name = "Trash"

def anki_cleaner(vault_path: str):
	delete_empty_decks()
	delete_empty_decks(vault_path)

def delete_empty_decks():
	names_and_ids = mw.col.decks.all_names_and_ids()
	for name_and_id in names_and_ids:
		# I could not find what type this object is, so the only logical way for me to do it now is to use the string.
		name_and_id_segments = str(name_and_id).split("\n")
		id = int(name_and_id_segments[0].split(": ")[1])
		if id != 1 and mw.col.decks.card_count(id, True) == 0:
			mw.col.decks.rem(id, True, True)

def delete_empty_decks(vault_path: str):
	# ======================================================
	# | TODO: Make this thing customizable in the settings |
	# ======================================================
	
	os.listdir(vault_path + "/" + deleted_files_folder_name)
	
	pass

		
		
