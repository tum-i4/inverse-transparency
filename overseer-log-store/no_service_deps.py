from typing import List, Set

from overseer.main import overseer
from overseer.models import RevoloriId
from overseer.services import RevoloriService


class MockRevoloriService(RevoloriService):
    @staticmethod
    def map_ids(tool: str, tool_specific_ids: List[str]) -> Set[RevoloriId]:
        return {RevoloriId(tool_specific_id) for tool_specific_id in tool_specific_ids}


overseer.dependency_overrides[RevoloriService] = MockRevoloriService
