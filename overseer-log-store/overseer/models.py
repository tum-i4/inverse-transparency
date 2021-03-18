#!/usr/bin/env python3
""" Definitions of models """

import datetime as dt
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RevoloriId(str):
    """
    Type which represents an ID which managed by Revolori.
    """

    pass


class DataAccessKind(str, Enum):
    """
    Enum representing all forms of access.
    """

    DIRECT = "Direkt"
    QUERY = "Query"
    AGGREGATE = "Aggregation"


class DataAccessSingleOwner(BaseModel):
    """
    A view of a data access.
    The view only contains the data owner who is requesting this view.
    The other owners are not included for privacy reasons.
    """

    access_kind: DataAccessKind = Field(
        ..., description="The kind of data access which was performed."
    )

    data_types: List[str] = Field(
        ...,
        description="The types of data which have been accessed, e.g., "
        "Jira issues, email address, etc.",
    )

    justification: Optional[str] = Field(
        ..., description="Plain text why this data access was justified."
    )

    owner_rid: RevoloriId = Field(
        ..., description="The Revolori ID of the user who's data has been accessed."
    )

    timestamp: dt.datetime = Field(
        ..., description="The time when the data was accessed."
    )

    tool: str = Field(
        ...,
        description="The name of the tool which was been used to perform the data "
        "access.",
    )

    user_rid: RevoloriId = Field(
        ..., description="The Revolori ID of the user which performed the data access."
    )


class DataAccessesResponse(BaseModel):
    """
    Response when querying the accesses to the data of a user.
    """

    accesses: List[DataAccessSingleOwner] = Field(
        ..., description="The list of data accesses which concern the requesting user."
    )

    owner_rid: RevoloriId = Field(
        ..., description="The Revolori ID of the user whose data has been accessed."
    )


class RequestAccessRequest(BaseModel):
    """
    Base fields which are the same for all kinds of data access.
    """

    data_types: List[str] = Field(
        ...,
        description="The types of data being accessed, e.g., "
        "Jira issues, email address, etc.",
    )
    justification: Optional[str] = Field(
        ..., description="Plain text why this data access is justified."
    )
    tool: str = Field(
        ..., description="The name of the tool which is accessing the data."
    )
    user: str = Field(
        ...,
        description="The user which is trying to access the data. "
        "(specific to the tool; could be email address, Slack ID, etc.)",
    )


class RequestDirectAccessRequest(RequestAccessRequest):
    """
    Request body when requesting access to the data of a single user.
    """

    owner: str = Field(
        ...,
        description="The user whose data is being accessed. "
        "(specific to the tool; could be email address, Slack ID, etc.)",
    )


class RequestQueryAccessRequest(RequestAccessRequest):
    """
    Request body when requesting access to the data of multiple users
    as part of a search query.
    """

    owners: List[str] = Field(
        ...,
        description="The users whose data are being accessed. "
        "(specific to the tool; could be email address, Slack ID, etc.)",
    )


class RequestAggregateAccessRequest(RequestAccessRequest):
    """
    Request body when requesting access to the data of multiple users
    as part of an aggregate function.
    """

    owners: List[str] = Field(
        ...,
        description="The users whose data are being accessed. "
        "(specific to the tool; could be email address, Slack ID, etc.)",
    )


class RequestAccessResponse(BaseModel):
    """
    Response when requesting access to data.
    """

    granted: bool = Field(
        ...,
        description="Boolean whether access was granted, "
        "i.e. whether the data may be used in an analysis.",
    )


class DataAccessPolicyBase(BaseModel):
    """
    Shared fields between DataAccessPolicy and DataAccessPolicyUpdate
    """

    access_kind: Optional[DataAccessKind] = Field(
        None,
        description="The kind of access which should be allowed. "
        "A wildcard is represented by a null value.",
    )

    tool: Optional[str] = Field(
        None,
        description="The tool which should be allowed access. "
        "A wildcard is represented by a null value.",
    )

    user_rid: Optional[RevoloriId] = Field(
        None,
        description="The Revolori ID of the user who should be allowed access. "
        "A wildcard is represented by a null value.",
    )

    validity_period_end_date: Optional[dt.date] = Field(
        None,
        description="The end of the date range within which this policy is valid. "
        "A wildcard is represented by a null value.",
    )

    validity_period_start_date: Optional[dt.date] = Field(
        None,
        description="The start of the date range within which this policy is valid. "
        "A wildcard is represented by a null value.",
    )


class DataAccessPolicy(DataAccessPolicyBase):
    """
    A data access policy.
    """

    id: int = Field(..., description="The unique id of the data access policy.")


class DataAccessPolicyUpdate(DataAccessPolicyBase):
    """
    Writable fields of a data access policy.
    """

    pass


class Tool(BaseModel):
    """
    A tool which is used for accessing data.
    """

    name: str = Field(..., description="The name of the tool.")
