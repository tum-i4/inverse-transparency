#!/usr/bin/env python3
""" overseer: Inverse Transparency log store """

import datetime as dt
from typing import List, Optional, Tuple

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

import overseer.models as dto
from overseer.auth import admin_user_logged_in, technical_user_logged_in
from overseer.dao.data_access import DataAccessDao
from overseer.dao.data_access_policy import DataAccessPolicyDao
from overseer.dao.tool import ToolDao
from overseer.db.connection import Session, close_db, get_db, init_db
from overseer.db.models import DataAccess, DataAccessPolicy, DataOwner, DataType, Tool
from overseer.exception import (
    handle_owner_not_signed_up,
    handle_user_not_signed_up,
    http_exception,
)
from overseer.models import DataAccessKind, RevoloriId
from overseer.services import RevoloriService
from starlette.responses import RedirectResponse, Response
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

DOCS_URL = "/docs"

overseer = FastAPI(docs_url=DOCS_URL)

overseer.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


##### APP LIFECYCLE #####


@overseer.on_event("startup")
def startup():
    """ Called on app startup """
    init_db()


@overseer.on_event("shutdown")
def shutdown():
    """ Called on app shutdown """
    close_db()


##### ROUTES #####


@overseer.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url=DOCS_URL)


@overseer.get("/health", response_model=None)
def check_health(session: Session = Depends(get_db)):
    try:
        session.execute("SELECT 1")
    except Exception as exc:
        raise HTTPException(
            HTTP_500_INTERNAL_SERVER_ERROR, detail="Database is unavailable."
        ) from exc


@overseer.get("/data-accesses", response_model=dto.DataAccessesResponse)
def get_data_accesses(
    date_start: dt.date = Query(None, description="Start of the relevant date range."),
    date_end: dt.date = Query(None, description="End of the relevant date range."),
    limit: int = Query(None, description="Maximum number of entries to return."),
    dao: DataAccessDao = Depends(),
    session: Session = Depends(get_db),
):
    """ Retrieve stored data accesses. """

    with session:
        accesses: List[DataAccess] = dao.load_all(
            session=session, date_start=date_start, date_end=date_end, limit=limit,
        )

        single_owner_accesses = [
            dto.DataAccessSingleOwner(
                access_kind=access.access_kind,
                data_types=[data_type.type for data_type in access.data_types],
                justification=access.justification,
                owner_rid=dao.logged_in_user,
                timestamp=access.timestamp,
                tool=access.tool,
                user_rid=access.user_rid,
            )
            for access in accesses
        ]

        return dto.DataAccessesResponse(
            owner_rid=dao.logged_in_user, accesses=single_owner_accesses
        )


def check_consent_and_log_access(
    session: Session, data_access: DataAccess
) -> dto.RequestAccessResponse:
    """ Helper function for checking whether an access is allowed and logging it. """
    granted = DataAccessPolicyDao.is_access_granted(session, data_access)
    if granted:
        DataAccessDao.add(session, data_access)
    return dto.RequestAccessResponse(granted=granted)


def validate_tool_exists(session: Session, tool_name: Optional[str]):
    """
    Helper function for validating that the tool exists in the DB.
    The tool's existence is also enforced through foreign key constraints.

    The purpose of this function is to return a 400 error instead of a generic 500 error
    caused by a constraint violation.
    """
    if tool_name is not None and ToolDao.load_single(session, tool_name) is None:
        raise HTTPException(HTTP_400_BAD_REQUEST, f"Tool '{tool_name}' is unknown.")


@overseer.post(
    "/request-access/direct",
    response_model=dto.RequestAccessResponse,
    dependencies=[Depends(technical_user_logged_in)],
)
def request_direct_access(
    body: dto.RequestDirectAccessRequest,
    session: Session = Depends(get_db),
    revolori_service: RevoloriService = Depends(),
):
    """
    Requests direct access to the data of a single individual.
    E.g. data which has been accessed by its id.
    """
    with session:
        validate_tool_exists(session, body.tool)

        with handle_owner_not_signed_up():
            owner_rid = revolori_service.map_id(body.tool, body.owner)

        with handle_user_not_signed_up():
            user_rid = revolori_service.map_id(body.tool, body.user)

        data_access = DataAccess(
            user_rid=user_rid,
            tool=body.tool,
            access_kind=DataAccessKind.DIRECT,
            timestamp=dt.datetime.now(),
            justification=body.justification,
        )
        data_access.data_owners = [DataOwner(owner_rid=owner_rid)]
        data_access.data_types = [
            DataType(type=data_type) for data_type in body.data_types
        ]

        return check_consent_and_log_access(session, data_access)


@overseer.post(
    "/request-access/query",
    response_model=dto.RequestAccessResponse,
    dependencies=[Depends(technical_user_logged_in)],
)
def request_query_access(
    body: dto.RequestQueryAccessRequest,
    session: Session = Depends(get_db),
    revolori_service: RevoloriService = Depends(),
):
    """
    Requests access to the data of multiple individuals as part of a search query.
    E.g. data which has been displayed as part of a search result.
    """
    with session:
        validate_tool_exists(session, body.tool)

        with handle_owner_not_signed_up():
            owner_rids = revolori_service.map_ids(body.tool, body.owners)

        with handle_user_not_signed_up():
            user_rid = revolori_service.map_id(body.tool, body.user)

        data_access = DataAccess(
            user_rid=user_rid,
            tool=body.tool,
            access_kind=DataAccessKind.QUERY,
            timestamp=dt.datetime.now(),
            justification=body.justification,
        )
        data_access.data_owners = [
            DataOwner(owner_rid=owner_rid) for owner_rid in owner_rids
        ]
        data_access.data_types = [
            DataType(type=data_type) for data_type in body.data_types
        ]

        return check_consent_and_log_access(session, data_access)


@overseer.post(
    "/request-access/aggregate",
    response_model=dto.RequestAccessResponse,
    dependencies=[Depends(technical_user_logged_in)],
)
def request_aggregate_access(
    body: dto.RequestAggregateAccessRequest,
    session: Session = Depends(get_db),
    revolori_service: RevoloriService = Depends(),
):
    """
    Requests access to the data of multiple individuals as part of an aggregate function.
    """
    with session:
        validate_tool_exists(session, body.tool)

        with handle_owner_not_signed_up():
            owner_rids = revolori_service.map_ids(body.tool, body.owners)

        with handle_user_not_signed_up():
            user_rid = revolori_service.map_id(body.tool, body.user)

        data_access = DataAccess(
            user_rid=user_rid,
            tool=body.tool,
            access_kind=DataAccessKind.AGGREGATE,
            timestamp=dt.datetime.now(),
            justification=body.justification,
        )
        data_access.data_owners = [
            DataOwner(owner_rid=owner_rid) for owner_rid in owner_rids
        ]
        data_access.data_types = [
            DataType(type=data_type) for data_type in body.data_types
        ]

        return check_consent_and_log_access(session, data_access)


@overseer.post(
    "/generate", response_model=str, dependencies=[Depends(admin_user_logged_in)],
)
def generate(
    owner_rid: RevoloriId = Query(
        ...,
        description="Revolori ID of the data owner for whom the data accesses should be "
        "generated.",
    ),
    date_start: dt.date = Query(
        ...,
        description="Start of the date range within which the data accesses should be "
        "generated.",
    ),
    date_end: dt.date = Query(
        ...,
        description="End of the date range within which the data accesses should be "
        "generated.",
    ),
    number_of_entries: int = Query(
        ..., description="The number of entries which should be generated."
    ),
    session: Session = Depends(get_db),
):
    """ Generate fake entries. """
    date_range: Tuple[dt.date, dt.date] = (date_start, date_end)

    with session:
        tools = [tool.name for tool in ToolDao.load_all(session)]

        if not tools:
            raise HTTPException(HTTP_400_BAD_REQUEST, "DB contains no tools.")

        DataAccessDao.generate_log(
            session=session,
            owner_rid=owner_rid,
            date_range=date_range,
            number_of_entries=number_of_entries,
            tools=tools,
        )
        return f"{number_of_entries} entries were added"


@overseer.get("/data-access-policies", response_model=List[dto.DataAccessPolicy])
def get_data_access_policies(
    dao: DataAccessPolicyDao = Depends(), session: Session = Depends(get_db),
):
    """ Load all data access policies for the logged in user. """
    with session:
        data_access_policies: List[DataAccessPolicy] = dao.load_all(session=session)
        return [
            dto.DataAccessPolicy(**policy.__dict__) for policy in data_access_policies
        ]


@overseer.post("/data-access-policies", response_model=dto.DataAccessPolicy)
def create_data_access_policy(
    policy: dto.DataAccessPolicyUpdate,
    dao: DataAccessPolicyDao = Depends(),
    session: Session = Depends(get_db),
):
    """ Create a data access policy for the logged in user. """
    with session:
        validate_tool_exists(session, policy.tool)

        data_access_policy = DataAccessPolicy(**policy.dict())

        dao.add(session=session, data_access_policy=data_access_policy)
        session.flush()  # persist entity to get an id
        return dto.DataAccessPolicy(**data_access_policy.__dict__)


@overseer.get(
    "/data-access-policies/{data_access_policy_id}",
    response_model=dto.DataAccessPolicy,
)
def get_data_access_policy(
    data_access_policy_id: int,
    dao: DataAccessPolicyDao = Depends(),
    session: Session = Depends(get_db),
):
    """ Get a data access policy by id. """
    with session:
        data_access_policy = dao.load_single(
            session=session, data_access_policy_id=data_access_policy_id,
        )

        if data_access_policy is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)

        return dto.DataAccessPolicy(**data_access_policy.__dict__)


@overseer.put(
    "/data-access-policies/{data_access_policy_id}",
    response_model=dto.DataAccessPolicy,
)
def update_data_access_policy(
    data_access_policy_id: int,
    policy_update: dto.DataAccessPolicyUpdate,
    dao: DataAccessPolicyDao = Depends(),
    session: Session = Depends(get_db),
):
    """ Update a data access policy. """
    with session:
        validate_tool_exists(session, policy_update.tool)

        data_access_policy = dao.load_single(
            session=session, data_access_policy_id=data_access_policy_id,
        )

        if data_access_policy is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)

        for key, value in policy_update.dict().items():
            setattr(data_access_policy, key, value)

        return dto.DataAccessPolicy(**data_access_policy.__dict__)


@overseer.delete(
    "/data-access-policies/{data_access_policy_id}", status_code=204,
)
def delete_data_access_policy(
    data_access_policy_id: int,
    dao: DataAccessPolicyDao = Depends(),
    session: Session = Depends(get_db),
):
    """ Update a data access policy. """
    with session:
        succeeded = dao.delete(
            session=session, data_access_policy_id=data_access_policy_id,
        )

        if not succeeded:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)

        return Response(status_code=HTTP_204_NO_CONTENT)


@overseer.get("/tool-types", response_model=List[dto.Tool])
def get_tool_types(session: Session = Depends(get_db)):
    """ Get all tool types. """
    with session:
        return [dto.Tool(**tool.__dict__) for tool in ToolDao.load_all(session)]


@overseer.post(
    "/tool-types",
    response_model=dto.Tool,
    dependencies=[Depends(admin_user_logged_in)],
)
def create_tool_type(tool: dto.Tool, session: Session = Depends(get_db)):
    """ Create a new tool type. """
    with session:
        if ToolDao.load_single(session, tool.name) is not None:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail=f"Tool '{tool.name}' already exists.",
            )

        new_tool = Tool(**tool.dict())
        ToolDao.add(session, new_tool)
        return dto.Tool(**new_tool.__dict__)


@overseer.delete(
    "/tool-types/{tool_name}",
    status_code=204,
    dependencies=[Depends(admin_user_logged_in)],
)
def delete_tool_type(tool_name: str, session: Session = Depends(get_db)):
    """ Delete a tool type. """
    exception_mapper = http_exception(
        IntegrityError,
        HTTP_500_INTERNAL_SERVER_ERROR,
        "Something went wrong. The tool might be still in use. Please check the server "
        "logs.",
    )
    with exception_mapper, session:
        succeeded = ToolDao.delete(session, tool_name)

        if not succeeded:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)

        return Response(status_code=HTTP_204_NO_CONTENT)


##### ENTRY POINT #####


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:overseer", host="127.0.0.1", port=5421, log_level="info")
