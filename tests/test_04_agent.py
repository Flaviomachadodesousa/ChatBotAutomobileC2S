from unittest.mock import patch, MagicMock
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agent.virtual_agent import VirtualAgent
from core.models import CombustivelEnum

def test_agent_parse_simple_marca_modelo():
    agent = VirtualAgent()
    text = "Quero um Ford Fiesta"
    filters = agent._parse_user_input(text)
    assert filters.get("marca") == "Ford"
    assert filters.get("modelo") == "Fiesta"

def test_agent_parse_ano():
    agent = VirtualAgent()
    text = "carro do ano 2020"
    filters = agent._parse_user_input(text)
    assert filters.get("ano_modelo_min") == 2020
    assert filters.get("ano_modelo_max") == 2020


def test_agent_parse_combustivel():
    agent = VirtualAgent()
    text = "combustível gasolina"
    filters = agent._parse_user_input(text)
    assert filters.get("combustivel") == CombustivelEnum.GASOLINA.value 

@patch('builtins.input')
@patch('agent.virtual_agent.MCPClient')
def test_agent_interaction_flow_basic_search(MockMCPClient, mock_input):
    # Configurar o mock do cliente MCP
    mock_mcp_instance = MockMCPClient.return_value
    mock_mcp_instance.connect.return_value = True
    mock_mcp_instance.query_vehicles.return_value = {
        "status": "success",
        "data": [
            {"marca": "Ford", "modelo": "Ka", "ano_modelo": 2019, "cor": "Vermelho", "quilometragem": 12345, "preco": 45000.00, "combustivel": "Gasolina", "transmissao": "Manual", "num_portas": 4}
        ]
    }

    # Simular entradas do usuário
    # 1. Saudação implícita
    # 2. Entrada do usuário com filtros
    # 3. Confirmação para buscar
    # 4. Sair
    mock_input.side_effect = [
        "Ford Ka 2019",   # Filtros iniciais
        "buscar",         # Confirma a busca
        "sair"            # Encerra o loop
    ]

    agent = VirtualAgent()
    
    # Capturar prints para verificar a saída
    with patch('builtins.print') as mock_print:
        agent.run_interaction_loop()

    # Verificar se o cliente MCP foi chamado com os filtros corretos
    # {'marca': 'Ford', 'modelo': 'Ka', 'ano_modelo_min': 2019, 'ano_modelo_max': 2019}
    expected_filters = {'marca': 'Ford', 'modelo': 'Ka', 'ano_modelo_min': 2019, 'ano_modelo_max': 2019}
    mock_mcp_instance.query_vehicles.assert_called_once_with(expected_filters)

    # Verificar se os resultados foram impressos
    found_result_print = False
    for call_args in mock_print.call_args_list:
        if "Encontrei 1 veículo(s) para você:" in str(call_args[0][0]):
            found_result_print = True
            break
    assert found_result_print, "Mensagem de resultado da busca não encontrada no print."