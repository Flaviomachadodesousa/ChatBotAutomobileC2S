# Automobile Finder Project

Este projeto implementa um sistema de busca de automóveis com uma interface de agente virtual no terminal, comunicação cliente-servidor via um protocolo customizado (MCP) e persistência de dados em um banco de dados.

## Funcionalidades

1.  **Modelagem de Dados**: Esquema de automóveis com atributos como marca, modelo, ano, motorização, etc.
2.  **Banco de Dados Fictício**: Script para popular o banco com dados simulados.
3.  **Comunicação Cliente-Servidor (MCP)**:
    * Cliente envia filtros (JSON).
    * Servidor consulta o banco e retorna resultados (JSON).
4.  **Aplicação no Terminal com Agente Virtual**:
    * Interface conversacional para buscar veículos.
    * O agente coleta informações e interage com o servidor MCP.

## Estrutura do Projeto
├── agent/                  # Lógica do agente virtual

├── core/                   # Modelos, schemas, configuração do Banco de Dados

├── mcp/                    # Cliente e Servidor MCP

├── scripts/                # Script popular Banco de Dados

├── tests/                  # Testes automatizados

├── main.py                 # Inicio

├── requirements.txt        # Dependências

└── README.md

## Pré-requisitos

* Python 3.8+

## Instalação 
1.  Clone o repositório
2.  Crie e ative um ambiente virtual (recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Como executar o projeto
1.  Execute uma vez para criar as tabelas e popular o banco com 100 veículos fictícios:
```bash
python main.py --populate
```
2.  Após popular o banco de dados, execute o Cliente + Servidor
```bash
python main.py --run-agent
```

## Opcional
3.  Caso queira rodar o Servidor MCP sepado do Agente
```bash
python main.py --run-server-only
```
4. Se o servidor já estiver rodando em outro terminal
```bash
python main.py --run-agent --skip-server
```

## Testes automatizados
1.  Para rodar os testes automatizados, use o seguinte comando no terminal:
```bash
python -m pytest -v
```