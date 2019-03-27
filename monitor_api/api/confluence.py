#!/usr/bin/env python3
# encoding=utf-8

""" moduleinfo """


from typing import List, Tuple
from flask_restful import Resource


BASE_URL = "http://vmpretschner28.informatik.tu-muenchen.de/"
API_BASE_PATH = "api/"

# Paths – ? = not explored, o = explored, t = to implement, x = done
# (?) audit/
# (?) content/
# (?) group/
# (o) longtask
# (o) longtask/{id}
# (o) search
# (?) space/
# (?) user/

RESOURCES:List[Tuple[Resource, str]] = []
