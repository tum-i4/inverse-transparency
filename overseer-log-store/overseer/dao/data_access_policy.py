#!/usr/bin/env python3
""" Data access policy DAO module """

from typing import List, Optional

from fastapi import Depends
from sqlalchemy import or_

from overseer.auth import get_current_user
from overseer.db.connection import Session
from overseer.db.models import DataAccess, DataAccessPolicy


class DataAccessPolicyDao:
    """
    Class for manipulating data access policy objects in the database.
    Instance methods are authenticated using JWT tokens.
    Class and static methods are not authenticated.

    Attributes:
        logged_in_user: The Revolori ID of the currently logged in user.
    """

    def __init__(self, logged_in_user=Depends(get_current_user)):
        self.logged_in_user = logged_in_user

    def add(self, session: Session, data_access_policy: DataAccessPolicy):
        """ Insert a data access policy into the database """
        data_access_policy.owner_rid = self.logged_in_user
        session.add(data_access_policy)

    def load_all(self, session: Session) -> List[DataAccessPolicy]:
        """ Load all data access policies for the given user. """
        query = session.query(DataAccessPolicy).filter(
            DataAccessPolicy.owner_rid == self.logged_in_user
        )
        return query.all()

    def load_single(
        self, session: Session, data_access_policy_id: int
    ) -> Optional[DataAccessPolicy]:
        """ Load a data access policy by id """
        query = session.query(DataAccessPolicy).filter(
            DataAccessPolicy.id == data_access_policy_id,
            DataAccessPolicy.owner_rid == self.logged_in_user,
        )
        return query.first()

    @staticmethod
    def load_matching(
        session: Session, data_access: DataAccess
    ) -> List[DataAccessPolicy]:
        """ Load all data access policies which permit the given data access """
        owners = [owner.owner_rid for owner in data_access.data_owners]
        date_of_access = data_access.timestamp.date()

        query = session.query(DataAccessPolicy).filter(
            DataAccessPolicy.owner_rid.in_(owners),
            or_(
                DataAccessPolicy.access_kind == data_access.access_kind,
                DataAccessPolicy.access_kind == None,
            ),
            or_(
                DataAccessPolicy.tool == data_access.tool, DataAccessPolicy.tool == None
            ),
            or_(
                DataAccessPolicy.user_rid == data_access.user_rid,
                DataAccessPolicy.user_rid == None,
            ),
            or_(
                DataAccessPolicy.validity_period_end_date >= date_of_access,
                DataAccessPolicy.validity_period_end_date == None,
            ),
            or_(
                DataAccessPolicy.validity_period_start_date <= date_of_access,
                DataAccessPolicy.validity_period_end_date == None,
            ),
        )

        return query.all()

    @classmethod
    def is_access_granted(cls, session: Session, data_access: DataAccess) -> bool:
        """ Checks whether a the data access is allowed by all involved owners """
        policies = cls.load_matching(session, data_access)

        # extract all owners from the data access and deduplicate them using a set.
        involved_owners = {owner.owner_rid for owner in data_access.data_owners}

        # extract all owners from the matching policies and deduplicate them using a set.
        granted_owners = {policy.owner_rid for policy in policies}

        # Since a DataAccess can hold multiple owners, we need to compare sets of owners.
        # `granted_owners` will never be larger than `involved_owners`
        # due to the IN clause on the owner column in `cls.load_matching`.
        # Therefore, we can use strict equality here.
        return involved_owners == granted_owners

    def delete(self, session: Session, data_access_policy_id: int) -> bool:
        """ Deletes a data access policy by id """
        query = session.query(DataAccessPolicy).filter(
            DataAccessPolicy.id == data_access_policy_id,
            DataAccessPolicy.owner_rid == self.logged_in_user,
        )
        return 1 == query.delete()
