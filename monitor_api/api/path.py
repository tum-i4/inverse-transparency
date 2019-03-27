#!/usr/bin/env python3
# encoding=utf-8

""" API path handling """

from typing import List, Tuple

def join(first:str, *others:str) -> str:
	"""
	Join one or more path components intelligently.
	Contrary to `os.path`, there are no "absolute paths".
	Rules:
	- Starting / ending slashes (from the first and last component) will be kept
	- Empty components will be discarded
	- A slash can be enforced with a starting / ending component "/"
	"""

	if not others:
		return first

	s = "/"
	strip = lambda p: p.strip(s)

	all_components:List[str] = [p for p in [first, *others] if p != ""]

	if not all_components:
		return ""

	start_s:bool = all_components[0].startswith(s)
	end_s:bool = all_components[-1].endswith(s)

	stripped_components:List[str] = [strip(p) for p in all_components if p != s]
	result = s.join(stripped_components)

	if start_s:
		result = s + result
	if end_s:
		result = result + s

	return result
