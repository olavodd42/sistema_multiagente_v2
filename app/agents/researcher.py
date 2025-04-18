"""
Agente Pesquisador responsável por coletar informações da Wikipedia.
"""
from crewai import Agent
from typing import Optional, List, Dict, Any, Union

from app.tools.wikipedia_tool import WikipediaSearchTool, WikipediaContentTool, WikipediaSummaryTool


class ResearcherAgent:
    """
    Factory para criar o agente pesquisador que coleta informações da Wikipedia.
    """
    
    def __init__(
        self, 
        llm: Any = None,
        language: str = "pt",
        verbose: bool = False
    ):
        """
        Inicializa a factory do agente pesquisador.
        
        Args:
            llm: Instância do LLM ou nome do LLM (groq ou gemini)
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
    def task_prompt(topic: str) -> List[str]:
        return [
            f"# Pesquisa sobre \"{topic}\"",
            f"""## Instruções

                1. Pesquise informações abrangentes sobre o tópico "{topic}".
                2. Primeiro, realize uma busca ampla para identificar os resultados mais relevantes.
                3. Obtenha o resumo dos 2-3 resultados mais relevantes.
                4. Para pelo menos 2 dos resultados mais relevantes, colete o conteúdo completo, dividido por seções.
                5. Organize as informações coletadas de forma estruturada.
                6. Extraia palavras-chave e fontes.
                """,
                f"""## Formato de saída

                ```json
            {{
            "topic": "{topic}",
            "summary": "...",
            "main_sections": [{{"title": "...", "content": "..."}}],
            "keywords": ["..."],
            "sources": ["..."]
            }}
            ```"""
        ]