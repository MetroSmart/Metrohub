from sqlalchemy import Column, Integer, String, TIMESTAMP, Date, Time, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class DisponibilidadChofer(Base):
    __tablename__ = "disponibilidad_chofer"
    __table_args__ = (
        CheckConstraint(
            "motivo IN ('descanso', 'vacaciones', 'medico', 'capacitacion', 'personal', 'otro')",
            name="chk_motivo_disp",
        ),
        CheckConstraint("hora_desde < hora_hasta", name="chk_rango_horario"),
    )

    id             = Column(Integer, primary_key=True, index=True)
    chofer_id      = Column(Integer, ForeignKey("choferes.id", ondelete="CASCADE"), nullable=False)
    fecha          = Column(Date, nullable=False)
    hora_desde     = Column(Time, nullable=False)
    hora_hasta     = Column(Time, nullable=False)
    motivo         = Column(String(30), nullable=False)
    observaciones  = Column(Text)
    registrado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    created_at     = Column(TIMESTAMP, nullable=False, server_default=func.now())

    chofer  = relationship("Chofer",   back_populates="disponibilidades")
    usuario = relationship("Usuario")
