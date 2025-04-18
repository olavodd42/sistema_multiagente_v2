# Wiki Article Generator

Sistema multiagentes para geração automática de artigos a partir de tópicos da Wikipedia utilizando CrewAI.

## 📋 Sobre o Projeto

Este projeto implementa um sistema de geração automática de artigos baseados em pesquisas na Wikipedia. Utilizando a arquitetura de multiagentes do CrewAI, o sistema divide o processo de criação de conteúdo em três etapas fundamentais:

1. **Pesquisa** - Coleta informações detalhadas sobre o tópico na Wikipedia
2. **Redação** - Transforma as informações coletadas em um artigo estruturado
3. **Edição** - Revisa e aprimora o conteúdo para garantir qualidade

## 🤖 Agentes

O sistema utiliza três agentes especializados:

- **Pesquisador**: Coleta informações da Wikipedia sobre o tópico solicitado
- **Redator**: Transforma as informações em um artigo bem estruturado
- **Editor**: Revisa e aprimora o artigo, corrigindo erros e melhorando a qualidade

## 🛠️ Tecnologias Utilizadas

- **Python 3.9+**
- **CrewAI**: Framework para criação e gerenciamento de agentes
- **CrewAI-tools**: Ferramentas personalizadas para interação com APIs
- **FastAPI**: Framework web para criação da API
- **Pydantic**: Validação e serialização de dados
- **Groq/Gemini**: Modelos de linguagem para os agentes

## 📦 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/wiki-article-generator.git
cd wiki-article-generator
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
# No Windows
venv\Scripts\activate
# No Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o arquivo `.env` com suas chaves de API:
```bash
cp .env.example .env
# Edite o arquivo .env com seus dados
```

## 🚀 Uso

### Executando a API

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

### Endpoints Principais

- **GET /** - Informações básicas da API
- **POST /generate** - Gera um novo artigo
- **GET /status/{task_id}** - Verifica o status da geração

### Exemplo de Requisição

```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"topic": "Inteligência Artificial", "min_words": 500, "language": "pt"}'
```

## 📊 Estrutura do Projeto

```
wiki-article-generator/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── researcher.py
│   │   ├── writer.py
│   │   └── editor.py
│   ├── crew/
│   │   ├── __init__.py
│   │   └── article_crew.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── article.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── wikipedia_tool.py
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_article_crew.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## 🧪 Testes

Para executar os testes:

```bash
pytest
```

## 🙏 Agradecimentos

- [CrewAI](https://github.com/joaomdmoura/crewAI)
- [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page)