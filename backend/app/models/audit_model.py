from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func # Pour le timestamp par défaut
from app.db.session import Base # Notre Base déclarative

class Audit(Base):
    __tablename__ = "audits" # Nom de la table dans la base de données

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    event_name = Column(String(255), index=True) # Un nom court pour l'événement
    details = Column(JSON, nullable=True) # Détails plus longs, stockés en JSON

    def __repr__(self):
        return f"<Audit(id={self.id}, event_name='{self.event_name}', timestamp='{self.timestamp}')>"
