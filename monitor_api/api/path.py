# encoding=utf-8
""" API path handling """

from typing import List, Tuple

def join(first:str, *others:str) -> str:
	"""
	Join one or more path components intelligently.
	Contrary to `os.path`, there are no "absolute paths".
	Rules:
	- The returned path will always start with "/", except if the first component starts with "http"
	- The returned path will never end with "/", except when enforced (see below)
	- Empty components will be discarded
	- A trailing slash can be enforced with a final component "/"
	- Caution: "http://" will be stripped of its slashes! Instead pass "http://www.de" or similar.
	"""

	s = "/"
	strip = lambda p: p.strip(s)

	all_components:List[str] = [
		p for p in [first, *others]
		if p != ""
	]

	if not all_components:
		return ""

	start_s:bool = not all_components[0].startswith("http")
	end_s:bool = all_components[-1] == s

	# Filter empty strings again; this ensures that "/" and "//" do not result in double slashes
	stripped_components:List[str] = [
		p for p in [
			strip(p) for p in all_components
		] if p != ""
	]
	result = s.join(stripped_components)

	if start_s:
		result = s + result
	if end_s:
		result = result + s

	return result
