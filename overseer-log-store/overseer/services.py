#!/usr/bin/env python3

from typing import Dict, List, Set

import requests

from overseer.models import RevoloriId
from overseer.settings import settings


class ServiceError(Exception):
    """
    Error which is raised whenever a service returns a bad status code.
    """

    def __init__(self, endpoint, status_code):
        super(ServiceError, self).__init__(f"{endpoint} returned status {status_code}.")


class IdMappingError(Exception):
    """
    Error which is raised whenever some IDs couldn't be mapped.
    """

    def __init__(self):
        super(IdMappingError, self).__init__("One or more ids couldn't be mapped.")


class RevoloriService:
    @staticmethod
    def get_id_mapping(
        tool: str, tool_specific_ids: List[str]
    ) -> Dict[RevoloriId, Set[str]]:
        """
        Return mapping of unique `RevoloriId`s to their corresponding tool specific ids.
        """
        payload = {tool: tool_specific_ids}
        response = requests.get(settings.REVOLORI_ID_ENDPOINT, json=payload)

        if 400 <= response.status_code < 500:
            raise IdMappingError()
        elif 500 <= response.status_code:
            raise ServiceError(settings.REVOLORI_ID_ENDPOINT, response.status_code)

        # The response is a mapping `tool : { tool_specific_id : revolori_id }`
        resolved_ids: Dict[str, str] = response.json()[tool]

        owner_rid_reverse_map: Dict[RevoloriId, Set[str]] = dict()
        for tool_specific_id, revolori_id_str in resolved_ids.items():
            revolori_id = RevoloriId(revolori_id_str)
            if revolori_id not in owner_rid_reverse_map:
                owner_rid_reverse_map[revolori_id] = set()
            owner_rid_reverse_map[revolori_id].add(tool_specific_id)

        return owner_rid_reverse_map

    @staticmethod
    def map_ids(tool: str, tool_specific_ids: List[str]) -> Set[RevoloriId]:
        """
        Map tool specific IDs to Revolori IDs.
        """
        return set(RevoloriService.get_id_mapping(tool, tool_specific_ids).keys())

    @classmethod
    def map_id(cls, tool: str, tool_specific_id: str) -> RevoloriId:
        """
        Map a tool specific ID to a Revolori ID.
        """
        return cls.map_ids(tool, [tool_specific_id]).pop()
