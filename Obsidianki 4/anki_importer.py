#!/usr/bin/env python3
import os
import shutil
from . import settings
from aqt import mw
from anki.cards import Card
from anki.notes import Note
from anki.collection import Collection
from aqt.utils import showInfo

def importer(my_files_catalog):
	for file in my_files_catalog:
		importer_to_anki(file)
	empty_trash()
	delete_empty_decks()
	
def importer_to_anki(file):
	if file.get_file_root_folder() == "Trash":
		uid = file.get_file_uid()
		note_list = mw.col.find_notes(uid)
		if len(note_list) > 0:
			for single_note_id in note_list:
				single_note = mw.col.getNote(single_note_id)
				try:
					if single_note["UID"] == uid:
						mw.col.remNotes([single_note_id])
				except KeyError:
					pass
#		os.remove(file.get_file_full_path())
	else:
		deck_id = mw.col.decks.id(file.get_deck_name())
		mw.col.decks.select(deck_id)
		card_model = mw.col.models.byName("Obsidianki4")
		note_list = mw.col.find_notes(file.get_file_uid())
		found_exisiting_file = False
		if len(note_list) > 0:
			for single_note_id in note_list:
				single_note = mw.col.getNote(single_note_id)
				if single_note.model() == card_model:
					if single_note["UID"] == file.get_file_uid():
						if file.get_cloze_or_basic():
							single_note["Cloze"] = file.get_file_content()
							single_note["Text"] = ""
						else:
							single_note["Cloze"] = "{{c1::}}"
							single_note["Text"] = file.get_file_content()
							
						back_extra = "Source: " + file.get_file_name_with_url()
						single_note["Back Extra"] = back_extra
						
						single_note.tags = []
						for tag in file.get_tags():
							single_note.tags.append(tag)
						
						card_ids = mw.col.card_ids_of_note(single_note_id)
						mw.col.set_deck(card_ids, deck_id)
						single_note.flush()
						found_exisiting_file = True
		if not found_exisiting_file:
			try:
				deck = mw.col.decks.get(deck_id)
				deck["mid"] = card_model["id"]
				mw.col.decks.save(deck)
				note_object = mw.col.newNote(deck_id)
				if file.get_cloze_or_basic():
					note_object["Cloze"] = file.get_file_content()
					note_object["Text"] = ""
				else:
					note_object["Cloze"] = "{{c1::}}"
					note_object["Text"] = file.get_file_content()
				note_object["UID"] = file.get_file_uid()
				back_extra = "Source: " + file.get_file_name_with_url()
				note_object["Back Extra"] = back_extra
				for tag in file.get_tags():
					note_object.tags.append(tag)
				
				mw.col.add_note(note_object, deck_id)
			except TypeError:
				pass

def delete_empty_decks():
	names_and_ids = mw.col.decks.all_names_and_ids()
	for name_and_id in names_and_ids:
		# I could not find what type this object is, so the only way for me to do it now is to use the string.
		name_and_id_segments = str(name_and_id).split("\n")
		id = int(name_and_id_segments[0].split(": ")[1])
		if id != 1 and mw.col.decks.card_count(id, True) == 0:
			mw.col.decks.rem(id, True, True)
			
def empty_trash():
	path = settings.get_settings_by_name("vault path")
	# TODO: Add this to settings
	trash_can_path = path + "/" + "Trash"
	trash_directories = os.listdir(trash_can_path)
	for trash_directory in trash_directories:
		trash_directory_path = trash_can_path + "/" + trash_directory
		shutil.rmtree(trash_directory_path)