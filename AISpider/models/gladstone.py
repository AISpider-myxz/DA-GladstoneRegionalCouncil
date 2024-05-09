from sqlalchemy import Column, String, Text, Integer, DateTime, func, UniqueConstraint
from .metadata_base import Base


class Gladstone(Base):
    __tablename__ = 'gladstone'
    id = Column(Integer, primary_key=True)
    application_id = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    submit = Column(Integer, nullable=True)
    status = Column(String(255), nullable=True, server_default=None)
    address = Column(String(512), nullable=True, server_default=None)
    site_address = Column(String(512), nullable=True, default=None)
    decision = Column(Text, nullable=True, server_default=None)
    names = Column(String(255), nullable=True, server_default=None)
    documents = Column(Text, nullable=True, server_default=None)
    
    _tid = Column(String(255), nullable=False, server_default=None)
    created_at = Column(DateTime, server_default=func.now())
    update_at = Column(DateTime, server_default=func.now(), onupdate=func.now())