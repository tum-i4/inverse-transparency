#!/usr/bin/env python3
""" Data access DAO module """

import datetime as dt
import itertools
import random
from typing import Dict, List, Optional, Tuple

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.orm import Query, selectinload

from overseer.auth import get_current_user
from overseer.db.connection import Session
from overseer.db.models import DataAccess, DataOwner
from overseer.models import DataAccessKind, RevoloriId


class DataAccessDao:
    """
    Class for manipulating data access objects in the database.
    Instance methods are authenticated using JWT tokens.
    Class and static methods are not authenticated.

    Attributes:
        logged_in_user: The Revolori ID of the currently logged in user.
    """

    def __init__(self, logged_in_user=Depends(get_current_user)):
        self.logged_in_user = logged_in_user

    @staticmethod
    def add(session: Session, data_access: DataAccess):
        """Insert a data access into the database"""
        session.add(data_access)

    @staticmethod
    def _filter_query_with_date_range(
        query: Query,
        date_start: Optional[dt.date] = None,
        date_end: Optional[dt.date] = None,
    ) -> Query:
        if date_start is not None:
            query = query.filter(func.DATE(DataAccess.timestamp) >= date_start)
        if date_end is not None:
            query = query.filter(func.DATE(DataAccess.timestamp) <= date_end)

        return query

    def load_all(
        self,
        session: Session,
        date_start: Optional[dt.date] = None,
        date_end: Optional[dt.date] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[DataAccess]:
        """Load all entries of the given data owner."""

        query = session.query(DataAccess).filter(
            DataAccess.data_owners.any(owner_rid=self.logged_in_user)
        )

        query = self._filter_query_with_date_range(query, date_start, date_end)

        query = query.order_by(DataAccess.timestamp.desc())

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        data_accesses: List[DataAccess] = query.options(
            # eager load data types
            selectinload(DataAccess.data_types),
        ).all()

        return data_accesses

    def count(
        self,
        session: Session,
        date_start: Optional[dt.date] = None,
        date_end: Optional[dt.date] = None,
    ) -> Dict[str, Dict[str, int]]:
        """
        Count the total number of entries available in the database per key (user_rid,
        tool, and access_kind) and grouped by unique values.
        """

        result = {}

        for field_name in ["user_rid", "tool", "access_kind"]:
            field = getattr(DataAccess, field_name)
            query: Query = session.query(
                field,
                func.count(),
            ).filter(DataAccess.data_owners.any(owner_rid=self.logged_in_user))

            query = self._filter_query_with_date_range(query, date_start, date_end)
            query = query.group_by(field)
            result[field_name] = dict(query.all())

        return result

    @classmethod
    def generate_log(
        cls,
        session: Session,
        owner_rid: RevoloriId,
        date_range: Tuple[dt.date, dt.date],
        number_of_entries: int,
        tools: List[str],
    ) -> None:
        """Generate a log for the given data owner."""

        data_accesses = cls._generate_data_accesses(owner_rid, date_range, tools)
        for data_access in itertools.islice(data_accesses, number_of_entries):
            cls.add(session, data_access)

    @staticmethod
    def _generate_data_accesses(
        owner_rid: RevoloriId,
        date_range: Tuple[dt.date, dt.date],
        tools: List[str],
    ):
        """Infinite generator for creating data accesses for the given data owner."""

        if date_range[0] > date_range[1]:
            date_range = (date_range[1], date_range[0])

        # fmt: off
        users = ["frauke@example.com", "admin@example.com", "markiplier-1928@example.com", "d_schmidberger@example.com", "westermann@example.com", "valentin@example.com", "maren@example.com", "marlene@example.com", "erick@example.com"]
        kinds = [DataAccessKind.AGGREGATE, DataAccessKind.QUERY, DataAccessKind.DIRECT]
        # fmt: on
        max_days_extra = (date_range[1] - date_range[0]).days

        while True:
            user: str = random.choice(users)
            tool = random.choice(tools)
            access_kind = random.choice(kinds)
            timestamp = dt.datetime.combine(
                date=date_range[0], time=dt.time(0, 0)
            ) + dt.timedelta(
                days=random.randint(0, max_days_extra),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59),
            )

            data_access = DataAccess(
                user_rid=user,
                tool=tool,
                access_kind=access_kind,
                timestamp=timestamp,
                justification=None,
            )
            data_access.data_owners = [DataOwner(owner_rid=owner_rid)]

            yield data_access
