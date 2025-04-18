"""
Agente Pesquisador responsável por coletar informações da Wikipedia.
"""
from crewai import Agent
from typing import Optional, List, Dict, Any

from app.tools.wikipedia_tool import WikipediaSearchTool, WikipediaContentTool, WikipediaSummaryTool


class ResearcherAgent:
    """
    Factory para criar o agente pesquisador que coleta informações da Wikipedia.
    """
    
    def __init__(
        self, 
        llm: str = "groq",
        language: str = "pt",
        verbose: bool = False
    ):
        """
        Inicializa a factory do agente pesquisador.
        
        Args:
            llm (str): Nome do LLM a ser usado (groq ou gemini)
            language (str): Código do idioma para pesquisa na Wikipedia
            verbose (bool): Se deve mostrar logs detalhados
        """
        self.llm = llm
        self.language = language
        self.verbose = verbose
        
        # Inicializa as ferramentas
        self.search_tool = WikipediaSearchTool(language=language)
        self.content_tool = WikipediaContentTool(language=language)
        self.summary_tool = WikipediaSummaryTool(language=language)
    
    def create(self) -> Agent:
        """
        Cria e configura o agente pesquisador.
        
        Returns:
            Agent: Instância do agente pesquisador
        """
        return Agent(
            role="Pesquisador de Informações",
            goal="Coletar informações abrangentes e precisas sobre o tópico solicitado",
            backstory="""
            Você é um pesquisador especializado em coleta de informações da Wikipedia.
            Com anos de experiência em pesquisa, você tem habilidade para encontrar 
            informações relevantes, confiáveis e detalhadas sobre qualquer tópico.
            Seu trabalho é coletar dados de alta qualidade para que o redator possa
            criar artigos informativos e precisos.
            """,
            tools=[
                self.search_tool,
                self.content_tool,
                self.summary_tool
            ],
            verbose=self.verbose,
            llm=self.llm,
            # Instruções específicas sobre como o agente deve executar sua função
            allow_delegation=False
        )
    
    @staticmethod
    def task_prompt(topic: str) -> str:
        """
        Gera o prompt da tarefa para o agente pesquisador.
        
        Args:
            topic (str): Tópico a ser pesquisado
            
        Returns:
            str: Prompt formatado com instruções específicas
        """
        return f"""
        # Pesquisa sobre "{topic}"
        
        ## Instruções
        
        1. Pesquise informações abrangentes sobre o tópico "{topic}".
        2. Primeiro, realize uma busca ampla para identificar os resultados mais relevantes.
        3. Obtenha o resumo dos 2-3 resultados mais relevantes.
        4. Para pelo menos 2 dos resultados mais relevantes, colete o conteúdo completo, dividido por seções.
        5. Organize as informações coletadas de forma estruturada, identificando:
           - Definições e conceitos principais
           - Informações históricas relevantes
           - Fatos e dados atuais
           - Diferentes perspectivas ou abordagens, se aplicável
        6. Identifique e extraia pelo menos 5-10 palavras-chave relacionadas ao tópico.
        7. Cite todas as fontes utilizadas.
        
        ## Formato de saída (JSON)
        
        Estruture sua resposta no seguinte formato JSON:
        
        ```json
        {{
            "topic": "{topic}",
            "summary": "Um resumo abrangente baseado em todas as fontes",
            "main_sections": [
                {{
                    "title": "Título da Seção 1",
                    "content": "Conteúdo detalhado da seção 1"
                }},
                {{
                    "title": "Título da Seção 2",
                    "content": "Conteúdo detalhado da seção 2"
                }}
            ],
            "keywords": ["palavra-chave1", "palavra-chave2", ...],
            "sources": ["Título da fonte 1", "Título da fonte 2", ...]
        }}
        ```
        
        Concentre-se em obter informações precisas, detalhadas e bem estruturadas.
        O redator utilizará estas informações para criar um artigo informativo sobre "{topic}".
        """


class ResearchResult:
    """
    Estrutura para organizar os resultados da pesquisa.
    """
    
    def __init__(
        self,
        topic: str,
        summary: str,
        main_sections: List[Dict[str, str]],
        keywords: List[str],
        sources: List[str]
    ):
        """
        Inicializa um resultado de pesquisa.
        
        Args:
            topic (str): Tópico pesquisado
            summary (str): Resumo das informações coletadas
            main_sections (List[Dict[str, str]]): Seções principais com título e conteúdo
            keywords (List[str]): Palavras-chave relacionadas
            sources (List[str]): Fontes consultadas
        """
        self.topic = topic
        self.summary = summary
        self.main_sections = main_sections
        self.keywords = keywords
        self.sources = sources
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o resultado da pesquisa para dicionário.
        
        Returns:
            Dict[str, Any]: Representação em dicionário do resultado
        """
        return {
            "topic": self.topic,
            "summary": self.summary,
            "main_sections": self.main_sections,
            "keywords": self.keywords,
            "sources": self.sources
        }