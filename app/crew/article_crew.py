"""
Definição da Crew responsável pela geração de artigos.
"""
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

from crewai import Crew, Task, Process
from pydantic import ValidationError

from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent 
from app.agents.editor import EditorAgent
from app.models.article import Article, ArticleSection, ArticleMetadata


class ArticleCrew:
    """
    Crew responsável pela geração de artigos com base em tópicos da Wikipedia.
    """
    
    def __init__(
        self, 
        llm: str = "groq",
        language: str = "pt",
        verbose: bool = False,
        process: Process = Process.sequential
    ):
        """
        Inicializa a Crew de geração de artigos.
        
        Args:
            llm (str): Nome do LLM a ser usado (groq ou gemini)
            language (str): Código do idioma para pesquisa na Wikipedia
            verbose (bool): Se deve mostrar logs detalhados
            process (Process): Processo de execução das tarefas (sequential ou hierarchical)
        """
        self.llm = llm
        self.language = language
        self.verbose = verbose
        self.process = process
        
        # Inicializa os agentes
        self.researcher = ResearcherAgent(llm=llm, language=language, verbose=verbose).create()
        self.writer = WriterAgent(llm=llm, verbose=verbose).create()
        self.editor = EditorAgent(llm=llm, verbose=verbose).create()
    
    def _create_research_task(self, topic: str) -> Task:
        """
        Cria a tarefa de pesquisa.
        
        Args:
            topic (str): Tópico a ser pesquisado
            
        Returns:
            Task: Tarefa configurada
        """
        return Task(
            description=f"Pesquisar informações sobre '{topic}' na Wikipedia",
            agent=self.researcher,
            expected_output="Dados estruturados contendo resumo, seções principais, palavras-chave e fontes",
            context=ResearcherAgent.task_prompt(topic)
        )
    
    def _create_writing_task(self, min_words: int = 300) -> Task:
        """
        Cria a tarefa de redação.
        
        Args:
            min_words (int): Número mínimo de palavras para o artigo
            
        Returns:
            Task: Tarefa configurada
        """
        return Task(
            description=f"Escrever um artigo com pelo menos {min_words} palavras usando as informações pesquisadas",
            agent=self.writer,
            expected_output="Artigo completo no formato JSON com título, resumo, seções e metadados",
            context=None  # Será definido após a tarefa de pesquisa
        )
    
    def _create_editing_task(self, min_words: int = 300) -> Task:
        """
        Cria a tarefa de edição.
        
        Args:
            min_words (int): Número mínimo de palavras para o artigo
            
        Returns:
            Task: Tarefa configurada
        """
        return Task(
            description=f"Revisar e aprimorar o artigo, garantindo qualidade e mínimo de {min_words} palavras",
            agent=self.editor,
            expected_output="Artigo revisado e aprimorado no formato JSON",
            context=None  # Será definido após a tarefa de redação
        )
    
    def run(self, topic: str, min_words: int = 300, sections_count: Optional[int] = None) -> Dict[str, Any]:
        """
        Executa a Crew para gerar um artigo completo.
        
        Args:
            topic (str): Tópico do artigo
            min_words (int): Número mínimo de palavras para o artigo
            sections_count (Optional[int]): Número desejado de seções
            
        Returns:
            Dict[str, Any]: Resultado contendo o artigo gerado e metadados
        """
        start_time = time.time()
        
        # Cria as tarefas
        research_task = self._create_research_task(topic)
        writing_task = self._create_writing_task(min_words)
        editing_task = self._create_editing_task(min_words)
        
        # Configura a Crew
        crew = Crew(
            agents=[self.researcher, self.writer, self.editor],
            tasks=[research_task, writing_task, editing_task],
            verbose=self.verbose,
            process=self.process
        )
        
        # Executa as tarefas sequencialmente
        result = crew.kickoff()
        processing_time = time.time() - start_time
        
        # Processa o resultado da última tarefa (editor)
        try:
            article_data = self._parse_json_result(result)
            article = self._convert_to_pydantic_model(article_data)
            
            return {
                "article": article.dict(),
                "processing_time": round(processing_time, 2),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "processing_time": round(processing_time, 2),
                "status": "error"
            }
    
    def _parse_json_result(self, result: str) -> Dict[str, Any]:
        """
        Extrai e analisa o JSON do resultado da Crew.
        
        Args:
            result (str): Resultado bruto da execução
            
        Returns:
            Dict[str, Any]: Dados estruturados do artigo
        """
        # Tenta encontrar JSON no resultado
        try:
            # Primeiro, tenta analisar o resultado completo como JSON
            return json.loads(result)
        except json.JSONDecodeError:
            # Se falhar, tenta extrair JSON delimitado por ```json e ```
            import re
            json_pattern = r'```json(.*?)```'
            match = re.search(json_pattern, result, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
            else:
                # Se ainda falhar, tenta encontrar chaves JSON no texto
                json_pattern = r'\{.*\}'
                match = re.search(json_pattern, result, re.DOTALL)
                
                if match:
                    json_str = match.group(0)
                    return json.loads(json_str)
                
                raise ValueError("Não foi possível extrair JSON do resultado")
    
    def _convert_to_pydantic_model(self, article_data: Dict[str, Any]) -> Article:
        """
        Converte o dicionário do artigo para o modelo Pydantic.
        
        Args:
            article_data (Dict[str, Any]): Dados do artigo em formato de dicionário
            
        Returns:
            Article: Instância do modelo Pydantic
        """
        # Extrai os dados necessários
        title = article_data.get("title", "")
        summary = article_data.get("summary", "")
        
        # Converte seções
        sections = []
        for section_data in article_data.get("sections", []):
            section = ArticleSection(
                title=section_data.get("title", ""),
                content=section_data.get("content", "")
            )
            sections.append(section)
        
        # Processa metadados
        metadata_data = article_data.get("metadata", {})
        metadata = ArticleMetadata(
            keywords=metadata_data.get("keywords", []),
            sources=metadata_data.get("sources", []),
            generated_at=datetime.now()
        )
        
        # Cria e retorna o artigo
        return Article(
            title=title,
            summary=summary,
            sections=sections,
            metadata=metadata
        )