from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
from .models import CombustivelEnum, TransmissaoEnum

class AutomobileBase(BaseModel):
    marca: str
    modelo: str
    ano_fabricacao: int = Field(gt=1900, lt=date.today().year + 2)
    ano_modelo: int = Field(gt=1900, lt=date.today().year + 2)
    motorizacao: str
    combustivel: CombustivelEnum
    cor: str
    quilometragem: int = Field(..., ge=0)
    num_portas: int = Field(..., gt=0, lt=7)
    transmissao: TransmissaoEnum
    preco: float = Field(..., gt=0)
    tipo_veiculo: Optional[str] = "Passeio"
    opcionais: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class AutomobileCreate(AutomobileBase):
    #Input de criação (POST).
    pass

class AutomobileDisplay(AutomobileBase):
    id: int
    data_cadastro: date

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class AutomobileFilter(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano_fabricacao_min: Optional[int] = None
    ano_fabricacao_max: Optional[int] = None
    ano_modelo_min: Optional[int] = None
    ano_modelo_max: Optional[int] = None
    combustivel: Optional[CombustivelEnum] = None
    cor: Optional[str] = None
    quilometragem_max: Optional[int] = None
    num_portas: Optional[int] = None
    transmissao: Optional[TransmissaoEnum] = None
    preco_min: Optional[float] = None
    preco_max: Optional[float] = None
    tipo_veiculo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)