#!/usr/bin/env python3
import re
import html
import random
from . import settings
from .markdown2 import markdown2
from .markdown2 import markdown2Mathjax
from aqt.utils import showInfo


mark_file_extras = {
	"fenced-code-blocks": None,
	"metadata": None, 
	"strike": None, 
	"tables": None, 
	"tag-friendly": None, 
	"task_list": None, 
	"footnotes": None, 
	"break-on-newline": True
}

def read_file(full_path:str) -> list:
	output = ""
	source = ""
	uid = ""
	has_uid = False
	with open(full_path, mode="r", encoding="utf-8") as file:
		source = file.read()
		temporary_content = markdown2Mathjax.sanitizeInput(source)
		if source.startswith("---"):
			markdown_file = markdown2.markdown(temporary_content[0], extras = ["fenced-code-blocks", "metadata", "strike", "tables", "tag-friendly", "task_list", "footnotes", "break-on-newline"])
			metadata = markdown_file.metadata
		else:
			markdown_file = markdown2.markdown(temporary_content[0], extras = ["fenced-code-blocks", "strike", "tables", "tag-friendly", "task_list", "footnotes", "break-on-newline"])
			metadata = {}
		try:
			uid = metadata["uid"]
		except:
			random_number = random.randint(0, 100000000000000000000000000000)
			new_source = source + full_path + str(random_number)
			uid = str(abs(hash(new_source)))
			if len(metadata) == 0:
				source = "---\nuid: " + uid + "\n---\n\n" + source
			else:
				source_lines = source.split("\n")
				source_lines[0] = "---\nuid: " + uid
				source = "\n".join(source_lines)
		for i in range(len(temporary_content[1])):
			temporary_content[1][i] = html.escape(temporary_content[1][i])
			temporary_content[1][i] = temporary_content[1][i].replace("{{", "{ {")
			temporary_content[1][i] = temporary_content[1][i].replace("}}", "} }")
		
		cloze_settings = metadata_to_settings(metadata)
		
		markdown_file = get_converted_file(cloze_settings, markdown_file)
		if cloze_settings["type"] != "cloze" and cloze_settings["type"] != "Cloze":
			markdown_file[1] = False
		output = markdown2Mathjax.reconstructMath(markdown_file[0], temporary_content[1])
	output = math_conversion(output)
	
	# FIXME: output here
	with open(full_path, mode = "w", encoding = "utf-8") as file:
		file.write(source)
	return [uid, output, markdown_file[1], metadata]

def metadata_to_settings(metadata: dict) -> dict:
	new_settings = {}
	default_settings = settings.get_settings()
	for individual_key in default_settings.keys():
		try:
			new_settings[individual_key] = metadata[individual_key]
		except KeyError:
			new_settings[individual_key] = default_settings[individual_key]
	return new_settings

def get_converted_file(cloze_settings, file_content):
	file_content = cloze_generation(cloze_settings, file_content)
	file_content = cloze_number_generation(cloze_settings["mode"], file_content)
	return file_content

# Special thanks to Anis Qiao (https://github.com/qiaozhanrong) for the math_conversion section of the code! Now, obsidianki can support display math formula written in multiple lines. 

def math_conversion(file_content):
	isOpen = False
	s = ""
	p = 0
	while True:
		q = file_content.find("$$", p)
		if q == -1:
			s += file_content[p:]
			break
		s += file_content[p:q] + ("\]" if isOpen else "\[")
		isOpen = not isOpen
		p = q + 2
	file_content = s
	
	isOpen = False
	s = ""
	p = 0
	while True:
		q = file_content.find("$", p)
		if q == -1:
			s += file_content[p:]
			break
		s += file_content[p:q] + ("\)" if isOpen else "\(")
		isOpen = not isOpen
		p = q + 1
	file_content = s
	
	return file_content
				
def cloze_generation(cloze_settings:dict, file_content:str) -> str:
	if cloze_settings["type"] == "cloze" or cloze_settings["type"] == "Cloze":
		if cloze_settings["bold"] == "True" or cloze_settings["bold"] == "true":
			file_content = file_content.replace("<strong>", "<strong>{{c¡::")
			file_content = file_content.replace("</strong>", "}}</strong>")
		if cloze_settings["italics"] == "True" or cloze_settings["italics"] == "true":
			file_content = file_content.replace("<em>", "<em>{{c¡::")
			file_content = file_content.replace("</em>", "}}</em>")
		if cloze_settings["image"] == "True" or cloze_settings["image"] == "true":
			file_content = apply_cloze_to_image(file_content)
		if cloze_settings["inline code"] == "True" or cloze_settings["inline code"] == "true":
			file_content = re.sub(r"<code>(?!<span)", "<code>{{c¡::", file_content)
			file_content = re.sub(r"</code>(?!</pre>)", "}}</code>", file_content)
		if cloze_settings["QA"] == "True" or cloze_settings["QA"] == "true":
			tmp = file_content.split("\n")
			for i in range(0, len(tmp)):
				if tmp[i].startswith("<p>A: ") and tmp[i].endswith("</p>"):
					# TODO: add a security check to make sure that these two things are in the same line. 
					tmp[i] = tmp[i].replace("{{¡::", "")
					tmp[i] = tmp[i].replace("}}", "")
					tmp[i] = tmp[i].replace("<p>A: ", "<p>A: {{c¡::", 1)
					tmp[i] = tmp[i].replace("</p>", "}}</p>", 1)
				elif tmp[i].startswith("<p>答：") and tmp[i].endswith("</p>"):
					tmp[i] = tmp[i].replace("{{¡::", "")
					tmp[i] = tmp[i].replace("}}", "")
					tmp[i] = tmp[i].replace("<p>答：", "<p>答：{{c¡::", 1)
					tmp[i] = tmp[i].replace("</p>", "}}</p>")
					
				# ==================================================================
				# | You Can Disable this code if you Enabled strict line spacing.  |
				# ==================================================================
				elif tmp[i].startswith("A: ") and tmp[i].endswith("</p>"):
					tmp[i] = tmp[i].replace("{{¡::", "")
					tmp[i] = tmp[i].replace("}}", "")
					tmp[i] = tmp[i].replace("A: ", "A: {{c¡::", 1)
					tmp[i] = tmp[i].replace("</p>", "}}</p>", 1)
				elif tmp[i].startswith("答：") and tmp[i].endswith("</p>"):
					tmp[i] = tmp[i].replace("{{¡::", "")
					tmp[i] = tmp[i].replace("}}", "")
					tmp[i] = tmp[i].replace("答：", "答: {{c¡::", 1)
					tmp[i] = tmp[i].replace("</p>", "}}</p>", 1)
			file_content = "\n".join(tmp)
		if cloze_settings["list"] == "True" or cloze_settings["list"] == "true":
			tmp = file_content.split("\n")
			for i in range(0, len(tmp)):
				if tmp[i].find("{{c¡::") != -1:
					pass
				else:
					tmp[i] = tmp[i].replace("<li>", "<li>{{c¡::")
					tmp[i] = tmp[i].replace("</li>", "}}</li>")
			file_content = "\n".join(tmp)
		if cloze_settings["quote"] == "True" or cloze_settings["quote"] == "true":
			# ===================================================
			# | TODO: use REGEX to replace the proper ones here |
			# ===================================================
			file_content = file_content.replace("<blockquote>", "<blockquote>{{c¡::")
			file_content = file_content.replace("</blockquote>", "}}</blockquote>")
		if cloze_settings["block code"] == "True" or cloze_settings["block code"] == "true":
			# ===================================================
			# | TODO: use REGEX to replace the proper ones here |
			# ===================================================
			file_content = file_content.replace("<div class=\"codehilite\"><pre><span></span><code>", "<div class=\"codehilite\"><pre><span></span><code>{{c¡::")
			file_content = file_content.replace("</code></pre></div>", "}}</code></pre></div>")
		file_content = highlight_conversion(file_content, cloze_settings["highlight"])
	elif cloze_settings["type"] == "basic" or cloze_settings["type"] == "Basic":
		file_content = highlight_conversion(file_content, "False")
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
		cloze_num = 0
		for i in range (0, len(tmp)):
			if tmp[i].find("¡") != -1:
				cloze_num = cloze_num + 1
				tmp[i] = tmp[i].replace("¡", str(cloze_num))
		file_content = "\n".join(tmp)
	elif mode == "heading":
		# ==========================================================
		# | TODO: Check the code here to see if it actually works  |
		# ==========================================================
		tmp = file_content.split("\n")
		cloze_num = 0
		increase_num = 0
		new_cloze = 0
		for i in range(0, len(tmp)):
			if re.search(r"<h\d>", tmp[i]) != None:
				cloze_num = get_cloze_number(tmp) + 1
			elif tmp[i].startswith("<p>A: ") or tmp[i].startswith("<p>答：") or tmp[i].startswith("A: ") or tmp[i].startswith("答："):
				increase_num = get_cloze_number(tmp) + 1
				tmp[i] = tmp[i].replace("¡", str(increase_num))
				cloze_num = increase_num + 1
			elif tmp[i].startswith("<li>"):
				if new_cloze == 0:
					new_cloze = 1
					increase_num = get_cloze_number(tmp) + 1
					tmp[i] = tmp[i].replace("¡", str(increase_num))
				elif new_cloze == 1 and i < (len(tmp) - 2) and tmp[i + 1].startswith("<li>"):
					tmp[i] = tmp[i].replace("¡", str(increase_num))
				elif new_cloze == 1 and i < (len(tmp) - 2) and not tmp[i + 1].startswith("<li>"):
					tmp[i] = tmp[i].replace("¡", str(increase_num))
					cloze_num = increase_num + 1
					new_cloze = 0
				
			tmp[i] = tmp[i].replace("¡", str(cloze_num))
		file_content = "\n".join(tmp)
	elif mode == "document":
		if file_content.find("¡") != -1:
			file_content = file_content.replace("¡", "1")
	return [file_content, has_cloze]


def get_cloze_number(tmp) -> int:
	file_content = "".join(tmp)
	cloze_number = 0
	for i in range(1, 7):
		if file_content.find("{{c%d::"%(i)) != -1:
			cloze_number = i
	return cloze_number

# =========================================
# | TODO: Check to see if this code works |
# =========================================


def highlight_conversion(file_content: str, to_cloze: bool) -> str:
	lines = file_content.split("\n")
	isInCode = False
	for i in range(0, len(lines)):
		if lines[i].startswith("<div class=\"codehilite\"><pre><span></span><code>"):
			isInCode = True
		elif lines[i].startswith("</code></pre></div>"):
			isInCode = False
		if not isInCode:
			lines[i] = apply_highlight(lines[i], to_cloze)
	file_content = "\n".join(lines)
	return file_content


def apply_highlight(line: str, to_cloze: str) -> str:
	line = "ªªª" + line + "ªªª"
	line_segments = line.split("==")
	number_of_highlights = len(line_segments) // 2
	if number_of_highlights > 0:
		if to_cloze == "True" or to_cloze == "true":
			for i in range(1, number_of_highlights + 1):
				highlight_index = 2 * i - 1
				line_segments[highlight_index] = "<label id = \"highlight\">{{c¡::" + line_segments[highlight_index] + "}}</label>"
		else:
			for i in range(1, number_of_highlights + 1):
				highlight_index = 2 * i - 1
				line_segments[highlight_index] = "<label id = \"highlight\">" + line_segments[highlight_index] + "</label>"

	line = "".join(line_segments)
	line = line.replace("ªªª", "")
	return line

def apply_cloze_to_image(file_content: str) -> str:
	lines = file_content.split("\n")
	for i in range(0, len(lines)):
		image_url = re.search(r"<img src=\".+? \/>", lines[i])
		if image_url != None:
			lines[i] = re.sub(r"<img src=\".+? \/>", "{{c¡::" + image_url.group(0) + "}}", lines[i])
	file_content = "\n".join(lines)
	return file_content