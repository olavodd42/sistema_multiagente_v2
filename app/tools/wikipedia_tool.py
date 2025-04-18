import json
import httpx
from typing import Dict, List, Optional, Any, Annotated
from pydantic import Field
from crewai.tools import BaseTool


class WikipediaSearchTool(BaseTool):
    name: str = "Pesquisa na Wikipedia"
    description: str = "Busca por tópicos na Wikipedia e retorna os resultados da pesquisa"
    language: Annotated[str, Field(description="Idioma da Wikipedia")] = "pt"

    def _run(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        base_url = f"https://{self.language}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": limit,
            "utf8": 1
        }
        with httpx.Client() as client:
            response = client.get(base_url, params=params)
            data = response.json()

            if "error" in data:
                return [{"error": data["error"].get("info", "Erro desconhecido")}]  # corrigido

            results = []
            for item in data.get("query", {}).get("search", []):
                results.append({
                    "title": item["title"],
                    "snippet": item["snippet"].replace('<span class="searchmatch">', '').replace('</span>', ''),
                    "pageid": item["pageid"]
                })
            return results


class WikipediaContentTool(BaseTool):
    name: str = "Conteúdo da Wikipedia"
    description: str = "Obtém o conteúdo completo de uma página da Wikipedia pelo título ou ID"
    language: Annotated[str, Field(description="Idioma da Wikipedia")] = "pt"

    def _run(self, title: Optional[str] = None, pageid: Optional[int] = None, sections: bool = False) -> Dict[str, Any]:
        if not title and not pageid:
            return {"error": "É necessário fornecer um título ou ID de página"}

        base_url = f"https://{self.language}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "extracts",
            "exlimit": 1,
            "explaintext": 1,
            "format": "json",
            "utf8": 1,
            "redirects": 1,
            "exsectionformat": "wiki" if sections else "plain"
        }
        if title:
            params["titles"] = title
        else:
            params["pageids"] = str(pageid)

        with httpx.Client() as client:
            response = client.get(base_url, params=params)
            data = response.json()

            if "error" in data:
                return {"error": data["error"].get("info", "Erro desconhecido")}

            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return {"error": "Nenhuma página encontrada"}

            page = next(iter(pages.values()))
            if "missing" in page:
                return {"error": f"Página '{title}' não encontrada"}

            content = page.get("extract", "")
            return self._parse_sections(content, page.get("title", "")) if sections else {
                "title": page.get("title", ""),
                "content": content,
                "pageid": page.get("pageid")
            }

    def _parse_sections(self, content: str, page_title: str) -> Dict[str, Any]:
        lines = content.split('\n')
        sections = []
        current_section = {"title": "Introdução", "content": ""}

        for line in lines:
            if line.startswith("== ") and line.endswith(" =="):
                if current_section["content"].strip():
                    sections.append(current_section)
                current_section = {"title": line.strip("= "), "content": ""}
            else:
                current_section["content"] += f"\n{line}" if current_section["content"] else line

        if current_section["content"].strip():
            sections.append(current_section)

        return {"title": page_title, "sections": sections, "pageid": None}


class WikipediaSummaryTool(BaseTool):
    name: str = "Resumo da Wikipedia"
    description: str = "Obtém um resumo conciso de uma página da Wikipedia pelo título ou ID"
    language: Annotated[str, Field(description="Idioma da Wikipedia")] = "pt"

    def _run(self, title: Optional[str] = None, pageid: Optional[int] = None) -> Dict[str, str]:
        if not title and not pageid:
            return {"error": "É necessário fornecer um título ou ID de página"}

        base_url = f"https://{self.language}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "format": "json",
            "utf8": 1,
            "redirects": 1
        }
        params["titles" if title else "pageids"] = title or str(pageid)

        with httpx.Client() as client:
            response = client.get(base_url, params=params)
            data = response.json()

            if "error" in data:
                return {"error": data["error"].get("info", "Erro desconhecido")}

            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return {"error": "Nenhuma página encontrada"}

            page = next(iter(pages.values()))
            if "missing" in page:
                return {"error": f"Página '{title}' não encontrada"}

            return {
                "title": page.get("title", ""),
                "summary": page.get("extract", ""),
                "pageid": page.get("pageid")
            }
