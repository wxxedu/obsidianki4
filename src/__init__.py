#!/usr/bin/env python3
import os
from . import files
from . import settings
from . import obsidian_url
from . import anki_importer
import aqt
from aqt import mw
from aqt import AnkiQt, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo
from aqt.utils import tooltip
from PyQt5 import QtWidgets, QtCore


def read_files(root_path, relative_path):
	files_catalog = []
	if relative_path == "":
		paths = os.listdir(root_path)
	else:
		paths = os.listdir(root_path + "/" + relative_path)
	for path in paths:
		foler_is_ignored = False
		ignore_folder_s = settings.get_settings_by_name("ignore folder")
		
		if ignore_folder_s == "":
			pass
		elif ignore_folder_s.find("\n") != -1:
			ignore_folders = ignore_folder_s.split("\n")
		else:
			ignore_folders = [ignore_folder_s]
		
		for ignore_folder in ignore_folders:
			ignore_folder = ignore_folder.lstrip(" ")
			ignore_folder = ignore_folder.rstrip(" ")
			ignore_folder = "/" + ignore_folder
			if relative_path.startswith(ignore_folder):
				foler_is_ignored = True
		
		if path.find(".") != -1 and path.split(".")[-1] != "md" and path != ".trash":
			pass
		elif foler_is_ignored:
			pass
		elif path.endswith(".md"):
			new_path = relative_path + "/" + path
			new_file = files.File(root_path, new_path)
			files_catalog.append(new_file)
		else:
			try: 
				new_path = relative_path + "/" + path
				files_catalog = files_catalog + read_files(root_path, new_path)
			except NotADirectoryError:
				pass
	return files_catalog

def get_bool(status_text):
	return status_text == "True" or status_text == "true"

def get_text(status_bool):
	if status_bool:
		return "True"
	else: 
		return "False"

class ObsidiankiSettings(QDialog):
	def __init__(self, mw):
		super().__init__(mw)
		
		
		layout = QFormLayout(self)
		
		
		self.vault_path = QPlainTextEdit(self)
		self.templates_folder = QPlainTextEdit(self)
		self.archive_folder = QPlainTextEdit(self)
		
		
		self.mode = QLineEdit(self)
		self.type = QLineEdit(self)
		
		
		self.bold = QCheckBox(self)
		self.highlight = QCheckBox(self)
		self.italics = QCheckBox(self)
		self.image = QCheckBox(self)
		self.quote = QCheckBox(self)
		self.QuestionOrAnswer = QCheckBox(self)
		self.list = QCheckBox(self)
		self.inline_code = QCheckBox(self)
		self.block_code = QCheckBox(self)
		self.convert_button = QPushButton("Save and Convert")
		self.save_button = QPushButton("Save and Close")
		
		
		layout.addRow(QLabel("Vault Path: "))
		layout.addRow(QLabel("(Please use forward slashes for your vault path)"))
		layout.addRow(self.vault_path)
		
		layout.addRow(QLabel("Ignore Folders: "))
		layout.addRow(QLabel("(Notes in Anki in this obsidian folder will be ignored)"))
		layout.addRow(self.templates_folder)
		
		layout.addRow(QLabel("Archive Folder Name: "))
		layout.addRow(self.archive_folder)
		layout.addRow(QLabel("Anki Cards in this folder will be deleted"))
		
		
		layout.addRow(QLabel("Mode: "), self.mode)
		layout.addRow(QLabel("Mode: choose from word/line/heading/document"))
		layout.addRow(QLabel("Type: "), self.type)
		layout.addRow(QLabel("Type: choose from cloze/basic"))
		
		
		layout.addRow(QLabel("Bold to Cloze: "), self.bold)
		layout.addRow(QLabel("Italics to Cloze: "), self.italics)
		layout.addRow(QLabel("Highlight to Cloze: "), self.highlight)
		layout.addRow(QLabel("Image to Cloze: "), self.image)
		layout.addRow(QLabel("Quote to Cloze: "), self.quote)
		layout.addRow(QLabel("QA to Cloze"), self.QuestionOrAnswer)
		layout.addRow(QLabel("List to Cloze"), self.list)
		layout.addRow(QLabel("Inline Code to Cloze"), self.inline_code)
		layout.addRow(QLabel("Block Code to Cloze"), self.block_code)
		
		
		layout.addRow(self.save_button, self.convert_button)
		
		
		self.vault_path.setPlainText(settings.get_settings_by_name("vault path"))
		self.templates_folder.setPlainText(settings.get_settings_by_name("ignore folder"))
		self.archive_folder.setPlainText(settings.get_settings_by_name("archive folder"))
		
		
		self.mode.setText(settings.get_settings_by_name("mode"))
		self.type.setText(settings.get_settings_by_name("type"))
		
		
		self.bold.setChecked(get_bool(settings.get_settings_by_name("bold")))
		self.italics.setChecked(get_bool(settings.get_settings_by_name("italics")))
		self.highlight.setChecked(get_bool(settings.get_settings_by_name("highlight")))
		self.image.setChecked(get_bool(settings.get_settings_by_name("image")))
		self.quote.setChecked(get_bool(settings.get_settings_by_name("quote")))
		self.QuestionOrAnswer.setChecked(get_bool(settings.get_settings_by_name("QA")))
		self.list.setChecked(get_bool(settings.get_settings_by_name("list")))
		self.inline_code.setChecked(get_bool(settings.get_settings_by_name("inline code")))
		self.block_code.setChecked(get_bool(settings.get_settings_by_name("block code")))
		
		
		self.convert_button.setDefault(True)
		self.convert_button.clicked.connect(self.onOk)
		self.save_button.clicked.connect(self.onSave)
		self.show()
		
	def onOk(self):
		newSettings = {}
		newSettings["vault path"] = self.vault_path.toPlainText()
		newSettings["ignore folder"] = self.templates_folder.toPlainText()
		# newSettings["trash folder"] = self.trash_folder.text()
		newSettings["archive folder"] = self.archive_folder.toPlainText()
		newSettings["mode"] = self.mode.text()
		newSettings["type"] = self.type.text()
		newSettings["bold"] = get_text(self.bold.isChecked())
		newSettings["highlight"] = get_text(self.highlight.isChecked())
		newSettings["italics"] = get_text(self.italics.isChecked())
		newSettings["image"] = get_text(self.image.isChecked())
		newSettings["quote"] = get_text(self.quote.isChecked())
		newSettings["QA"] = get_text(self.QuestionOrAnswer.isChecked())
		newSettings["list"] = get_text(self.list.isChecked())
		newSettings["inline code"] = get_text(self.inline_code.isChecked())
		newSettings["block code"] = get_text(self.block_code.isChecked())
		settings.save_settings(newSettings)
		
		###############################################################################################################################
		###############################################################################################################################
		###############################################################################################################################
		
		if self.vault_path.toPlainText().find("\n") != -1:
			vault_paths = self.vault_path.toPlainText().split("\n")
		else:
			vault_paths = [self.vault_path.toPlainText()]
			
		for a_vault_path in vault_paths:
			showInfo(a_vault_path)
			if a_vault_path != "":
				my_files_catalog = read_files(a_vault_path, "")
		
		length_of_files = len(my_files_catalog)
		for i in range(0, length_of_files):
			my_files_catalog[i].set_file_content(obsidian_url.process_obsidian_file(my_files_catalog[i].file_content, my_files_catalog))
		
		anki_importer.importer(my_files_catalog)
		
		###############################################################################################################################
		###############################################################################################################################
		###############################################################################################################################
		
		mw.update()
		mw.reset(True)

		self.close()
		
	def onSave(self):
		newSettings = {}
		newSettings["vault path"] = self.vault_path.toPlainText()
		newSettings["ignore folder"] = self.templates_folder.toPlainText()
		newSettings["archive folder"] = self.archive_folder.toPlainText()
		
		newSettings["mode"] = self.mode.text()
		newSettings["type"] = self.type.text()
		newSettings["bold"] = get_text(self.bold.isChecked())
		newSettings["highlight"] = get_text(self.highlight.isChecked())
		newSettings["italics"] = get_text(self.italics.isChecked())
		newSettings["image"] = get_text(self.image.isChecked())
		newSettings["quote"] = get_text(self.quote.isChecked())
		newSettings["QA"] = get_text(self.QuestionOrAnswer.isChecked())
		newSettings["list"] = get_text(self.list.isChecked())
		newSettings["inline code"] = get_text(self.inline_code.isChecked())
		newSettings["block code"] = get_text(self.block_code.isChecked())
		settings.save_settings(newSettings)
		self.close()
		
action = QAction("Obsidianki 4", aqt.mw)
action.triggered.connect(lambda: ObsidiankiSettings(aqt.mw))

aqt.mw.form.menuTools.addAction(action)