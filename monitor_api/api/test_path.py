# encoding=utf-8

""" Test module for api.path """

from typing import List, Tuple

import api.path


def test_join():
	test_cases:List[Tuple[List[str], str]] = [
		# Always starts with "/", never ends with "/" for normal inputs
		([""],                  ""),
		(["abc"],               "/abc"),
		(["a/", "b/", "c/"],    "/a/b/c"),
		(["/a", "/b", "/c"],    "/a/b/c"),
		(["/abc/"],             "/abc"),
		(["/a", "b/"],          "/a/b"),
		(["/a/", "/b/", "/c/"], "/a/b/c"),
		(["a", "b", "c", "d"],  "/a/b/c/d"),
		# Last component "/" -> trailing slash
		(["a", "b", "c", "/"],  "/a/b/c/"),
		(["a", "", "/"],        "/a/"),
		(["/", "a", "b", "c"],  "/a/b/c"),
		(["/", "", "a"],        "/a"),
		(["/", "", "a", "/"],   "/a/"),
		# Last component "" -> no trailing slash
		(["a", ""],             "/a"),
		# First component starts with "http" -> no starting slash
		(["http://r.a/w/", "x"],   "http://r.a/w/x"),
		(["http://xyz", "x", "/"], "http://xyz/x/"),
		# Ensure robustness
		(["", "a", "", "/b/", "/c", "/", ""], "/a/b/c/"),
		(["", "", ""],          ""),
		(["", "", "a"],         "/a"),
		(["", "", "/a"],        "/a"),
		(["", "", "/a/"],       "/a"),
		(["", "", "/a/", ""],   "/a"),
	]

	for inputs, expected_result in test_cases:
		actual_result = api.path.join(*inputs)
		assert expected_result == actual_result
