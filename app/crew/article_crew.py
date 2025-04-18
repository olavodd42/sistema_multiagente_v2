import json
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from crewai import Crew, Task, Agent
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
        process: str = "sequential"
    ):
        self.llm = llm
        self.language = language
        self.verbose = verbose
        self.process = process

        self.researcher = ResearcherAgent(
            llm=llm, language=language, verbose=verbose
        ).create()
        self.writer = WriterAgent(
            llm=llm, verbose=verbose
        ).create()
        self.editor = EditorAgent(
            llm=llm, verbose=verbose
        ).create()

    def _create_tasks(self, topic: str, min_words: int = 300) -> List[Task]:
        """
        Cria todas as tarefas necessárias para o fluxo de trabalho.
        
        Args:
            topic: O tópico do artigo
            min_words: Número mínimo de palavras
            
        Returns:
            Uma lista de tarefas configuradas
        """
        # Cria a tarefa de pesquisa
        research_task = Task(
            description=f"Pesquisar informações sobre '{topic}' na Wikipedia",
            agent=self.researcher,
            expected_output="Dados estruturados contendo resumo, seções principais, palavras-chave e fontes"
        )
        
        # Cria a tarefa de escrita
        writing_task = Task(
            description=f"Escrever um artigo com pelo menos {min_words} palavras usando as informações pesquisadas",
            agent=self.writer,
            expected_output="Artigo completo no formato JSON com título, resumo, seções e metadados"
        )
        
        # Cria a tarefa de edição
        editing_task = Task(
            description=f"Revisar e aprimorar o artigo, garantindo qualidade e mínimo de {min_words} palavras",
            agent=self.editor,
            expected_output="Artigo revisado e aprimorado no formato JSON"
        )
        
        return [research_task, writing_task, editing_task]

    def run(
        self,
        topic: str,
        min_words: int = 300,
        sections_count: Optional[int] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        # Obter todas as tarefas em uma única chamada
        tasks = self._create_tasks(topic, min_words)
        
        crew = Crew(
            agents=[self.researcher, self.writer, self.editor],
            tasks=tasks,
            verbose=self.verbose,
            process=self.process
        )

        result = crew.kickoff()
        processing_time = time.time() - start_time

        try:
            article_data = self._parse_json_result(result)
            try:
                article = self._convert_to_pydantic_model(article_data)
                article_output = article.model_dump()
            except ValidationError:
                article_output = article_data

            return {
                "article": article_output,
                "processing_time": round(processing_time, 2),
                "status": "success"
            }
        except Exception as e:
            return {
                "error": str(e),
                "processing_time": round(processing_time, 2),
                "status": "error"
            }

    def _parse_json_result(self, result: Any) -> Dict[str, Any]:
        if isinstance(result, dict):
            return result
        if not isinstance(result, str):
            raise ValueError(f"Tipo inesperado de resultado: {type(result)}")

        def try_load(s: str) -> Any:
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return None

        parsed = try_load(result)
        if isinstance(parsed, dict):
            return parsed
        if isinstance(parsed, str):
            nested = try_load(parsed)
            if isinstance(nested, dict):
                return nested

        import re
        match = re.search(r'```json(.*?)```', result, re.DOTALL)
        if match:
            content = match.group(1)
            parsed = try_load(content)
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, str):
                nested = try_load(parsed)
                if isinstance(nested, dict):
                    return nested

        match = re.search(r'(\{.*\})', result, re.DOTALL)
        if match:
            content = match.group(1)
            parsed = try_load(content)
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, str):
                nested = try_load(parsed)
                if isinstance(nested, dict):
                    return nested

        raise ValueError("Não foi possível extrair JSON do resultado")

    def _convert_to_pydantic_model(
        self,
        article_data: Dict[str, Any]
    ) -> Article:
        title = article_data.get("title", "")
        summary = article_data.get("summary", "")
        sections: List[ArticleSection] = []
        for sec in article_data.get("sections", []):
            sections.append(
                ArticleSection(
                    title=sec.get("title", ""),
                    content=sec.get("content", "")
                )
            )

        metadata_dict = article_data.get("metadata", {})
        metadata = ArticleMetadata(
            keywords=metadata_dict.get("keywords", []),
            sources=metadata_dict.get("sources", []),
            generated_at=datetime.now()
        )

        return Article(
            title=title,
            summary=summary,
            sections=sections,
            metadata=metadata
        )