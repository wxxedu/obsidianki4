#!/usr/bin/env python3
import re
import html
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
		markdown_file = markdown2.markdown(temporary_content[0], extras = ["fenced-code-blocks", "metadata", "strike", "tables", "tag-friendly", "task_list", "footnotes", "break-on-newline"])
		metadata = markdown_file.metadata
		try:
			uid = metadata["uid"]
		except:
			uid = str(abs(hash(source)))
			if len(metadata) == 0:
				markdown_file = markdown2.markdown(temporary_content[0], extras = ["fenced-code-blocks", "strike", "tables", "tag-friendly", "task_list", "break-on-newline", "footnotes"])
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
		if cloze_settings["type"] != "cloze":
			markdown_file[1] = False
		output = markdown2Mathjax.reconstructMath(markdown_file[0], temporary_content[1])
	output = math_conversion(output)
	# FIXME: output here
	with open(full_path, mode = "w", encoding = "utf-8") as file:
		file.write(source)
	return [uid, output, markdown_file[1], metadata]

def metadata_to_settings(metadata: dict) -> dict:
	new_settings = {}
	some_settings = settings.get_settings()
	try:
		if metadata["type"] == "cloze":
			for key in some_settings.keys():
				try:
					new_settings[key] = metadata[key]
				except:
					if key != "vault path":
						new_settings[key] = some_settings[key]
		elif metadata["type"] == "basic":
			for key in some_settings.keys():
				if key != "vault path":
					new_settings[key] = "False"
				new_settings["type"] = "basic"
				new_settings["mode"] = "None"
	except KeyError:
		metadata["type"] = some_settings["type"]
		new_settings = metadata_to_settings(metadata)
	return new_settings

def get_converted_file(cloze_settings, file_content):
	file_content = cloze_generation(cloze_settings, file_content)
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
			if tmp[i].startswith("<p>A: ") and tmp[i].endswith("</p>\n"):
				tmp[i] = tmp[i].replace("{{c¡::", "")
				# TODO: add a security check to make sure that these two things are in the same line. 
				
				tmp[i] = tmp[i].replace("<p>A: ", "<p>A: {{c¡::")
				tmp[i] = tmp[i].replace("</p>", "}}</p>")
			elif tmp[i].startswith("<p>答：") and tmp[i].endswith("</p>\n"):
				tmp[i] = tmp[i].replace("{{c¡::", "")
				tmp[i] = tmp[i].replace("<p>答：", "<p>答：{{c¡::")
				tmp[i] = tmp[i].replace("</p>", "}}</p>")
			# ==================================================================
			# | You Can Disable this code if you Enabled strict line spacing.  |
			# ==================================================================
			elif tmp[i].startswith("A: ") and tmp[i].endswith("</p>\n"):
				tmp[i] = tmp[i].replace("{{c¡::", "")
				tmp[i] = tmp[i].replace("A: ", "A: {{c¡::", 1)
				tmp[i] = tmp[i].replace("</p>", "}}</p>")
			elif tmp[i].startswith("答：") and tmp[i].endswith("</p>\n"):
				tmp[i] = tmp[i].replace("{{c¡::", "")
				tmp[i] = tmp[i].replace("答：", "答: {{c¡::")
				tmp[i] = tmp[i].replace("</p>", "}}</p>")
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
		# ==========================================================
		# | TODO: Check the code here to see if it actually works  |
		# ==========================================================
		tmp = file_content.split("\n")
		cloze_num = 0
		increase_num = 0
		for i in range(0, len(tmp)):
			if re.search(r"<h\d>", tmp[i]) != None:
				cloze_num = get_cloze_number(tmp) + 1
			elif tmp[i].startswith("<p>A: ") or tmp[i].startswith("<p>答：") or tmp[i].startswith("<li>") or tmp[i].startswith("A: ") or tmp[i].startswith("答："):
				increase_num = get_cloze_number(tmp) + 1
				tmp[i] = tmp[i].replace("¡", str(increase_num))
				cloze_num = increase_num + 1
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