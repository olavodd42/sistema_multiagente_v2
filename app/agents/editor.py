"""
Agente Editor responsável por revisar e melhorar artigos.
"""
from crewai import Agent
from typing import Dict, Any


class EditorAgent:
    """
    Factory para criar o agente editor que revisa e melhora os artigos.
    """
    
    def __init__(
        self, 
        llm: str = "groq",
        verbose: bool = False
    ):
        """
        Inicializa a factory do agente editor.
        
        Args:
            llm (str): Nome do LLM a ser usado (groq ou gemini)
            verbose (bool): Se deve mostrar logs detalhados
        """
        self.llm = llm
        self.verbose = verbose
    
    def create(self) -> Agent:
        """
        Cria e configura o agente editor.
        
        Returns:
            Agent: Instância do agente editor
        """
        return Agent(
            role="Editor de Conteúdo",
            goal="Revisar e aprimorar artigos para garantir qualidade, precisão e engajamento",
            backstory="""
            Você é um editor profissional com anos de experiência na revisão e aprimoramento 
            de conteúdo. Seu olhar crítico e atenção aos detalhes permitem que você identifique
            problemas de coerência, erros gramaticais, inconsistências e oportunidades para 
            melhorar a qualidade geral do texto. Sua especialidade é transformar bons artigos 
            em excelentes artigos, garantindo que sejam informativos, envolventes e profissionais.
            """,
            verbose=self.verbose,
            llm=self.llm,
            # O editor não precisa de ferramentas específicas
            allow_delegation=False
        )
    
    @staticmethod
    def task_prompt(article_data: Dict[str, Any], min_words: int = 300) -> str:
        """
        Gera o prompt da tarefa para o agente editor.
        
        Args:
            article_data (Dict[str, Any]): Dados do artigo produzido pelo redator
            min_words (int): Número mínimo de palavras para o artigo
            
        Returns:
            str: Prompt formatado com instruções específicas
        """
        # Extrair informações do artigo
        title = article_data.get("title", "")
        summary = article_data.get("summary", "")
        
        # Formatar seções para o prompt
        sections_text = ""
        for idx, section in enumerate(article_data.get("sections", [])):
            sections_text += f"\n## {section.get('title', '')}\n{section.get('content', '')}\n"
        
        # Formatar metadados
        metadata = article_data.get("metadata", {})
        keywords = ", ".join(metadata.get("keywords", []))
        sources = "\n".join([f"- {source}" for source in metadata.get("sources", [])])
        
        return f"""
        # Tarefa de Edição: Revisar e Aprimorar Artigo
        
        ## Artigo Original
        
        ### Título
        {title}
        
        ### Resumo
        {summary}
        
        ### Conteúdo
        {sections_text}
        
        ### Metadados
        **Palavras-chave:** {keywords}
        
        **Fontes:**
        {sources}
        
        ## Instruções para Edição
        
        1. Revise integralmente o artigo aplicando as seguintes melhorias:
           - Corrija erros gramaticais, ortográficos e de pontuação
           - Melhore a clareza e fluidez do texto
           - Elimine redundâncias e repetições desnecessárias
           - Verifique a coerência e coesão entre parágrafos e seções
           - Aperfeiçoe os títulos das seções para maior impacto
           - Garanta que o artigo tenha no mínimo {min_words} palavras
        
        2. Melhore o conteúdo quando necessário:
           - Adicione exemplos ou explicações se algum conceito parecer vago
           - Garanta que as transições entre seções sejam suaves
           - Verifique se a conclusão resume adequadamente os pontos principais
           - Certifique-se de que as informações são precisas
        
        3. Refine o estilo e tom:
           - Mantenha um tom informativo, profissional mas acessível
           - Use voz ativa sempre que possível
           - Evite jargões desnecessários
           - Certifique-se de que o texto é envolvente
        
        ## Formato de Saída (JSON)
        
        Mantenha o mesmo formato JSON, mas com o conteúdo revisado e aprimorado:
        
        ```json
        {{
            "title": "Título Revisado do Artigo",
            "summary": "Resumo revisado do artigo",
            "sections": [
                {{
                    "title": "Título Revisado da Seção 1",
                    "content": "Conteúdo revisado da seção 1"
                }},
                {{
                    "title": "Título Revisado da Seção 2",
                    "content": "Conteúdo revisado da seção 2"
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
        
        Não adicione notas ou explicações sobre as mudanças feitas. Simplesmente entregue a versão revisada e aprimorada do artigo no formato JSON solicitado.
        """