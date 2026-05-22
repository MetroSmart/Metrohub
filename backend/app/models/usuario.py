from sqlalchemy import Column, Integer, SmallInteger, String, Boolean, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint("rol IN ('admin_atu', 'supervisor_concesionario')", name="chk_rol_valido"),
        CheckConstraint(
            "(rol = 'admin_atu' AND concesionario_id IS NULL) OR "
            "(rol = 'supervisor_concesionario' AND concesionario_id IS NOT NULL)",
            name="chk_supervisor_tiene_concesionario",
        ),
        CheckConstraint("LENGTH(dni) = 8", name="chk_dni_longitud"),
    )

    id                = Column(Integer, primary_key=True, index=True)
    email             = Column(String(100), unique=True, nullable=False, index=True)
    password_hash     = Column(String(255), nullable=False)
    nombre            = Column(String(100), nullable=False)
    apellidos         = Column(String(100), nullable=False)
    dni               = Column(String(8), unique=True, nullable=False)
    rol               = Column(String(30), nullable=False)
    concesionario_id  = Column(Integer, ForeignKey("concesionarios.id", ondelete="RESTRICT"), nullable=True)
    activo            = Column(Boolean, nullable=False, default=True)
    intentos_fallidos = Column(SmallInteger, nullable=False, default=0)
    bloqueado_hasta   = Column(TIMESTAMP, nullable=True)
    ultimo_login      = Column(TIMESTAMP, nullable=True)
    created_at        = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at        = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    concesionario = relationship("Concesionario", back_populates="usuarios")
