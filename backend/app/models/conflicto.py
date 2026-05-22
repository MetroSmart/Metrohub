from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Conflicto(Base):
    __tablename__ = "conflictos"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('solapamiento_turno', 'exceso_8h_dia', 'chofer_no_disponible', "
            "'licencia_vencida', 'certif_prot_vencida', 'descanso_insuficiente', "
            "'concesionario_incorrecto', 'bus_no_operativo', 'otro')",
            name="chk_tipo_conflicto",
        ),
        CheckConstraint("severidad IN ('baja', 'media', 'alta', 'critica')", name="chk_severidad"),
    )

    id               = Column(Integer, primary_key=True, index=True)
    asignacion_id    = Column(Integer, ForeignKey("asignaciones.id", ondelete="CASCADE"), nullable=False)
    tipo             = Column(String(30), nullable=False)
    severidad        = Column(String(10), nullable=False, default="media")
    descripcion      = Column(Text, nullable=False)
    resuelto         = Column(Boolean, nullable=False, default=False)
    resuelto_por     = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    fecha_resolucion = Column(TIMESTAMP, nullable=True)
    created_at       = Column(TIMESTAMP, nullable=False, server_default=func.now())

    asignacion = relationship("Asignacion", back_populates="conflictos")
    usuario    = relationship("Usuario")
