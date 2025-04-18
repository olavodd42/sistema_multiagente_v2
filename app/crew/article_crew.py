import json
import time
import os
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from crewai import Crew, Task, Agent
from pydantic import ValidationError
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI as ChatGemini

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

        llm_instance = self._configure_llm(llm)

        self.researcher = ResearcherAgent(
            llm=llm_instance, language=language, verbose=verbose
        ).create()
        self.writer = WriterAgent(
            llm=llm_instance, verbose=verbose
        ).create()
        self.editor = EditorAgent(
            llm=llm_instance, verbose=verbose
        ).create()

    def _configure_llm(self, llm_name: str):
        import litellm
        from langchain_community.chat_models import ChatLiteLLM

        if llm_name.lower() == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY não encontrada nas variáveis de ambiente")
            return ChatLiteLLM(
                model="groq/qwen-qwq-32b",
                litellm_params={"api_key": api_key},
                temperature=0.7
            )

        elif llm_name.lower() == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY não encontrada nas variáveis de ambiente")
            return ChatLiteLLM(
                model="gemini-pro",
                litellm_params={"api_key": api_key},
                temperature=0.7
            )

        else:
            raise ValueError(f"LLM não suportado: {llm_name}. Use 'groq' ou 'gemini'")

    def _create_tasks(self, topic: str, min_words: int = 300) -> List[Task]:
        research_prompts_list = ResearcherAgent.task_prompt(topic)
        research_prompt = "\n".join(research_prompts_list) if isinstance(research_prompts_list, list) else research_prompts_list

        research_task = Task(
            description=f"Pesquisar informações sobre '{topic}' na Wikipedia",
            agent=self.researcher,
            expected_output="Dados estruturados contendo resumo, seções principais, palavras-chave e fontes",
            context=[{
                "description": f"Pesquisar informações sobre '{topic}' na Wikipedia",
                "expected_output": "Dados estruturados contendo resumo, seções principais, palavras-chave e fontes",
                "instructions": research_prompt
            }]
        )

        writer_prompt = WriterAgent.task_prompt({"topic": topic}, min_words)
        writing_task = Task(
            description=f"Escrever um artigo com pelo menos {min_words} palavras",
            agent=self.writer,
            expected_output="Artigo completo no formato JSON com título, resumo, seções e metadados",
            context=[{
                "description": f"Escrever um artigo com pelo menos {min_words} palavras",
                "expected_output": "Artigo completo no formato JSON com título, resumo, seções e metadados",
                "instructions": writer_prompt
            }]
        )

        editor_prompt = EditorAgent.task_prompt({"topic": topic}, min_words)
        editing_task = Task(
            description=f"Revisar e aprimorar o artigo, garantindo qualidade e mínimo de {min_words} palavras",
            agent=self.editor,
            expected_output="Artigo revisado e aprimorado no formato JSON",
            context=[{
                "description": f"Revisar e aprimorar o artigo, garantindo qualidade e mínimo de {min_words} palavras",
                "expected_output": "Artigo revisado e aprimorado no formato JSON",
                "instructions": editor_prompt
            }]
        )

        return [research_task, writing_task, editing_task]

    def run(
        self,
        topic: str,
        min_words: int = 300,
        sections_count: Optional[int] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        tasks = self._create_tasks(topic, min_words)

        crew = Crew(
            agents=[self.researcher, self.writer, self.editor],
            tasks=tasks,
            verbose=self.verbose,
            process=self.process
        )

        crew_result = crew.kickoff()
        processing_time = time.time() - start_time
        
        # Handle CrewOutput object
        if hasattr(crew_result, 'output'):
            result = crew_result.output
        elif hasattr(crew_result, 'result'):
            result = crew_result.result
        elif hasattr(crew_result, 'last_output'):
            result = crew_result.last_output()
        else:
            result = str(crew_result)  # Fallback to string representation

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

        # Logar resultado bruto
        print("[DEBUG] Resultado bruto:", result)

        def try_load(s: str) -> Any:
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return None

        # Tentativas diretas
        parsed = try_load(result)
        if isinstance(parsed, dict):
            return parsed

        if isinstance(parsed, str):
            nested = try_load(parsed)
            if isinstance(nested, dict):
                return nested

        # Regex para blocos markdown ```json ... ```
        import re
        match = re.search(r'```json(.*?)```', result, re.DOTALL)
        if match:
            content = match.group(1).strip()
            parsed = try_load(content)
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, str):
                nested = try_load(parsed)
                if isinstance(nested, dict):
                    return nested

        # Regex para qualquer JSON {...}
        match = re.search(r'(\{.*\})', result, re.DOTALL)
        if match:
            content = match.group(1).strip()
            parsed = try_load(content)
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, str):
                nested = try_load(parsed)
                if isinstance(nested, dict):
                    return nested

        # Última tentativa: remover qualquer prefixo/sufixo textual e tentar parsear
        result_clean = result.strip().split("\n")
        for line in result_clean:
            possible = try_load(line.strip())
            if isinstance(possible, dict):
                return possible

        raise ValueError("Não foi possível extrair JSON do resultado: veja log de debug")

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