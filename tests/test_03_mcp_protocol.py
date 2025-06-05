from mcp.client import MCPClient

def test_mcp_ping(mcp_client_instance: MCPClient, mcp_test_server): # Garante que o servidor está no ar
    assert mcp_client_instance.connect(), "Cliente não conseguiu conectar ao servidor de teste"
    response = mcp_client_instance.ping_server()
    assert response is not None, "Nenhuma resposta do ping"
    assert response.get("status") == "success"
    assert response.get("message") == "pong"

def test_mcp_invalid_filter_value_type(mcp_client_instance: MCPClient, mcp_test_server):
    assert mcp_client_instance.connect()
    response = mcp_client_instance.query_vehicles(filters={"preco_min": "muito_caro_carro"})
    assert response is not None
    assert response.get("status") == "error"
    assert "Filtros inválidos" in response.get("message", "")