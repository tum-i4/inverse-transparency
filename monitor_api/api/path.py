#!/usr/bin/env python3
# encoding=utf-8

""" API path handling """

from typing import List, Tuple

def join(path:str, *paths:str) -> str:
	"""
	Join one or more path components intelligently.
	Contrary to `os.path`, there are no "absolute paths".
	Returned path (component) will never start with, but always end with "/".
	"""

	if not paths:
		return path

	s = "/"
	strip = lambda p: p.strip(s)

	all_components:List[str] = [strip(p) for p in [path, *paths]]
	return s.join(all_components) + s
