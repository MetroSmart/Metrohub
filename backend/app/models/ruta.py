from sqlalchemy import Column, Integer, SmallInteger, String, Boolean, TIMESTAMP, Time, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Ruta(Base):
    __tablename__ = "rutas"
    __table_args__ = (
        CheckConstraint("tipo IN ('regular', 'expreso', 'nocturna')", name="chk_tipo_ruta"),
        CheckConstraint("frecuencia_min BETWEEN 2 AND 60", name="chk_frecuencia"),
    )

    id             = Column(Integer, primary_key=True, index=True)
    codigo         = Column(String(10), unique=True, nullable=False)
    nombre         = Column(String(100), nullable=False)
    tipo           = Column(String(20), nullable=False)
    hora_inicio    = Column(Time, nullable=False)
    hora_fin       = Column(Time, nullable=False)
    frecuencia_min = Column(SmallInteger, nullable=False)
    activa         = Column(Boolean, nullable=False, default=True)
    created_at     = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at     = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    estaciones       = relationship("RutaEstacion", back_populates="ruta", cascade="all, delete-orphan")
    horarios_servicio = relationship("HorarioServicio", back_populates="ruta")


class RutaEstacion(Base):
    __tablename__ = "ruta_estacion"
    __table_args__ = (
        UniqueConstraint("ruta_id", "orden", name="uk_ruta_orden"),
    )

    ruta_id        = Column(Integer, ForeignKey("rutas.id", ondelete="CASCADE"), primary_key=True)
    estacion_id    = Column(Integer, ForeignKey("estaciones.id", ondelete="RESTRICT"), primary_key=True)
    orden          = Column(SmallInteger, nullable=False)
    tiempo_est_min = Column(SmallInteger)

    ruta     = relationship("Ruta",     back_populates="estaciones")
    estacion = relationship("Estacion")
