#!/usr/bin/env python3
import os
from . import files
from . import settings
import aqt
from aqt import AnkiQt, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo
from aqt.utils import tooltip
from PyQt5 import QtWidgets, QtCore

files_catalog = []

def read_files(vault_path, relative_path):
	try:
		if relative_path == "":
			paths = os.listdir(vault_path)
		else:
			paths = os.listdir(vault_path + "/" + relative_path)
		for path in paths:
			if path.find(".") != -1 and path.split(".")[-1] != "md":
				pass
			elif path.endswith(".md"):
				new_path = relative_path + "/" + path
				new_file = files.File(vault_path, new_path)
				files_catalog.append(new_file)
			else:
				new_path = relative_path + "/" + path
				read_files(vault_path, new_path)
	except FileNotFoundError:
		pass

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
		
		self.vault_path = QLineEdit(self)
		self.mode = QLineEdit(self)
		self.type = QLineEdit(self)
		self.bold = QCheckBox(self)
		self.italics = QCheckBox(self)
		self.image = QCheckBox(self)
		self.quote = QCheckBox(self)
		self.QuestionOrAnswer = QCheckBox(self)
		self.list = QCheckBox(self)
		self.inline_code = QCheckBox(self)
		self.block_code = QCheckBox(self)
		self.convert_button = QPushButton("Save and Convert")
		self.save_button = QPushButton("Save and Close")
		
		layout.addRow(QLabel("Vault Path: "), self.vault_path)
		layout.addRow(QLabel("Please use forward slashes for your vault path."))
		layout.addRow(QLabel("Mode: "), self.mode)
		layout.addRow(QLabel("Mode: choose from word/line/heading/document"))
		layout.addRow(QLabel("Type: "), self.type)
		layout.addRow(QLabel("Type: choose from cloze/basic"))
		layout.addRow(QLabel("Bold to Cloze: "), self.bold)
		layout.addRow(QLabel("Italics to Cloze: "), self.italics)
		layout.addRow(QLabel("Image to Cloze: "), self.image)
		layout.addRow(QLabel("Quote to Cloze: "), self.quote)
		layout.addRow(QLabel("QA to Cloze"), self.QuestionOrAnswer)
		layout.addRow(QLabel("List to Cloze"), self.list)
		layout.addRow(QLabel("Inline Code to Cloze"), self.inline_code)
		layout.addRow(QLabel("Block Code to Cloze"), self.block_code)
		
		layout.addRow(self.save_button, self.convert_button)
		
		my_settings = settings.load_settings()
		
		try:
			self.vault_path.setText(my_settings["vault path"])
			self.mode.setText(my_settings["mode"])
			self.type.setText(my_settings["type"])
			self.bold.setChecked(get_bool(my_settings["bold"]))
			self.italics.setChecked(get_bool(my_settings["italics"]))
			self.image.setChecked(get_bool(my_settings["image"]))
			self.quote.setChecked(get_bool(my_settings["quote"]))
			self.QuestionOrAnswer.setChecked(get_bool(my_settings["QA"]))
			self.list.setChecked(get_bool(my_settings["list"]))
			self.inline_code.setChecked(get_bool(my_settings["inline code"]))
			self.block_code.setChecked(get_bool(my_settings["block code"]))
		except KeyError:
			self.vault_path.setText(settings.default_settings["vault path"])
			self.mode.setText(settings.default_settings["mode"])
			self.type.setText(settings.default_settings["type"])
			self.bold.setChecked(get_bool(settings.default_settings["bold"]))
			self.italics.setChecked(get_bool(settings.default_settings["italics"]))
			self.image.setChecked(get_bool(settings.default_settings["image"]))
			self.quote.setChecked(get_bool(settings.default_settings["quote"]))
			self.QuestionOrAnswer.setChecked(get_bool(settings.default_settings["QA"]))
			self.list.setChecked(get_bool(settings.default_settings["list"]))
			self.inline_code.setChecked(get_bool(settings.default_settings["inline code"]))
			self.block_code.setChecked(get_bool(settings.default_settings["block code"]))
		
		self.convert_button.setDefault(True)
		self.convert_button.clicked.connect(self.onOk)
		self.save_button.clicked.connect(self.onSave)
		self.show()
		
	def onOk(self):
		files_catalog = []
		newSettings = {}
		newSettings["vault path"] = self.vault_path.text()
		newSettings["mode"] = self.mode.text()
		newSettings["type"] = self.type.text()
		newSettings["bold"] = get_text(self.bold.isChecked())
		newSettings["italics"] = get_text(self.italics.isChecked())
		newSettings["image"] = get_text(self.image.isChecked())
		newSettings["quote"] = get_text(self.quote.isChecked())
		newSettings["QA"] = get_text(self.QuestionOrAnswer.isChecked())
		newSettings["list"] = get_text(self.list.isChecked())
		newSettings["inline code"] = get_text(self.inline_code.isChecked())
		newSettings["block code"] = get_text(self.block_code.isChecked())
		settings.save_settings(newSettings)
		read_files(self.vault_path.text(), "")
		self.close()
		
	def onSave(self):
		newSettings = {}
		newSettings["vault path"] = self.vault_path.text()
		newSettings["mode"] = self.mode.text()
		newSettings["type"] = self.type.text()
		newSettings["bold"] = get_text(self.bold.isChecked())
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
		