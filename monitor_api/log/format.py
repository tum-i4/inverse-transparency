#!/usr/bin/env python3
# encoding=utf-8
""" Log formatting """

import json
from logging import Formatter


ISO_DATE_FORMAT:str = "%Y-%m-%dT%H:%M:%S%z"

READABLE_LOG_FORMAT:str = "%(asctime)s (%(name)s | %(levelname)s) %(message)s"
JSON_LOG_FORMAT:str = json.dumps({
	"time" : "%(asctime)s",
	"name" : "%(name)s",
	"level" : "%(levelname)s",
	"content" : "%(message)s"
})
