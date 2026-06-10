from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AreaOperativa(Base):
    __tablename__ = "areas_operativas"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String(100), nullable=False)
    nombre_corto = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    activo      = Column(Boolean, nullable=False, default=True)
    created_at  = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at  = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    usuarios     = relationship("Usuario",      back_populates="area")
    choferes     = relationship("Chofer",       back_populates="area")
    buses        = relationship("Bus",          back_populates="area")
    asignaciones = relationship("Asignacion",   back_populates="area")
