#!/usr/bin/env python3
""" Database models """

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

ACCESS_KIND = String(20)
REVOLORI_ID = String(100)


Base = declarative_base()


class DataAccess(Base):
    __tablename__ = "data_accesses"

    id = Column(Integer, primary_key=True)

    access_kind = Column(ACCESS_KIND, nullable=False)
    data_owners = relationship("DataOwner")
    data_types = relationship("DataType")
    justification = Column(Text)
    timestamp = Column(DateTime, nullable=False)
    tool = Column(
        String,
        ForeignKey("tools.name", name="fk__data_accesses__tool__tools"),
        nullable=False,
    )
    user_rid = Column(REVOLORI_ID, nullable=False)


class DataOwner(Base):
    __tablename__ = "data_owners"

    data_access_id = Column(Integer, ForeignKey("data_accesses.id"), primary_key=True)
    owner_rid = Column(REVOLORI_ID, primary_key=True)


class DataType(Base):
    __tablename__ = "data_types"

    data_access_id = Column(Integer, ForeignKey("data_accesses.id"), primary_key=True)
    type = Column(String(100), primary_key=True)


class DataAccessPolicy(Base):
    __tablename__ = "data_access_policies"

    id = Column(Integer, primary_key=True)

    access_kind = Column(ACCESS_KIND)
    owner_rid = Column(REVOLORI_ID, nullable=False)
    tool = Column(
        String, ForeignKey("tools.name", name="fk__data_access_policies__tool__tools")
    )
    user_rid = Column(REVOLORI_ID)
    validity_period_end_date = Column(Date)
    validity_period_start_date = Column(Date)


class Tool(Base):
    __tablename__ = "tools"

    name = Column(String(20), primary_key=True)
