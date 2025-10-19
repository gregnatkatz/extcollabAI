"""
Database models and connection management for AdventHealth Research Platform.
Uses SQLAlchemy ORM with Azure SQL Database.
"""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Text, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from datetime import datetime
import uuid
from typing import Optional
from app.config import settings

Base = declarative_base()

class Project(Base):
    """Projects table"""
    __tablename__ = 'Projects'
    
    ProjectId = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    Name = Column(String(255), nullable=False)
    PIUserId = Column(String(255), nullable=False)
    PIName = Column(String(255), nullable=False)
    PIEmail = Column(String(255), nullable=False)
    FabricWorkspaceId = Column(String(255), nullable=False)
    FabricWorkspaceUrl = Column(String(500))
    MLWorkspaceId = Column(String(255))
    MLWorkspaceUrl = Column(String(500))
    Status = Column(String(50), default='Active')
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    UpdatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    members = relationship("ProjectMember", back_populates="project")
    export_requests = relationship("ExportRequest", back_populates="project")

class ProjectMember(Base):
    """Project members table (B2B access control)"""
    __tablename__ = 'ProjectMembers'
    
    MemberId = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    ProjectId = Column(UNIQUEIDENTIFIER, ForeignKey('Projects.ProjectId'), nullable=False)
    UserId = Column(String(255), nullable=False, index=True)
    UserEmail = Column(String(255), nullable=False)
    UserName = Column(String(255))
    Institution = Column(String(255))
    Role = Column(String(50), nullable=False)
    AccessGrantedAt = Column(DateTime, default=datetime.utcnow)
    AccessExpiresAt = Column(DateTime, nullable=False)
    CanExport = Column(Boolean, default=False)
    IsActive = Column(Boolean, default=True)
    CreatedBy = Column(String(255), nullable=False)
    
    project = relationship("Project", back_populates="members")

class ExportRequest(Base):
    """Export requests table"""
    __tablename__ = 'ExportRequests'
    
    RequestId = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    RequestNumber = Column(String(50), unique=True, nullable=False)
    ProjectId = Column(UNIQUEIDENTIFIER, ForeignKey('Projects.ProjectId'), nullable=False)
    RequestorUserId = Column(String(255), nullable=False, index=True)
    RequestorEmail = Column(String(255), nullable=False)
    DatasetName = Column(String(255), nullable=False)
    RowCount = Column(Integer)
    Justification = Column(Text, nullable=False)
    Status = Column(String(50), default='Pending', index=True)
    PIReviewerId = Column(String(255))
    PIReviewerEmail = Column(String(255))
    ReviewedAt = Column(DateTime)
    ReviewNotes = Column(Text)
    DownloadUrl = Column(String(500))
    DownloadExpiresAt = Column(DateTime)
    RequestedAt = Column(DateTime, default=datetime.utcnow)
    CompletedAt = Column(DateTime)
    
    project = relationship("Project", back_populates="export_requests")

class ActivityLog(Base):
    """Activity log table (audit trail)"""
    __tablename__ = 'ActivityLog'
    
    ActivityId = Column(BigInteger, primary_key=True, autoincrement=True)
    UserId = Column(String(255), nullable=False, index=True)
    UserEmail = Column(String(255))
    ProjectId = Column(UNIQUEIDENTIFIER)
    ActivityType = Column(String(100), nullable=False, index=True)
    ActivityDetails = Column(Text)
    ResourceId = Column(String(255))
    IPAddress = Column(String(50))
    UserAgent = Column(String(500))
    CreatedAt = Column(DateTime, default=datetime.utcnow, index=True)

class Notification(Base):
    """Notifications table"""
    __tablename__ = 'Notifications'
    
    NotificationId = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    UserId = Column(String(255), nullable=False, index=True)
    Type = Column(String(50), nullable=False)
    Message = Column(Text, nullable=False)
    IsRead = Column(Boolean, default=False, index=True)
    RelatedEntityType = Column(String(50))
    RelatedEntityId = Column(String(255))
    CreatedAt = Column(DateTime, default=datetime.utcnow)

def get_database_engine():
    """
    Create database engine.
    In production, uses Azure SQL Database with managed identity.
    In development, uses mock in-memory database.
    """
    if settings.DATABASE_URL and not settings.is_development():
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
    else:
        engine = create_engine(
            'sqlite:///:memory:',
            echo=settings.DEBUG
        )
    
    return engine

def init_database():
    """Initialize database tables"""
    engine = get_database_engine()
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get database session"""
    engine = get_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_db():
    """
    Dependency for FastAPI endpoints to get database session.
    Usage: def endpoint(db: Session = Depends(get_db)):
    """
    db = get_session()
    try:
        yield db
    finally:
        db.close()
