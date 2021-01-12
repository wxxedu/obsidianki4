#!/usr/bin/env python3

import markdown2
import markdown2Mathjax
import re
import html

path = "./test.md"
file_content = ""
with open(path, mode = "r", encoding = "utf-8") as f:
	file_content = f.read()
	
markdown2file = markdown2.markdown(file_content, extras = ["fenced-code-blocks", "metadata"])


markdown2file = re.sub("<code>(?!<span)", "<code>{{c¡::", markdown2file)
markdown2file = re.sub("</code>(?!</pre>)", "}}<code>", markdown2file)

temporary_content = markdown2Mathjax.sanitizeInput(file_content)
print(temporary_content[1])
markdown_file = markdown2.markdown(temporary_content[0], extras = ["fenced-code-blocks", "metadata", "strike", "tables", "tag-friendly", "task_list", "break-on-newline", "footnotes"])
metadata = markdown_file.metadata
if len(metadata) == 0:
	markdown_file = markdown2.markdown(temporary_content[0], extras = ["fenced-code-blocks", "strike", "tables", "tag-friendly", "task_list", "break-on-newline", "footnotes"])
for i in range(len(temporary_content[1])):
	temporary_content[1][i] = html.escape(temporary_content[1][i])
	print(temporary_content[1][i])
output = markdown2Mathjax.reconstructMath(markdown_file, temporary_content[1])

print(output)
