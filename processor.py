#!/usr/bin/env python3
import re

default_cloze_mode = "heading"
default_cloze_settings = {
	"bold": True,
	"italics": False,
	"image": False,
	"quote": False,
	"QA": True,
	"orderd list": True,
	"non-ordered list": True,
	"inline code": True,
	"block code": False,
	"inline math": True,
	"block math": False
}

def cloze_modes(mode=str, file_content=str) -> [str, bool]:
	has_cloze = False
	if file_content.find("¡") != -1:
		has_cloze = True
	
	if mode == "word":
		cloze_num = 1
		while file_content.find("¡") != -1:
			file_content = file_content.replace("¡", str(cloze_num), 1)
			cloze_num = cloze_num + 1
	elif mode == "line":
		tmp = file_content.split("\n")
		for i in range (0, len(tmp)):
			cloze_num = 1
			while tmp[i].find("¡") != 0:
				tmp[i] = tmp[i].replace("¡", str(cloze_num), 1)
				cloze_num = cloze_num + 1
		file_content = "\n".join(tmp)
	elif mode == "heading":
		tmp = file_content.split("\n")
		cloze_num = 1
		for i in range(0, len(tmp)):
			tmp[i] = tmp[i].replace("¡", str(cloze_num))
			if re.search(r"<h\d>", tmp[i]) != None:
				cloze_num = cloze_num + 1
		file_content = "\n".join(tmp)
	elif mode == "doc":
		if file_content.find("¡") != 0:
			file_content = file_content.replace("¡", "1")
	else:
		# ==================================================
		# | TODO: Add the setting for default_cloze_mode   |
		# ==================================================
		file_content = cloze_modes(default_cloze_mode, file_content)
	
	return [file_content, has_cloze]
		
def word_mode(cloze_settings=dict, file_content=str) -> str:
	new_settings = default_cloze_settings
	for key in cloze_settings.keys:
		new_settings[key] = cloze_settings[key]
	if new_settings["bold"]:
		file_content = file_content.replace("<strong>", "<strong>{{c¡::")
		file_content = file_content.replace("</strong>", "}}</strong>")
	if new_settings["italics"]:
		file_content = file_content.replace("<em>", "<em>{{c¡::")
		file_content = file_content.replace("</em>", "}}</em>")
	if new_settings["image"]:
		file_content = file_content.replace("<img", "{{c¡::<img")
		file_content = file_content.replace("</img>", "</img>}}")
	if new_settings["quote"]:
		pass
	if new_settings["QA"]:
		tmp = file_content.split("\n")
		for i in range(0, len(tmp)):
			if tmp[i].startswith("<p>A: "):
				
				# TODO: add a security check to make sure that these two things are in the same line. 
				
				tmp[i] = tmp[i].replace("<p>A: ", "<p>A: {{c¡::")
				tmp[i] = tmp[i].replace("</p>", "}}</p>")
			elif tmp[i].startswith("<p>问："):
				tmp[i] = tmp[i].replace("<p>问：", "<p>问：{{c¡::")
				tmp[i] = tmp[i].replace("</p>", "}}</p>")
		file_content = "\n".join(tmp)
	if new_settings["ordered list"]:
		pass
	if new_settings["non-ordered list"]:
		pass
	if new_settings["inline code"]:
		file_content = re.sub(r"<code>(?!<span)", "<code>{{c¡::", file_content)
		file_content = re.sub(r"</code>(?!</pre>)", "}}</code>", file_content)
	if new_settings["block code"]:
		pass
	if new_settings["inline math"]:
		pass
	if new_settings["block math"]:
		pass
	
	pass
	
def math_conversion(file_content):
	tmp = file_content.split("\n")
	for i in range(0, len(tmp)):
		isOpen = True
		while tmp[i].find("$$") != -1:
			if isOpen:
				tmp[i] = tmp[i].replace("$$", "\[")
				isOpen = False
			else:
				tmp[i] = tmp[i].replace("$$", "\]")
				isOpen = True
		isOpen = True
		while tmp[i].find("$") != -1:
			if isOpen:
				tmp[i] = tmp[i].replace("$", "\(")
			else:
				tmp[i] = tmp[i].replace("$", "\)")
	