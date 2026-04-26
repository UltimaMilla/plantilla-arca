from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Comprobante(Base):
    __tablename__ = "comprobantes"

    id = Column(Integer, primary_key=True, index=True)
    cuit_emisor = Column(String(11), nullable=False, index=True)
    tipo_comprobante = Column(Integer, nullable=False)
    punto_venta = Column(Integer, nullable=False)
    numero_comprobante = Column(Integer, nullable=False, index=True)
    cae = Column(String(14), nullable=False, unique=True, index=True)
    vencimiento_cae = Column(Date, nullable=False)
    importe_total = Column(Float, nullable=False)
    fecha_emision = Column(Date, nullable=False, index=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Comprobante {self.tipo_comprobante}/{self.punto_venta}/{self.numero_comprobante}>"
