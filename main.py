import threading
import time
import argparse
import os
import sys
from core.database import create_db_and_tables, get_db_session 
from scripts.populate_db import populate_db
from mcp.server import start_server
from agent.virtual_agent import VirtualAgent
from mcp.client import MCPClient

# Garante que o diretório raiz do projeto esteja no sys.path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# Variável global para sinalizar que o servidor está pronto
server_ready = threading.Event()

def run_server_thread(test_mode=False):
    print("Iniciando thread do servidor MCP...")
    try:
        start_server(test_mode=test_mode)
    except Exception as e:
        print(f"Erro ao iniciar o servidor na thread: {e}")

def check_server_readiness(client: MCPClient, retries=5, delay=2):
    for i in range(retries):
        print(f"Tentativa {i+1}/{retries} de conectar ao servidor...")
        if client.connect():
            ping_response = client.ping_server()
            if ping_response and ping_response.get("status") == "success":
                print("Servidor MCP está pronto e respondendo a pings.")
                client.close()
                return True
            client.close() # Fechar se o ping falhou mas conectou
        time.sleep(delay)
    print("Servidor MCP não ficou pronto a tempo.")
    return False

def main():
    parser = argparse.ArgumentParser(description="Automobile Finder Test C2S")
    parser.add_argument(
        "--populate", action="store_true", help="Popula o banco de dados."
    )
    parser.add_argument(
        "--skip-server", action="store_true", help="Não inicia o servidor MCP (útil se já estiver rodando)."
    )
    parser.add_argument(
        "--run-agent", action="store_true", help="Roda o agente virtual no terminal."
    )
    parser.add_argument(
        "--run-server-only", action="store_true", help="Roda apenas o servidor MCP."
    )
    parser.add_argument(
        "--test-mode-db", action="store_true", help="Usa banco de dados de teste em memória para o servidor."
    )

    args = parser.parse_args()

    # 1. Criar tabelas
    print("Inicializando banco de dados e tabelas...")
    # Determina se o DB de teste deve ser usado para criar as tabelas
    create_tables_on_test_db = args.test_mode_db and (args.run_server_only or (not args.skip_server and args.run_agent))
    create_db_and_tables(use_test_engine=create_tables_on_test_db)

    # 2. Popular o banco de dados se solicitado
    if args.populate:
        print("Populando o banco de dados principal (arquivo)...")
        try:
            with get_db_session(use_test_engine=False) as db: # 'db' aqui é a sessão do SQLAlchemy
                populate_db(db, num_automobiles=100)
        except Exception as e:
            print(f"Erro durante a população do banco de dados: {e}")
        print("População do banco de dados concluída.")
        if not args.run_agent and not args.run_server_only:
            return 

    server_thread = None
    if args.run_server_only:
        print("Iniciando apenas o servidor MCP...")
        start_server(test_mode=args.test_mode_db)
        return

    if not args.skip_server and args.run_agent:
        print("Iniciando servidor MCP em uma thread separada...")
        server_thread = threading.Thread(target=run_server_thread, args=(args.test_mode_db,), daemon=True)
        server_thread.start()
        
        print("Aguardando o servidor MCP ficar pronto...")
        time.sleep(2) 
        temp_client = MCPClient()
        if not check_server_readiness(temp_client):
            print("AVISO: Não foi possível confirmar que o servidor está rodando. O agente pode não funcionar.")

    if args.run_agent:
        if args.skip_server:
            print("Agente iniciado sem iniciar um novo servidor (esperando um existente).")
        
        print("\nIniciando o Agente Virtual...")
        agent = VirtualAgent() # Cria a instância do agente
        try:
            agent.run_interaction_loop()
        except KeyboardInterrupt:
            print("\nAgente encerrado pelo usuário.")
        except Exception as e:
            print(f"\nOcorreu um erro no agente: {e}")
        finally:
            # Garante que o cliente MCP do agente seja fechado se existir
            if hasattr(agent, 'client') and agent.client:
                 agent.client.close()
            print("Agente finalizado.")
    
    if server_thread and server_thread.is_alive() and not args.run_server_only:
        print("Servidor MCP está rodando em segundo plano (thread daemon). Ele será encerrado com o programa principal.")

    if not args.run_agent and not args.populate and not args.run_server_only and not args.skip_server:
         parser.print_help()

if __name__ == "__main__":
    main()