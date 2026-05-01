from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Concesionario(Base):
    __tablename__ = "concesionarios"
    __table_args__ = (
        CheckConstraint("LENGTH(ruc) = 11", name="chk_ruc_longitud"),
    )

    id             = Column(Integer, primary_key=True, index=True)
    ruc            = Column(String(11), unique=True, nullable=False)
    razon_social   = Column(String(150), nullable=False)
    nombre_corto   = Column(String(50), nullable=False)
    telefono       = Column(String(20))
    email_contacto = Column(String(100))
    activo         = Column(Boolean, nullable=False, default=True)
    created_at     = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at     = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    usuarios  = relationship("Usuario",  back_populates="concesionario")
    choferes  = relationship("Chofer",   back_populates="concesionario")
    buses     = relationship("Bus",      back_populates="concesionario")
    asignaciones = relationship("Asignacion", back_populates="concesionario")
