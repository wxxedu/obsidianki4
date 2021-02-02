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
	
	archive_folder_input = settings.get_settings_by_name("archive folder")
	if archive_folder_input == "":
		pass
	elif archive_folder_input.find("\n") != -1:
		archive_folders = archive_folder_input.split("\n")
	else:
		archive_folders = [archive_folder_input]
	
	is_in_archive_folder = False
	
	for archive_folder in archive_folders:
		archive_folder = archive_folder.lstrip(" ")
		archive_folder = archive_folder.rstrip(" ")
		archive_folder = "/" + archive_folder
		if file.get_file_relative_path().startswith(archive_folder) and archive_folder != "" and archive_folder != "\n":
			is_in_archive_folder = True
	
	if file.get_file_relative_path().startswith("/.trash"):
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
	elif is_in_archive_folder: # or file.get_file_root_folder() == settings.get_settings_by_name("ignore folder")
		uid = file.get_file_uid()
		note_list = mw.col.find_notes(uid)
		if len(note_list) > 0:
			for single_note_id in note_list:
				single_note = mw.col.getNote(single_note_id)
				if single_note["UID"] == uid:
					mw.col.remNotes([single_note_id])
	else:
		deck_id = mw.col.decks.id(file.get_deck_name())
		mw.col.decks.select(deck_id)
		card_model = mw.col.models.byName("Obsidianki4")
		uid = file.get_file_uid()
		note_list = mw.col.find_notes(uid)
		found_exisiting_file = False
		if len(note_list) > 0:
			for single_note_id in note_list:
				single_note = mw.col.getNote(single_note_id)
				if single_note.model() == card_model:
					if single_note["UID"] == uid:
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
						try:
							card_ids = mw.col.card_ids_of_note(single_note_id)
							mw.col.set_deck(card_ids, deck_id)
						except AttributeError:
							card_ids = mw.col.find_cards(uid)
							mw.col.decks.setDeck(card_ids, deck_id)
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
				note_object["UID"] = uid
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
		deck_id= int(name_and_id_segments[0].split(": ")[1])
		
		if deck_has_cards(deck_id):
			mw.col.decks.rem(deck_id, True, True)
			
def empty_trash():
	path_s = settings.get_settings_by_name("vault path")
	
	if path_s == "":
		pass
	elif path_s.find("\n"):
		paths = path_s.split("\n")
	else:
		paths = [paths]
	
	for path in paths:
		path = path.lstrip(" ")
		path = path.rstrip(" ")
		# TODO: Add this to settings
		if path != "":
			trash_can_path = path + "/" + ".trash"
			try:
				trash_directories = os.listdir(trash_can_path)
				for trash_directory in trash_directories:
					trash_directory_path = trash_can_path + "/" + trash_directory
					try:
						shutil.rmtree(trash_directory_path)
					except NotADirectoryError:
						os.remove(trash_directory_path)
			except NotADirectoryError:
				pass
		
def deck_has_cards(deck_id):
	if deck_id != 1:
		try:
			if mw.col.decks.card_count(deck_id, True) == 0:
				return True
		except AttributeError:
			cids = mw.col.decks.cids(deck_id, True)
			if len(cids) == 0:
				return True
	return False