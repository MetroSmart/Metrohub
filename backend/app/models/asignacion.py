from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Asignacion(Base):
    __tablename__ = "asignaciones"
    __table_args__ = (
        CheckConstraint("estado IN ('propuesta', 'confirmada', 'cancelada', 'reemplazada')", name="chk_estado_asig"),
        UniqueConstraint("horario_id", "chofer_id", name="uk_horario_chofer"),
    )

    id               = Column(Integer, primary_key=True, index=True)
    horario_id       = Column(Integer, ForeignKey("horarios_servicio.id", ondelete="CASCADE"), nullable=False)
    chofer_id        = Column(Integer, ForeignKey("choferes.id", ondelete="RESTRICT"), nullable=False)
    bus_placa        = Column(String(10), ForeignKey("buses.placa", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)
    concesionario_id = Column(Integer, ForeignKey("concesionarios.id", ondelete="RESTRICT"), nullable=False)
    estado           = Column(String(15), nullable=False, default="propuesta")
    asignado_por     = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    notas            = Column(Text)
    created_at       = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at       = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    horario       = relationship("HorarioServicio", back_populates="asignaciones")
    chofer        = relationship("Chofer",          back_populates="asignaciones")
    bus           = relationship("Bus",             back_populates="asignaciones")
    concesionario = relationship("Concesionario",   back_populates="asignaciones")
    usuario       = relationship("Usuario")
    conflictos    = relationship("Conflicto",       back_populates="asignacion", cascade="all, delete-orphan")
