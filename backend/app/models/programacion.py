from sqlalchemy import Column, Integer, String, TIMESTAMP, Date, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Programacion(Base):
    __tablename__ = "programaciones"
    __table_args__ = (
        CheckConstraint("estado IN ('borrador', 'revision', 'aprobada', 'archivada')", name="chk_estado_prog"),
        CheckConstraint("fecha_fin >= fecha_inicio", name="chk_rango_fechas"),
    )

    id               = Column(Integer, primary_key=True, index=True)
    nombre           = Column(String(100), nullable=False)
    fecha_inicio     = Column(Date, nullable=False)
    fecha_fin        = Column(Date, nullable=False)
    estado           = Column(String(20), nullable=False, default="borrador")
    creado_por       = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    aprobado_por     = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True)
    fecha_aprobacion = Column(TIMESTAMP, nullable=True)
    observaciones    = Column(Text)
    created_at       = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at       = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    creador          = relationship("Usuario", foreign_keys=[creado_por])
    aprobador        = relationship("Usuario", foreign_keys=[aprobado_por])
    horarios_servicio = relationship("HorarioServicio", back_populates="programacion", cascade="all, delete-orphan")
