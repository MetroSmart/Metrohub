from sqlalchemy import Column, Integer, SmallInteger, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AccesoChofer(Base):
    __tablename__ = "accesos_chofer"

    id                = Column(Integer, primary_key=True, index=True)
    chofer_id         = Column(Integer, ForeignKey("choferes.id", ondelete="CASCADE"), nullable=False, unique=True)
    email             = Column(String(100), unique=True, nullable=False, index=True)
    password_hash     = Column(String(255), nullable=False)
    activo            = Column(Boolean, nullable=False, default=True)
    intentos_fallidos = Column(SmallInteger, nullable=False, default=0)
    bloqueado_hasta   = Column(TIMESTAMP, nullable=True)
    ultimo_login      = Column(TIMESTAMP, nullable=True)
    creado_por        = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    created_at        = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at        = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    chofer  = relationship("Chofer", back_populates="acceso")
    creador = relationship("Usuario")
