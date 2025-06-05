import socket
import json

HOST = '127.0.0.1' # HOST LOCAL
PORT = 65432 # PORTA
BUFFER_SIZE = 8192 #BUFFER

class MCPClient:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            return True
        except ConnectionRefusedError:
            print(f"Erro: Não foi possível conectar ao servidor MCP em {self.host}:{self.port}. Verifique se o servidor está rodando.")
            self.sock = None
            return False
        except Exception as e:
            print(f"Erro inesperado ao conectar: {e}")
            self.sock = None
            return False


    def send_request(self, request_type: str, filters: dict = None):
        if not self.sock:
            if not self.connect(): # Tenta reconectar se o socket não existir ou se perdeu
                return {"status": "error", "message": "Falha na conexão com o servidor."}
        
        payload = {"type": request_type}
        if filters is not None:
            payload["filters"] = filters
        
        try:
            self.sock.sendall(json.dumps(payload).encode('utf-8'))
            
            # Receber a resposta em partes se for grande
            full_response_data = b""
            while True:
                chunk = self.sock.recv(BUFFER_SIZE)
                if not chunk:
                    # Conexão fechada pelo servidor antes de terminar a resposta
                    # ou se o servidor fechar a conexão abruptamente.
                    if not full_response_data: # Nenhuma parte da resposta foi recebida
                         return {"status": "error", "message": "Nenhuma resposta recebida do servidor, conexão pode ter sido fechada."}
                    break # Sai do loop se algo já foi recebido.
                full_response_data += chunk
                try:
                    # Tenta decodificar.
                    # Se for um JSON válido, assumimos que a mensagem terminou.
                    return json.loads(full_response_data.decode('utf-8'))
                except json.JSONDecodeError:
                    # Se não for um JSON válido ainda, continue recebendo mais dados.
                    if len(full_response_data) > BUFFER_SIZE * 10: # Evitar loop infinito para respostas muito grandes/corrompidas
                        return {"status": "error", "message": "Resposta do servidor muito grande ou mal formatada."}
                    pass # Continua no loop para receber mais partes da mensagem
            # Tentar decodificar última vez.
            try:
                return json.loads(full_response_data.decode('utf-8'))
            except json.JSONDecodeError:
                 return {"status": "error", "message": "Resposta final do servidor mal formatada."}

        except (ConnectionResetError, BrokenPipeError) as e:
            print(f"Conexão com o servidor perdida: {e}")
            self.sock = None # Força reconexão na próxima chamada
            return {"status": "error", "message": f"Conexão com o servidor perdida: {e}"}
        except Exception as e:
            print(f"Erro durante a comunicação com o servidor: {e}")
            return {"status": "error", "message": f"Erro de comunicação: {str(e)}"}

    def query_vehicles(self, filters: dict):
        return self.send_request(request_type="query", filters=filters)

    def ping_server(self):
        return self.send_request(request_type="ping")

    def close(self):
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR) # Informa o outro lado que não haverá mais envio/recebimento
            except OSError:
                pass # Socket pode já estar fechado
            self.sock.close()
            self.sock = None
            print("Conexão MCP fechada.")
