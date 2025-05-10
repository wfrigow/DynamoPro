"""
Modèles de base de données pour l'API de subventions
--------------------------------------------------
Définit les modèles SQLAlchemy pour la persistance des données
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """Modèle pour les utilisateurs de l'API de subventions"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    applications = relationship("Application", back_populates="user")
    drafts = relationship("ApplicationDraft", back_populates="user")


class Application(Base):
    """Modèle pour les applications de subventions"""
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    reference_number = Column(String(20), unique=True, index=True, nullable=False)
    subsidy_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="submitted")
    status_label = Column(String(50), nullable=False, default="Soumise")
    submission_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Données de l'application
    applicant_data = Column(JSON, nullable=False)
    property_data = Column(JSON, nullable=False)
    project_data = Column(JSON, nullable=False)
    bank_details = Column(JSON, nullable=True)
    subsidy_data = Column(JSON, nullable=False)
    next_steps = Column(JSON, nullable=True)

    # Relations
    user = relationship("User", back_populates="applications")
    documents = relationship("ApplicationDocument", back_populates="application")
    notes = relationship("ApplicationNote", back_populates="application")
    history = relationship("ApplicationHistory", back_populates="application", order_by="ApplicationHistory.date.desc()")


class ApplicationDraft(Base):
    """Modèle pour les brouillons d'applications de subventions"""
    __tablename__ = "application_drafts"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    subsidy_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Données du brouillon
    applicant_data = Column(JSON, nullable=True)
    property_data = Column(JSON, nullable=True)
    project_data = Column(JSON, nullable=True)
    bank_details = Column(JSON, nullable=True)

    # Relations
    user = relationship("User", back_populates="drafts")


class ApplicationDocument(Base):
    """Modèle pour les documents d'une application de subvention"""
    __tablename__ = "application_documents"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    upload_date = Column(DateTime, default=datetime.utcnow)
    validation_date = Column(DateTime, nullable=True)
    comments = Column(Text, nullable=True)
    size = Column(Integer, nullable=True)
    file_path = Column(String(255), nullable=True)
    content_type = Column(String(100), nullable=True)

    # Relations
    application = relationship("Application", back_populates="documents")


class ApplicationNote(Base):
    """Modèle pour les notes d'une application de subvention"""
    __tablename__ = "application_notes"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    author = Column(String(255), nullable=False)
    author_type = Column(String(20), nullable=False)  # admin, user
    content = Column(Text, nullable=False)

    # Relations
    application = relationship("Application", back_populates="notes")


class ApplicationHistory(Base):
    """Modèle pour l'historique d'une application de subvention"""
    __tablename__ = "application_history"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)

    # Relations
    application = relationship("Application", back_populates="history")
