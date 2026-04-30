from sqlalchemy import Column, Integer, SmallInteger, String, TIMESTAMP, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Chofer(Base):
    __tablename__ = "choferes"
    __table_args__ = (
        CheckConstraint("tipo_licencia IN ('A-IIIA', 'A-IIIB', 'A-IIIC')", name="chk_tipo_licencia"),
        CheckConstraint(
            "estado IN ('activo', 'suspendido', 'licencia_medica', 'vacaciones', 'inactivo')",
            name="chk_estado_chofer",
        ),
        CheckConstraint("LENGTH(dni) = 8", name="chk_dni_chofer_longitud"),
    )

    id                    = Column(Integer, primary_key=True, index=True)
    dni                   = Column(String(8), unique=True, nullable=False)
    nombres               = Column(String(100), nullable=False)
    apellidos             = Column(String(100), nullable=False)
    fecha_nacimiento      = Column(Date, nullable=False)
    telefono              = Column(String(20))
    email                 = Column(String(100))
    concesionario_id      = Column(Integer, ForeignKey("concesionarios.id", ondelete="RESTRICT"), nullable=False)
    numero_licencia       = Column(String(20), unique=True, nullable=False)
    tipo_licencia         = Column(String(10), nullable=False)
    fec_vence_licencia    = Column(Date, nullable=False)
    fec_vence_certif_prot = Column(Date, nullable=False)
    estado                = Column(String(20), nullable=False, default="activo")
    anios_experiencia     = Column(SmallInteger)
    created_at            = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at            = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    concesionario     = relationship("Concesionario", back_populates="choferes")
    disponibilidades  = relationship("DisponibilidadChofer", back_populates="chofer", cascade="all, delete-orphan")
    asignaciones      = relationship("Asignacion", back_populates="chofer")
