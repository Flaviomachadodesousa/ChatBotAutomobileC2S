from sqlalchemy import Column, Integer, String, Float, Date, Enum as SQLAlchemyEnum
from .database import Base
import enum
from datetime import date

class CombustivelEnum(enum.Enum):
    GASOLINA = "Gasolina"
    ALCOOL = "Álcool"
    DIESEL = "Diesel"
    ELETRICO = "Elétrico"
    HIBRIDO = "Híbrido"
    GNV = "GNV"

class TransmissaoEnum(enum.Enum):
    MANUAL = "Manual"
    AUTOMATICO = "Automático"
    CVT = "CVT"
    AUTOMATIZADO = "Automatizado"

class Automobile(Base):
    __tablename__ = "carros"

    # --- Chave Primária ---
    id = Column(Integer, primary_key=True, index=True)

    # --- Outros Atributos do Automóvel ---
    marca = Column(String, index=True, nullable=False) # Fiat
    modelo = Column(String, index=True, nullable=False) # Pulse
    ano_fabricacao = Column(Integer, nullable=False) # "2024"
    ano_modelo = Column(Integer, nullable=False) # Ex: "2025"
    motorizacao = Column(String, nullable=False) # Ex: "1.0 Turbo", "2.0 Aspirado"
    
    combustivel = Column(SQLAlchemyEnum(
        CombustivelEnum,
        name="ck_combustivel",
        native_enum=False,
        values_callable=lambda obj: [e.value for e in obj]
    ), nullable=False) # Ex: Gasolina ou Gásolina
    
    cor = Column(String, nullable=False)# Ex: "Vermelho"
    quilometragem = Column(Integer, nullable=False, default=0) #EX: 145881
    num_portas = Column(Integer, nullable=False) # Ex: "2 ou 4"
    
    transmissao = Column(SQLAlchemyEnum(
        TransmissaoEnum,
        name="ck_transmissao",
        native_enum=False,
        values_callable=lambda obj: [e.value for e in obj]
    ), nullable=False) # EX: Automático OU Automatico
    
    preco = Column(Float, nullable=False) # EX: 60228.14
    data_cadastro = Column(Date, default=date.today) #EX: 2025-06-05
    tipo_veiculo = Column(String, default="Passeio") # Ex: "Passeio", "SUV", "Picape"
    opcionais = Column(String, nullable=True) # Ex: "Ar condicionado,Vidro elétrico,Teto solar"

    def __repr__(self):
        return f"<Automobile(id={self.id}, marca='{self.marca}', modelo='{self.modelo}', ano='{self.ano_modelo}')>"