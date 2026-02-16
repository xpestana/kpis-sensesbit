from datetime import datetime

from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

OrganizationBase = declarative_base()


class Organization(OrganizationBase):
    __tablename__ = "organizations"
    __table_args__ = {"schema": settings.GLOBAL_SCHEMA}

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    license_type = Column(String, nullable=False)
    license_expiry = Column(DateTime, nullable=False)
    credits = Column(Integer, nullable=False, default=0)
    credits_ia = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
