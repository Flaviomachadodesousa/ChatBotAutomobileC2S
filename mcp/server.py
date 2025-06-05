import socket
import json
import threading
from sqlalchemy.orm import Session
from core.database import get_db_session
from core.models import Automobile 
from core.schemas import AutomobileFilter, AutomobileDisplay
from pydantic import ValidationError

HOST = '127.0.0.1' # HOST
PORT = 65432 # PORTA
BUFFER_SIZE = 8192 # Aumentar se necessário para respostas grandes

def handle_query(db: Session, filters_dict: dict):
    try:
        filters = AutomobileFilter(**filters_dict)
    except ValidationError as e:
        return {"status": "error", "message": f"Filtros inválidos: {e.errors()}"}

    query = db.query(Automobile)

    if filters.marca:
        query = query.filter(Automobile.marca.ilike(f"%{filters.marca}%"))
    if filters.modelo:
        query = query.filter(Automobile.modelo.ilike(f"%{filters.modelo}%"))
    if filters.ano_fabricacao_min:
        query = query.filter(Automobile.ano_fabricacao >= filters.ano_fabricacao_min)
    if filters.ano_fabricacao_max:
        query = query.filter(Automobile.ano_fabricacao <= filters.ano_fabricacao_max)
    if filters.ano_modelo_min:
        query = query.filter(Automobile.ano_modelo >= filters.ano_modelo_min)
    if filters.ano_modelo_max:
        query = query.filter(Automobile.ano_modelo <= filters.ano_modelo_max)
    if filters.combustivel:
        query = query.filter(Automobile.combustivel == filters.combustivel)
    if filters.cor:
        query = query.filter(Automobile.cor.ilike(f"%{filters.cor}%"))
    if filters.quilometragem_max:
        query = query.filter(Automobile.quilometragem <= filters.quilometragem_max)
    if filters.num_portas:
        query = query.filter(Automobile.num_portas == filters.num_portas)
    if filters.transmissao:
        query = query.filter(Automobile.transmissao == filters.transmissao)
    if filters.preco_min:
        query = query.filter(Automobile.preco >= filters.preco_min)
    if filters.preco_max:
        query = query.filter(Automobile.preco <= filters.preco_max)
    if filters.tipo_veiculo:
        query = query.filter(Automobile.tipo_veiculo.ilike(f"%{filters.tipo_veiculo}%"))
    
    results = query.limit(100).all() # Limitar resultados para não sobrecarregar.
    
    data_to_send = [AutomobileDisplay.model_validate(auto).model_dump(mode='json') for auto in results]
    
    return {"status": "success", "data": data_to_send}

def client_handler(conn: socket.socket, addr, db_context_manager_factory):
    try: # Bloco try para o socket
        with db_context_manager_factory() as db:
            while True:
                raw_data = conn.recv(BUFFER_SIZE)
                if not raw_data:
                    break
                try:
                    message_str = raw_data.decode('utf-8')
                    message = json.loads(message_str)
                except json.JSONDecodeError:
                    response = {"status": "error", "message": "JSON inválido"}
                except UnicodeDecodeError:
                    response = {"status": "error", "message": "Decodificação UTF-8 falhou"}
                else:
                    if message.get("type") == "query" and "filters" in message:
                        response = handle_query(db, message["filters"]) # 'db' é a sessão
                    elif message.get("type") == "ping":
                        response = {"status": "success", "message": "pong"}
                    else:
                        response = {"status": "error", "message": "Tipo de requisição inválida ou filtros ausentes"}

                conn.sendall(json.dumps(response).encode('utf-8'))
    except ConnectionResetError:
        print(f"Conexão com {addr} reiniciada.")
    except Exception as e:
        print(f"Erro ao lidar com o cliente {addr}: {e}")
        # ... (lógica de enviar erro ao cliente) ...
    finally:
        print(f"Desconectando {addr}")
        conn.close() # Fecha a conexão do socket

def start_server(host=HOST, port=PORT, test_mode=False):
    db_session_factory = lambda: get_db_session(use_test_engine=test_mode)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite reusar o endereço
        s.bind((host, port))
        s.listen()
        print(f"Servidor MCP escutando em {host}:{port}")
        print(f"Usando banco de dados {'de teste (em memória)' if test_mode else 'principal (arquivo)'}")

        try:
            while True:
                conn, addr = s.accept()
                thread = threading.Thread(target=client_handler, args=(conn, addr, db_session_factory))
                thread.daemon = True # Permite que o programa principal saia mesmo com threads ativas
                thread.start()
        except KeyboardInterrupt:
            print("\nServidor MCP encerrando...")
        finally:
            s.close()

if __name__ == '__main__':
    # Para executar o servidor standalone
    import sys
    import os
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from core.database import create_db_and_tables # type: ignore
    # Garante que as tabelas existam no DB principal ao rodar o servidor
    create_db_and_tables() 
    start_server()