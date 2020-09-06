"""Sqlalchemy models."""
import os

from dotenv import load_dotenv
from eralchemy import render_er
from sqlalchemy import (
    DDL,
    Column,
    DateTime,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    String,
    create_engine,
    event,
)
from sqlalchemy.ext.declarative import declarative_base

load_dotenv(override=True)
Base = declarative_base()

SCHEMA = "drugbank"


def db_connect():
    """Create database connection and return sqlalchemy engine."""
    return create_engine(os.environ.get("CONNECTION_STRING"))


def create_table(engine):
    event.listen(
        Base.metadata, "before_create", DDL(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
    )
    Base.metadata.create_all(engine)

    render_er(os.environ.get("CONNECTION_STRING"), "static/drugbank_schema.png")


class Drug(Base):
    __tablename__ = "drugs"
    __table_args__ = (
        PrimaryKeyConstraint("id", "scraped_at"),
        {"schema": SCHEMA},
    )

    id = Column(String)
    smiles = Column(String)
    scraped_at = Column(DateTime)


class Target(Base):
    __tablename__ = "targets"

    target_id = Column(String)
    drug_id = Column(String)
    gene_name = Column(String)
    scraped_at = Column(DateTime)

    __table_args__ = (
        PrimaryKeyConstraint("target_id", "scraped_at"),
        ForeignKeyConstraint((drug_id, scraped_at), [Drug.id, Drug.scraped_at]),
        {"schema": SCHEMA},
    )


class Action(Base):
    __tablename__ = "actions"

    target_id = Column(String)
    name = Column(String)
    scraped_at = Column(DateTime)

    __table_args__ = (
        PrimaryKeyConstraint("target_id", "name", "scraped_at"),
        ForeignKeyConstraint(
            (target_id, scraped_at), [Target.target_id, Target.scraped_at]
        ),
        {"schema": SCHEMA},
    )


class ExternalIdentifier(Base):
    __tablename__ = "external_identifiers"

    target_id = Column(String)
    name = Column(String)
    value = Column(String)
    url = Column(String)
    scraped_at = Column(DateTime)

    __table_args__ = (
        PrimaryKeyConstraint("target_id", "name", "scraped_at"),
        ForeignKeyConstraint(
            (target_id, scraped_at), [Target.target_id, Target.scraped_at]
        ),
        {"schema": SCHEMA},
    )
