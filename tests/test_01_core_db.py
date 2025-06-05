from sqlalchemy.orm import Session
from core.models import Automobile, CombustivelEnum, TransmissaoEnum
from core.schemas import AutomobileCreate
from datetime import date

def test_create_automobile_instance(db_session: Session):
    auto_data = AutomobileCreate(
        marca="TestMarca",
        modelo="TestModelo",
        ano_fabricacao=2022,
        ano_modelo=2022,
        motorizacao="1.4 Turbo",
        combustivel=CombustivelEnum.GASOLINA,
        cor="Azul",
        quilometragem=100,
        num_portas=4,
        transmissao=TransmissaoEnum.AUTOMATICO,
        preco=75000.00,
        tipo_veiculo="Sedan"
    )
    
    db_auto = Automobile(**auto_data.model_dump())
    db_session.add(db_auto)
    db_session.commit()
    db_session.refresh(db_auto)

    assert db_auto.id is not None
    assert db_auto.marca == "TestMarca"
    assert db_auto.combustivel == CombustivelEnum.GASOLINA
    assert db_auto.data_cadastro == date.today()

def test_query_automobile(db_session: Session):
    auto = Automobile(
        marca="OutraMarca",
        modelo="OutroModelo",
        ano_fabricacao=2020,
        ano_modelo=2020,
        motorizacao="1.0",
        combustivel=CombustivelEnum.ALCOOL,
        cor="Preto",
        quilometragem=50000,
        num_portas=2,
        transmissao=TransmissaoEnum.MANUAL,
        preco=45000.00
    )
    db_session.add(auto)
    db_session.commit()

    retrieved_auto = db_session.query(Automobile).filter(Automobile.marca == "OutraMarca").first()
    assert retrieved_auto is not None
    assert retrieved_auto.combustivel == CombustivelEnum.ALCOOL


def test_automobile_repr(db_session: Session):
    # Dados usados para criar o objeto
    marca_teste = "Volvo"
    modelo_teste = "XC90"
    ano_modelo_teste = 2020

    auto = Automobile(
        marca=marca_teste, 
        modelo=modelo_teste, 
        ano_fabricacao=2021, 
        ano_modelo=ano_modelo_teste,
        motorizacao="1.3", 
        combustivel=CombustivelEnum.ALCOOL,
        cor="Vermelho",
        quilometragem=134210, 
        num_portas=4, 
        transmissao=TransmissaoEnum.AUTOMATICO,
        preco=49945.19
    )
    db_session.add(auto)
    db_session.commit()
    db_session.refresh(auto) 

    expected_repr = f"<Automobile(id={auto.id}, marca='{marca_teste}', modelo='{modelo_teste}', ano='{ano_modelo_teste}')>"
    
    # A asserção
    assert repr(auto) == expected_repr