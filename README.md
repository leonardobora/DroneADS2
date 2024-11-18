# Projeto Drone Unibrasil

## Visão Geral

O Projeto Drone Unibrasil é uma aplicação que otimiza rotas para um drone autônomo encarregado de mapear Curitiba. O objetivo principal é fotografar uma lista de códigos postais enquanto minimiza o tempo de voo e as paradas para recarga, reduzindo assim os custos operacionais.

## Funcionalidades

- Cálculo de distâncias usando a fórmula de Haversine.
- Ajuste da velocidade do drone com base nas condições do vento.
- Consumo de bateria do drone durante os voos.
- Mapeamento de CEPs para coordenadas geográficas.
- Geração de um arquivo CSV detalhando o caminho de voo do drone.
- Implementação de um algoritmo genético para otimização das rotas.

## Requisitos

- Python 3.6 ou superior
- Bibliotecas necessárias (veja `requirements.txt`)

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/USERNAME/REPOSITORY.git
   cd REPOSITORY
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Para Linux/Mac
   venv\Scripts\activate  # Para Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Para executar o projeto, utilize o seguinte comando:

python main.py

python -m unittest discover -s tests

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir um issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para mais detalhes.