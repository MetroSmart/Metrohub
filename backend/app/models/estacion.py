from sqlalchemy import Column, Integer, SmallInteger, String, Boolean, TIMESTAMP, Numeric, CheckConstraint
from sqlalchemy.sql import func
from app.database import Base


class Estacion(Base):
    __tablename__ = "estaciones"
    __table_args__ = (
        CheckConstraint("tipo IN ('terminal', 'intermedia', 'transferencia')", name="chk_tipo_estacion"),
        CheckConstraint("tramo IN ('norte', 'centro', 'sur')", name="chk_tramo"),
    )

    id             = Column(Integer, primary_key=True, index=True)
    codigo         = Column(String(20), unique=True, nullable=False)
    nombre         = Column(String(100), nullable=False)
    tipo           = Column(String(20), nullable=False)
    tramo          = Column(String(20), nullable=False)
    orden_troncal  = Column(SmallInteger)
    latitud        = Column(Numeric(10, 8))
    longitud       = Column(Numeric(11, 8))
    activa         = Column(Boolean, nullable=False, default=True)
    created_at     = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at     = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
