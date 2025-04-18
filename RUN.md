# Como Executar o Wiki Article Generator

Este documento contém instruções detalhadas para executar o projeto Wiki Article Generator em diferentes ambientes.

## Pré-requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes do Python)
- Chaves de API para o LLM escolhido (Groq ou Gemini)

## Configuração Inicial

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/wiki-article-generator.git
cd wiki-article-generator
```

2. Crie e ative um ambiente virtual:
```bash
# Criação do ambiente virtual
python -m venv venv

# Ativação no Windows
venv\Scripts\activate

# Ativação no Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure suas variáveis de ambiente:
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com seu editor preferido
# nano .env
# ou
# vim .env
# ou abra no seu editor de texto
```

Adicione suas chaves de API no arquivo `.env`:
```
GROQ_API_KEY=sua_chave_groq_aqui
GOOGLE_API_KEY=sua_chave_gemini_aqui
DEFAULT_LLM=groq  # ou gemini
```

## Executando a API

Para iniciar a API, use o comando:

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

Você pode acessar a documentação interativa em `http://localhost:8000/docs`

## Utilizando a API

### Exemplo de como gerar um artigo:

```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"topic": "Inteligência Artificial", "min_words": 500, "language": "pt"}'
```

Resposta:
```json
{
  "task_id": "task_1713617123",
  "status": "processing",
  "message": "Geração do artigo sobre 'Inteligência Artificial' iniciada. Use o task_id para verificar o status."
}
```

### Verificando o status da geração:

```bash
curl "http://localhost:8000/status/task_1713617123"
```

## Usando a Interface de Linha de Comando

O projeto também inclui uma interface de linha de comando para geração de artigos:

```bash
# Sintaxe básica
python -m app.cli "Nome do Tópico"

# Exemplo
python -m app.cli "Inteligência Artificial"

# Com parâmetros adicionais
python -m app.cli "Inteligência Artificial" --min-words 500 --language pt --llm groq --output artigo.json
```

### Parâmetros disponíveis:

- `topic`: Tópico para geração do artigo (obrigatório)
- `--min-words`: Número mínimo de palavras (padrão: 300)
- `--sections`: Número desejado de seções (opcional)
- `--language`: Código do idioma para a Wikipedia (padrão: pt)
- `--llm`: Modelo LLM a ser usado (groq ou gemini)
- `--verbose`: Mostrar logs detalhados
- `--output` ou `-o`: Arquivo para salvar o resultado
- `--hierarchical`: Usar processo hierárquico em vez de sequencial

## Executando com Docker

Se preferir usar Docker:

```bash
# Construir a imagem
docker-compose build

# Iniciar o serviço
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## Executando os Testes

Para executar os testes automatizados:

```bash
pytest

# Para testes com cobertura
pytest --cov=app
```

## Solução de Problemas

### Erro de autenticação com o LLM

Se encontrar erros como "Authentication failed" ou "Invalid API key":

1. Verifique se as chaves de API estão corretas no arquivo `.env`
2. Confirme que o modelo de LLM escolhido está disponível para sua conta

### Problemas com a API da Wikipedia

Se a ferramenta de pesquisa na Wikipedia não estiver funcionando:

1. Verifique sua conexão com a internet
2. Confirme que o idioma selecionado é suportado pela Wikipedia
3. Tente reduzir a complexidade da consulta

### Tempos limite excedidos

Se as requisições estiverem expirando:

1. Aumente o timeout nas configurações de httpx nos arquivos da pasta `tools`
2. Para tarefas mais complexas, considere usar o processo hierárquico com `--hierarchical`