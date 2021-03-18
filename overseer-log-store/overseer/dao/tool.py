#!/usr/bin/env python3
""" Tool DAO module """
from typing import List, Optional

from overseer.db.connection import Session
from overseer.db.models import Tool


class ToolDao:
    """
    Class for manipulating tool objects in the database.
    """

    @staticmethod
    def add(session: Session, tool: Tool):
        """ Insert a tool into the database """
        session.add(tool)

    @staticmethod
    def load_all(session: Session) -> List[Tool]:
        """ Load all tools form the database """
        return session.query(Tool).all()

    @staticmethod
    def load_single(session: Session, tool_name: str) -> Optional[Tool]:
        query = session.query(Tool).filter(Tool.name == tool_name)
        return query.first()

    @staticmethod
    def delete(session: Session, tool_name: str) -> bool:
        """ Delete a tool by its name """
        query = session.query(Tool).filter(Tool.name == tool_name)
        return 1 == query.delete()
