from sqlalchemy import Column, Integer, SmallInteger, String, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Bus(Base):
    __tablename__ = "buses"
    __table_args__ = (
        CheckConstraint("tipo IN ('articulado', 'convencional')", name="chk_tipo_bus"),
        CheckConstraint("estado IN ('operativo', 'mantenimiento', 'baja', 'reparacion')", name="chk_estado_bus"),
        CheckConstraint("anio BETWEEN 1990 AND 2100", name="chk_anio_razonable"),
        CheckConstraint("LENGTH(placa) BETWEEN 6 AND 10", name="chk_placa_formato"),
    )

    placa               = Column(String(10), primary_key=True)
    concesionario_id    = Column(Integer, ForeignKey("concesionarios.id", ondelete="RESTRICT"), nullable=False)
    tipo                = Column(String(20), nullable=False)
    anio                = Column(SmallInteger)
    capacidad_pasajeros = Column(SmallInteger)
    estado              = Column(String(20), nullable=False, default="operativo")
    created_at          = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at          = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    concesionario = relationship("Concesionario", back_populates="buses")
    asignaciones  = relationship("Asignacion", back_populates="bus")
