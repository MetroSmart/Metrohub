from sqlalchemy import Column, Integer, SmallInteger, String, Boolean, TIMESTAMP, Date, Time, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class HorarioServicio(Base):
    __tablename__ = "horarios_servicio"
    __table_args__ = (
        CheckConstraint("turno IN ('manana', 'tarde', 'noche')", name="chk_turno"),
        CheckConstraint("duracion_est_min BETWEEN 15 AND 240", name="chk_duracion"),
        UniqueConstraint("ruta_id", "fecha", "hora_salida", name="uk_ruta_fecha_hora"),
    )

    id               = Column(Integer, primary_key=True, index=True)
    programacion_id  = Column(Integer, ForeignKey("programaciones.id", ondelete="CASCADE"), nullable=False)
    ruta_id          = Column(Integer, ForeignKey("rutas.id", ondelete="RESTRICT"), nullable=False)
    fecha            = Column(Date, nullable=False)
    hora_salida      = Column(Time, nullable=False)
    turno            = Column(String(10), nullable=False)
    duracion_est_min = Column(SmallInteger, nullable=False)
    activo           = Column(Boolean, nullable=False, default=True)
    created_at       = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at       = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    programacion = relationship("Programacion", back_populates="horarios_servicio")
    ruta         = relationship("Ruta",         back_populates="horarios_servicio")
    asignaciones = relationship("Asignacion",   back_populates="horario", cascade="all, delete-orphan")
