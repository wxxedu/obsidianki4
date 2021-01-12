#!/usr/bin/env python3
import re
import sys
import os
sys.path.append(os.path.abspath('./markdown2'))
import markdown2
import markdown2Mathjax
import html

default_cloze_settings = {
	"mode": "heading",
	"bold": "True",
	"italics": "True",
	"image": "True",
	"quote": "True",
	"QA": "True",
	"list": "True",
	"inline code": "True",
	"block code": "True"
}

def read_file(full_path:str) -> list:
	output = ""
	with open(full_path, mode="r", encoding="utf-8") as file:
		source = file.read()
		temporary_content = markdown2Mathjax.sanitizeInput(source)
		markdown_file = markdown2.markdown(temporary_content[0], extras = ["fenced-code-blocks", "metadata", "strike", "tables", "tag-friendly", "task_list", "break-on-newline", "footnotes"])
		metadata = markdown_file.metadata
		if len(metadata) == 0:
			markdown_file = markdown2.markdown(temporary_content[0], extras = ["fenced-code-blocks", "strike", "tables", "tag-friendly", "task_list", "break-on-newline", "footnotes"])
		for i in range(len(temporary_content[1])):
			temporary_content[1][i] = html.escape(temporary_content[1][i])
			temporary_content[1][i] = temporary_content[1][i].replace("{{", "{ {")
			temporary_content[1][i] = temporary_content[1][i].replace("}}", "} }")
		# ==================================
		# | FIXME: DELETE THIS TEST CODE   |
		# ==================================
		cloze_settings = metadata_to_settings(metadata)
		markdown_file = get_converted_file(cloze_settings, markdown_file)
		output = markdown2Mathjax.reconstructMath(markdown_file[0], temporary_content[1])
	output = math_conversion(output)
	# FIXME: output here
	print(output)
	return [output, markdown_file[1]]

def metadata_to_settings(metadata: dict) -> dict:
	new_settings = {}
	for key in default_cloze_settings.keys():
		try:
			new_settings[key] = metadata[key]
		except:
			new_settings[key] = default_cloze_settings[key]
	return new_settings

def get_converted_file(cloze_settings, file_content):
	file_content = cloze_generation(cloze_settings, file_content)
	# ==================================
	# | FIXME: DELETE THIS TEST CODE   |
	# ==================================
	file_content = cloze_number_generation(cloze_settings["mode"], file_content)
	return file_content

def math_conversion(file_content):
	tmp = file_content.split("\n")
	isOpen = True
	for i in range(0, len(tmp)):
		while tmp[i].find("$$") != -1:
			if isOpen:
				tmp[i] = tmp[i].replace("$$", "\[", 1)
				isOpen = False
			else:
				tmp[i] = tmp[i].replace("$$", "\]", 1)
				isOpen = True
		isOpen = True
		while tmp[i].find("$") != -1:
			if isOpen:
				tmp[i] = tmp[i].replace("$", "\(", 1)
				isOpen = False
			else:
				tmp[i] = tmp[i].replace("$", "\)", 1)
				isOpen = True
	file_content = "\n".join(tmp)
	return file_content
				
def cloze_generation(cloze_settings:dict, file_content:str) -> str:
	if cloze_settings["bold"] == "True":
		file_content = file_content.replace("<strong>", "<strong>{{c¡::")
		file_content = file_content.replace("</strong>", "}}</strong>")
	if cloze_settings["italics"] == "True":
		file_content = file_content.replace("<em>", "<em>{{c¡::")
		file_content = file_content.replace("</em>", "}}</em>")
	if cloze_settings["image"] == "True":
		file_content = file_content.replace("<img", "{{c¡::<img")
		file_content = file_content.replace("</img>", "</img>}}")
	if cloze_settings["quote"] == "True":
		file_content = file_content.replace("<blockquote>", "<blockquote>{{c¡::")
		file_content = file_content.replace("</blockquote>", "}}</blockquote>")
	if cloze_settings["QA"] == "True":
		tmp = file_content.split("\n")
		for i in range(0, len(tmp)):
			if tmp[i].startswith("<p>A: "):
				
				# TODO: add a security check to make sure that these two things are in the same line. 
				
				tmp[i] = tmp[i].replace("<p>A: ", "<p>A: {{c¡::")
				tmp[i] = tmp[i].replace("</p>", "}}</p>")
			elif tmp[i].startswith("<p>答："):
				tmp[i] = tmp[i].replace("<p>答：", "<p>答：{{c¡::")
				tmp[i] = tmp[i].replace("</p>", "}}</p>")
		file_content = "\n".join(tmp)
	if cloze_settings["list"] == "True":
		file_content = file_content.replace("<li>", "<li>{{c¡::")
		file_content = file_content.replace("</li>", "}}</li>")
	if cloze_settings["inline code"] == "True":
		file_content = re.sub(r"<code>(?!<span)", "<code>{{c¡::", file_content)
		file_content = re.sub(r"</code>(?!</pre>)", "}}</code>", file_content)
	if cloze_settings["block code"] == "True":
		file_content = file_content.replace("<div class=\"codehilite\"><pre><span></span><code>", "<div class=\"codehilite\"><pre><span></span><code>{{c¡::")
		file_content = file_content.replace("</code></pre></div>", "}}</code></pre></div>")
	
	return file_content

def cloze_number_generation(mode:str, file_content:str) -> [str, bool]:
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
			cloze_num = 0
			while tmp[i].find("¡") != -1:
				cloze_num = cloze_num + 1
				tmp[i] = tmp[i].replace("¡", str(cloze_num), 1)
		file_content = "\n".join(tmp)
	elif mode == "heading":
		tmp = file_content.split("\n")
		cloze_num = 0
		for i in range(0, len(tmp)):
			if re.search(r"<h\d>", tmp[i]) != None or tmp[i].startswith("<p>A: ") or tmp[i].startswith("<p>答：") or tmp[i].startswith("<li>"):
				cloze_num = cloze_num + 1
			tmp[i] = tmp[i].replace("¡", str(cloze_num))
			
		file_content = "\n".join(tmp)
	elif mode == "doc":
		if file_content.find("¡") != -1:
			file_content = file_content.replace("¡", "1")
#	else:
#		# ==================================================
#		# | TODO: Add the setting for default_cloze_mode   |
#		# ==================================================
#		file_content = cloze_modes(default_cloze_mode, file_content)
	
	return [file_content, has_cloze]


read_file("./markdown2/test.md")