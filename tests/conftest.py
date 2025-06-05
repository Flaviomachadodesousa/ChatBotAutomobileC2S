import pytest
from sqlalchemy.orm import sessionmaker, Session 
import threading
import time
import os
import sys
from core.database import test_engine as THE_GLOBAL_TEST_ENGINE
from core.models import Automobile, CombustivelEnum, TransmissaoEnum
from mcp.server import start_server, HOST as MCP_HOST, PORT as MCP_PORT
from mcp.client import MCPClient
from scripts.populate_db import populate_db as actual_populate_db

@pytest.fixture(scope="session", autouse=True)
def prepare_global_test_database_once():
    from core.database import Base, test_engine as THE_GLOBAL_TEST_ENGINE
    from sqlalchemy import inspect

    print("[CONTEST_DEBUG] Antes de drop_all/create_all. Tabelas existentes:", inspect(THE_GLOBAL_TEST_ENGINE).get_table_names())
    Base.metadata.drop_all(bind=THE_GLOBAL_TEST_ENGINE)
    Base.metadata.create_all(bind=THE_GLOBAL_TEST_ENGINE)
    print("[CONTEST_DEBUG] Depois de create_all. Tabelas existentes:", inspect(THE_GLOBAL_TEST_ENGINE).get_table_names())

@pytest.fixture(scope="session")
def mcp_test_data():
    """Popula o THE_GLOBAL_TEST_ENGINE com dados para os testes MCP."""
    SessionForTestMCP = sessionmaker(autocommit=False, autoflush=False, bind=THE_GLOBAL_TEST_ENGINE)
    db = SessionForTestMCP()
    try:
        # Limpa dados específicos da tabela Automobile antes de adicionar novos
        db.query(Automobile).delete()
        db.commit()

        cars_to_add_for_mcp = [
            Automobile(marca="TestMarcaA", modelo="TestModeloX", ano_fabricacao=2020, ano_modelo=2020, motorizacao="1.0", combustivel=CombustivelEnum.GASOLINA, cor="Azul", quilometragem=10000, num_portas=4, transmissao=TransmissaoEnum.MANUAL, preco=50000.00, tipo_veiculo="Hatch"),
            Automobile(marca="TestMarcaB", modelo="TestModeloY", ano_fabricacao=2021, ano_modelo=2021, motorizacao="2.0", combustivel=CombustivelEnum.DIESEL, cor="Preto", quilometragem=20000, num_portas=4, transmissao=TransmissaoEnum.AUTOMATICO, preco=120000.00, tipo_veiculo="SUV"),
            Automobile(marca="TestMarcaA", modelo="TestModeloZ", ano_fabricacao=2020, ano_modelo=2021, motorizacao="1.6", combustivel=CombustivelEnum.GASOLINA, cor="Branco", quilometragem=5000, num_portas=2, transmissao=TransmissaoEnum.MANUAL, preco=60000.00, tipo_veiculo="Hatch")
        ]
        db.add_all(cars_to_add_for_mcp)
        db.commit()
    except Exception as e:
        db.rollback()
        pytest.fail(f"Falha ao popular dados para mcp_test_data: {e}")
    finally:
        db.close()

@pytest.fixture(scope="session")
def mcp_test_server():
    """Inicia o servidor MCP para testes. Ele usará o THE_GLOBAL_TEST_ENGINE."""
    server_thread = threading.Thread(target=start_server, args=(MCP_HOST, MCP_PORT, True), daemon=True)
    server_thread.start()

    client = MCPClient(MCP_HOST, MCP_PORT)
    ready = False
    for _ in range(15): # Aumentado o timeout um pouco
        time.sleep(0.2) # Intervalo menor
        if client.connect():
            ping_res = client.ping_server()
            if ping_res and ping_res.get("status") == "success":
                ready = True; client.close(); break
            client.close()

    if not ready:
        pytest.fail("Servidor MCP de teste não iniciou ou não está respondendo a pings após várias tentativas.")
    yield
    print("Parando servidor MCP de teste (thread daemon finaliza com pytest).")

@pytest.fixture(scope="function")
def db_session():
    """Fornece uma sessão de DB para testes unitários, usando transações aninhadas para isolamento."""
    SessionForTests = sessionmaker(autocommit=False, autoflush=False, bind=THE_GLOBAL_TEST_ENGINE)
    session = SessionForTests()
    nested_transaction = session.begin_nested()
    try:
        yield session
    finally:
        if nested_transaction.is_active:
             nested_transaction.rollback()
        session.close()

@pytest.fixture(scope="function")
def mcp_client_instance():
    client = MCPClient(MCP_HOST, MCP_PORT)
    yield client
    client.close()

@pytest.fixture(scope="function")
def populated_db(db_session: Session):
    actual_populate_db(db_session, num_automobiles=20) # Popula 20 carros
    return db_session