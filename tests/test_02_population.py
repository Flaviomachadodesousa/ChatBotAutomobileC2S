from sqlalchemy.orm import Session
from core.models import Automobile

def test_db_population(populated_db: Session):
    count = populated_db.query(Automobile).count()
    assert count >= 20 # Verifica se pelo menos 20 carros foram adicionados pela fixture
    some_car = populated_db.query(Automobile).first()
    assert some_car is not None
    assert some_car.marca is not None
    assert some_car.modelo is not None
    assert some_car.ano_fabricacao > 1900
    assert some_car.preco > 0
    assert some_car.combustivel is not None
    assert some_car.transmissao is not None