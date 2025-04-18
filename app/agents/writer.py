"""
Agente Redator responsável por transformar informações em artigos.
"""
from crewai import Agent
from typing import Dict, Any, Optional, Union


class WriterAgent:
    """
    Factory para criar o agente redator que transforma informações em artigos.
    """
    
    def __init__(
        self, 
        llm: Any = None,
        verbose: bool = False
    ):
        """
        Inicializa a factory do agente redator.
        
        Args:
            llm: Instância do LLM ou nome do LLM (groq ou gemini)
            verbose (bool): Se deve mostrar logs detalhados
        """
        self.llm = llm
        self.verbose = verbose
    
    def create(self) -> Agent:
        """
        Cria e configura o agente redator.
        
        Returns:
            Agent: Instância do agente redator
        """
        return Agent(
            role="Redator de Artigos",
            goal="Criar artigos informativos, interessantes e bem estruturados",
            backstory="""
            Você é um redator de conteúdo profissional com experiência na criação de artigos 
            informativos e envolventes. Tem habilidade para transformar informações brutas em 
            textos coesos, bem estruturados e adaptados para o público-alvo. Seu trabalho é transformar 
            o material fornecido pelo pesquisador em um artigo interessante, informativo e com boa fluência.
            """,
            verbose=self.verbose,
            llm=self.llm,
            # O redator não precisa de ferramentas específicas
            allow_delegation=False
        )
    
    @staticmethod
    def task_prompt(research_data: Dict[str, Any], min_words: int = 300) -> str:
        """
        Gera o prompt da tarefa para o agente redator.
        
        Args:
            research_data (Dict[str, Any]): Dados de pesquisa coletados pelo pesquisador
            min_words (int): Número mínimo de palavras para o artigo
            
        Returns:
            str: Prompt formatado com instruções específicas
        """
        # Extrair informações dos dados de pesquisa
        topic = research_data.get("topic", "")
        summary = research_data.get("summary", "")
        
        # Formatar seções para o prompt
        sections_text = ""
        for idx, section in enumerate(research_data.get("main_sections", [])):
            sections_text += f"\n**Seção {idx+1}:** {section.get('title', '')}\n{section.get('content', '')}\n"
        
        # Formatar palavras-chave
        keywords = ", ".join(research_data.get("keywords", []))
        
        # Formatar fontes
        sources = "\n".join([f"- {source}" for source in research_data.get("sources", [])])
        
        return f"""
        # Tarefa de Redação: Criar um artigo sobre "{topic}"
        
        ## Dados de Pesquisa
        
        ### Resumo do Tópico
        {summary}
        
        ### Seções com Informações Detalhadas
        {sections_text}
        
        ### Palavras-chave Relacionadas
        {keywords}
        
        ### Fontes Consultadas
        {sources}
        
        ## Instruções para o Artigo
        
        1. Crie um artigo completo sobre "{topic}" com no mínimo {min_words} palavras.
        2. O artigo deve incluir:
           - Um título claro e atrativo
           - Uma introdução que contextualize o tema
           - Pelo menos 3 seções com subtítulos relevantes
           - Uma conclusão que sintetize as principais ideias
        3. Utilize as informações fornecidas, mas não as copie literalmente. Reescreva-as com suas próprias palavras.
        4. Mantenha uma linguagem clara, informativa e acessível.
        5. Inclua todas as informações importantes fornecidas pelo pesquisador.
        6. Evite repetições desnecessárias e mantenha uma boa coesão entre as seções.
        7. Utilize as palavras-chave naturalmente ao longo do texto.
        
        ## Formato de Saída (JSON)
        
        Estruture sua resposta no seguinte formato JSON:
        
        ```json
        {{
            "title": "Título do Artigo",
            "summary": "Resumo do artigo em aproximadamente 150 palavras",
            "sections": [
                {{
                    "title": "Título da Seção 1",
                    "content": "Conteúdo da seção 1"
                }},
                {{
                    "title": "Título da Seção 2",
                    "content": "Conteúdo da seção 2"
                }},
                ...
            ],
            "metadata": {{
                "keywords": ["palavra-chave1", "palavra-chave2", ...],
                "sources": ["Fonte 1", "Fonte 2", ...],
                "generated_at": "Data e hora atual"
            }}
        }}
        ```
        
        Não mencione que este é um artigo gerado por IA ou que está baseado em pesquisas. 
        Escreva como se fosse um artigo original produzido por um especialista humano no assunto.
        """