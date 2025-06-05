from faker import Faker
from sqlalchemy.orm import Session
from core.models import Automobile, CombustivelEnum, TransmissaoEnum
from core.schemas import AutomobileCreate
import random
from datetime import date
import sys
import os

fake = Faker('pt_BR')

MARCAS_MODELOS = {
    "Fiat": ["Uno", "Palio", "Strada", "Toro", "Argo", "Mobi", "Cronos", "Pulse", "Fastback"],
    "Volkswagen": ["Gol", "Polo", "Virtus", "T-Cross", "Nivus", "Saveiro", "Amarok", "Taos", "Jetta", "Voyage"],
    "Chevrolet": ["Onix", "Prisma", "Tracker", "S10", "Cruze", "Montana", "Spin", "Equinox", "Joy"],
    "Ford": ["Ka", "Fiesta", "EcoSport", "Ranger", "Territory", "Bronco", "Maverick"],
    "Hyundai": ["HB20", "Creta", "Tucson", "Santa Fe", "HB20S", "IX35"],
    "Toyota": ["Corolla", "Hilux", "Yaris", "SW4", "Corolla Cross", "RAV4", "Etios"],
    "Renault": ["Sandero", "Logan", "Duster", "Kwid", "Captur", "Oroch"],
    "Honda": ["Civic", "Fit", "City", "HR-V", "WR-V", "CR-V"],
    "Jeep": ["Renegade", "Compass", "Commander", "Wrangler", "Gladiator"],
    "Nissan": ["Kicks", "Versa", "Frontier", "Sentra", "March"],
    "Peugeot": ["208", "2008", "3008", "Partner", "Boxer"],
    "Citroën": ["C3", "C4 Cactus", "Jumpy", "Jumper"],
    "Mitsubishi": ["L200 Triton", "Pajero Sport", "Eclipse Cross", "Outlander", "ASX"],
    "BMW": ["Série 3", "X1", "X3", "Série 1", "320i", "X5", "118i", "X6"],
    "Mercedes-Benz": ["Classe C", "Classe A", "GLA", "GLC", "Sprinter", "C180", "A200"],
    "Audi": ["A3", "A4", "A5", "Q3", "Q5", "Q7", "Q8", "E-tron", "A1", "TT"],
    "Kia": ["Sportage", "Cerato", "Sorento", "Niro", "Stonic", "Picanto", "Rio"],
    "Land Rover": ["Range Rover Evoque", "Discovery", "Defender", "Range Rover Velar", "Range Rover Sport"],
    "Volvo": ["XC40", "XC60", "XC90", "S60", "V60"],
    "RAM": ["1500", "2500", "3500", "Rampage"],
}

CORES = ["Branco", "Preto", "Prata", "Cinza", "Vermelho", "Azul", "Verde", "Marrom", "Amarelo", "Laranja", "Vinho", "Bege", "Dourado", "Grafite"]
MOTORIZACOES = ["1.0", "1.3", "1.4", "1.5", "1.6", "1.8", "2.0", "1.0 Turbo", "1.4 Turbo", "2.0 Turbo", "2.8 Diesel", "3.2 Diesel"]
TIPOS_VEICULO = ["Passeio", "Hatch", "Sedan", "SUV", "Picape", "Van", "Esportivo"]
OPCIONAIS_LIST = ["Ar condicionado", "Direção hidráulica", "Vidros elétricos", "Travas elétricas", "Alarme", "Som MP3", "Rodas de liga leve", "Teto solar", "Bancos de couro", "Sensor de estacionamento", "Câmera de ré", "Airbag duplo", "Freios ABS", "Farol de neblina", "Controle de estabilidade"]


def create_random_automobile() -> AutomobileCreate:
    marca = random.choice(list(MARCAS_MODELOS.keys()))
    modelo = random.choice(MARCAS_MODELOS[marca])
    ano_atual = date.today().year
    # Garante que ano_fabricacao seja no máximo o ano anterior ao atual
    ano_fabricacao = random.randint(ano_atual - 15, ano_atual - 1 if ano_atual > 1900 else ano_atual)
    # Garante que ano_modelo seja igual ou um ano após ano_fabricacao, mas não no futuro distante
    ano_modelo = random.choice([ano_fabricacao, ano_fabricacao + 1])
    ano_modelo = min(ano_modelo, ano_atual + 1) # Limita o ano do modelo ao próximo ano
    preco_base_ano = 20000 + (ano_fabricacao - (ano_atual - 15)) * 3000
    preco = random.uniform(preco_base_ano * 0.7, preco_base_ano * 1.6)
    if "Picape" in modelo or "SUV" in modelo or marca in ["Volvo", "Toyota", "Audi"]:
        preco *= 1.7
    if marca in ["Ford", "Fiat", "Chevrolet", "Volkswagen"] and ano_fabricacao < ano_atual - 8:
        preco *= 0.8

    return AutomobileCreate(
        marca=marca,
        modelo=modelo,
        ano_fabricacao=ano_fabricacao,
        ano_modelo=ano_modelo,
        motorizacao=random.choice(MOTORIZACOES),
        combustivel=random.choice(list(CombustivelEnum)),
        cor=random.choice(CORES),
        quilometragem=random.randint(0, 200000) if ano_fabricacao < ano_atual else random.randint(0,1000),
        num_portas=random.choice([2, 4]),
        transmissao=random.choice(list(TransmissaoEnum)),
        preco=round(preco, 2),
        tipo_veiculo=random.choice(TIPOS_VEICULO),
        opcionais=",".join(random.sample(OPCIONAIS_LIST, k=random.randint(2, 6)))
    )

def populate_db(db: Session, num_automobiles: int = 100):
    current_count = db.query(Automobile).count()
    
    cars_to_add = num_automobiles - current_count
    if cars_to_add <= 0:
        print(f"Banco de dados já possui {current_count} veículos (ou mais). Nada a fazer para atingir {num_automobiles} veículos.")
        return

    print(f"Populando o banco com {cars_to_add} novos veículos para atingir um total de {num_automobiles}...")
    for _ in range(cars_to_add):
        auto_data_pydantic = create_random_automobile()
        db_auto = Automobile(**auto_data_pydantic.model_dump())
        db.add(db_auto)
    db.commit()
    print(f"{cars_to_add} veículos adicionados com sucesso.")

if __name__ == "__main__":
    project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root_dir not in sys.path:
        sys.path.insert(0, project_root_dir)

    from core.database import create_db_and_tables, get_db_session
    
    print("Criando tabelas (se não existirem)...")
    create_db_and_tables(use_test_engine=False) # Garante que opera no DB principal
    
    # Usando o gerenciador de contexto para a sessão
    try:
        with get_db_session(use_test_engine=False) as db:
            populate_db(db, num_automobiles=100)
    except Exception as e:
        print(f"Ocorreu um erro ao popular o banco de dados: {e}")
    finally:
        print("Script de população finalizado.")

