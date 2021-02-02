#!/usr/bin/env python3

from aqt.utils import showInfo

def process_obsidian_file(file_content:str, files_catalog:list):
	lines = file_content.split("\n")
	
	isInCode = False
	
	for i in range(0, len(lines)):
		if lines[i].startswith("<div class=\"codehilite\"><pre><span></span><code>"):
			isInCode = True
		elif lines[i].startswith("</code></pre></div>"):
			isInCode = False
		if not isInCode:
			lines[i] = process_obsidian_line(lines[i], files_catalog)
	
	file_content = "\n".join(lines)
	return file_content
			
def process_obsidian_line(line, files_catalog:list):
	if line.find("[[") != -1 and line.find("]]") != -1:
		line = line.replace("[[", "ªªª[[")
		line = line.replace("]]", "]]ªªª")
		line_segments = line.split("[[")
		line = "º".join(line_segments)
		line_segments = line.split("]]")
		line = "º".join(line_segments)
		line_segments = line.split("º")
		number_of_segments = len(line_segments)
		number_of_replacements = number_of_segments // 2
		if number_of_replacements > 0:
			for i in range(1, number_of_replacements + 1):
				replacement_index = 2 * i - 1
				line_segments[replacement_index] = process_obsidian_link_content(line_segments[replacement_index], files_catalog)
		line = "".join(line_segments)
		line = line.replace("ªªª", "")
	return line
	
def process_obsidian_link_content(content, files_catalog:list):
	if content.find("|") != -1:
		content_segments = content.split("|")
		obsidian_url = search_for_note(content_segments[0], files_catalog)
		content = "<a href = \"" + obsidian_url + "\">" + content_segments[1] + "</a>"
	else:
		obsidian_url = search_for_note(content, files_catalog)
		content = "<a href = \"" + obsidian_url + "\">" + content + "</a>"
	return content

def search_for_note(name:str, files_catalog:list):
	for file in files_catalog:
		if file.get_file_name() == name:
			return file.get_obsidian_url()
	return ""
