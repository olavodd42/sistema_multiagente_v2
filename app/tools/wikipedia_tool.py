"""
Ferramenta personalizada para consulta à API da Wikipedia usando a biblioteca crewai-tools.
"""
import json
import httpx
from typing import Dict, List, Optional, Any
from crewai_tools import BaseTool


class WikipediaSearchTool(BaseTool):
    """Ferramenta para pesquisar tópicos na Wikipedia."""
    
    name: str = "Pesquisa na Wikipedia"
    description: str = "Busca por tópicos na Wikipedia e retorna os resultados da pesquisa"
    
    def __init__(self, language: str = "pt"):
        """
        Inicializa a ferramenta de pesquisa na Wikipedia.
        
        Args:
            language (str): Código de idioma da Wikipedia (ex: 'pt' para português, 'en' para inglês)
        """
        super().__init__()
        self.language = language
        self.base_url = f"https://{language}.wikipedia.org/w/api.php"
    
    async def _arun(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Executa a pesquisa de forma assíncrona.
        
        Args:
            query (str): Termo de pesquisa
            limit (int): Número máximo de resultados
            
        Returns:
            List[Dict[str, str]]: Lista de resultados da pesquisa
        """
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": limit,
            "utf8": 1
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            data = response.json()
            
            if "error" in data:
                return {"error": data["error"].get("info", "Erro desconhecido")}
            
            results = []
            if "query" in data and "search" in data["query"]:
                for item in data["query"]["search"]:
                    results.append({
                        "title": item["title"],
                        "snippet": item["snippet"].replace('<span class="searchmatch">', '').replace('</span>', ''),
                        "pageid": item["pageid"]
                    })
            
            return results
    
    def _run(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Executa a pesquisa de forma síncrona.
        
        Args:
            query (str): Termo de pesquisa
            limit (int): Número máximo de resultados
            
        Returns:
            List[Dict[str, str]]: Lista de resultados da pesquisa
        """
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": limit,
            "utf8": 1
        }
        
        with httpx.Client() as client:
            response = client.get(self.base_url, params=params)
            data = response.json()
            
            if "error" in data:
                return {"error": data["error"].get("info", "Erro desconhecido")}
            
            results = []
            if "query" in data and "search" in data["query"]:
                for item in data["query"]["search"]:
                    results.append({
                        "title": item["title"],
                        "snippet": item["snippet"].replace('<span class="searchmatch">', '').replace('</span>', ''),
                        "pageid": item["pageid"]
                    })
            
            return results


class WikipediaContentTool(BaseTool):
    """Ferramenta para obter o conteúdo completo de páginas da Wikipedia."""
    
    name: str = "Conteúdo da Wikipedia"
    description: str = "Obtém o conteúdo completo de uma página da Wikipedia pelo título ou ID"
    
    def __init__(self, language: str = "pt"):
        """
        Inicializa a ferramenta de conteúdo da Wikipedia.
        
        Args:
            language (str): Código de idioma da Wikipedia (ex: 'pt' para português, 'en' para inglês)
        """
        super().__init__()
        self.language = language
        self.base_url = f"https://{language}.wikipedia.org/w/api.php"
    
    async def _arun(self, title: Optional[str] = None, pageid: Optional[int] = None, sections: bool = False) -> Dict[str, Any]:
        """
        Executa a busca de conteúdo de forma assíncrona.
        
        Args:
            title (Optional[str]): Título da página da Wikipedia
            pageid (Optional[int]): ID da página da Wikipedia
            sections (bool): Se deve retornar conteúdo dividido por seções
            
        Returns:
            Dict[str, Any]: Conteúdo da página da Wikipedia
        """
        if not title and not pageid:
            return {"error": "É necessário fornecer um título ou ID de página"}
        
        params = {
            "action": "query",
            "prop": "extracts",
            "exlimit": 1,
            "explaintext": 1,
            "format": "json",
            "utf8": 1,
            "redirects": 1
        }
        
        if sections:
            params["exsectionformat"] = "wiki"
        else:
            params["exsectionformat"] = "plain"
        
        if title:
            params["titles"] = title
        elif pageid:
            params["pageids"] = str(pageid)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            data = response.json()
            
            if "error" in data:
                return {"error": data["error"].get("info", "Erro desconhecido")}
            
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return {"error": "Nenhuma página encontrada"}
            
            # A API da Wikipedia retorna um dicionário com IDs de página como chaves
            page_id = next(iter(pages))
            page = pages[page_id]
            
            if "missing" in page:
                return {"error": f"Página '{title}' não encontrada"}
            
            content = page.get("extract", "")
            
            # Se solicitado, tenta dividir o conteúdo em seções
            if sections and content:
                return self._parse_sections(content, page.get("title", ""))
            
            return {
                "title": page.get("title", ""),
                "content": content,
                "pageid": page_id
            }
    
    def _run(self, title: Optional[str] = None, pageid: Optional[int] = None, sections: bool = False) -> Dict[str, Any]:
        """
        Executa a busca de conteúdo de forma síncrona.
        
        Args:
            title (Optional[str]): Título da página da Wikipedia
            pageid (Optional[int]): ID da página da Wikipedia
            sections (bool): Se deve retornar conteúdo dividido por seções
            
        Returns:
            Dict[str, Any]: Conteúdo da página da Wikipedia
        """
        if not title and not pageid:
            return {"error": "É necessário fornecer um título ou ID de página"}
        
        params = {
            "action": "query",
            "prop": "extracts",
            "exlimit": 1,
            "explaintext": 1,
            "format": "json",
            "utf8": 1,
            "redirects": 1
        }
        
        if sections:
            params["exsectionformat"] = "wiki"
        else:
            params["exsectionformat"] = "plain"
        
        if title:
            params["titles"] = title
        elif pageid:
            params["pageids"] = str(pageid)
        
        with httpx.Client() as client:
            response = client.get(self.base_url, params=params)
            data = response.json()
            
            if "error" in data:
                return {"error": data["error"].get("info", "Erro desconhecido")}
            
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return {"error": "Nenhuma página encontrada"}
            
            # A API da Wikipedia retorna um dicionário com IDs de página como chaves
            page_id = next(iter(pages))
            page = pages[page_id]
            
            if "missing" in page:
                return {"error": f"Página '{title}' não encontrada"}
            
            content = page.get("extract", "")
            
            # Se solicitado, tenta dividir o conteúdo em seções
            if sections and content:
                return self._parse_sections(content, page.get("title", ""))
            
            return {
                "title": page.get("title", ""),
                "content": content,
                "pageid": page_id
            }
    
    def _parse_sections(self, content: str, page_title: str) -> Dict[str, Any]:
        """
        Analisa o conteúdo extraído e tenta dividi-lo em seções.
        
        Args:
            content (str): Conteúdo completo da página
            page_title (str): Título da página
            
        Returns:
            Dict[str, Any]: Conteúdo estruturado com seções
        """
        lines = content.split('\n')
        
        # Identificar seções pelo padrão de linhas que começam com == ou ===
        sections = []
        current_section = {"title": "Introdução", "content": ""}
        
        for line in lines:
            if line.startswith('== ') and line.endswith(' =='):
                # Finaliza a seção atual e inicia uma nova
                if current_section["content"].strip():
                    sections.append(current_section)
                
                section_title = line.replace('== ', '').replace(' ==', '')
                current_section = {"title": section_title, "content": ""}
            
            elif line.startswith('=== ') and line.endswith(' ==='):
                # Subsection - podemos tratar como uma seção normal para simplificar
                if current_section["content"].strip():
                    sections.append(current_section)
                
                section_title = line.replace('=== ', '').replace(' ===', '')
                current_section = {"title": section_title, "content": ""}
            
            else:
                # Adiciona a linha ao conteúdo da seção atual
                if current_section["content"]:
                    current_section["content"] += "\n" + line
                else:
                    current_section["content"] = line
        
        # Adiciona a última seção se ela tiver conteúdo
        if current_section["content"].strip():
            sections.append(current_section)
        
        return {
            "title": page_title,
            "sections": sections,
            "pageid": None  # Não temos o ID aqui, mas poderíamos adicionar como parâmetro se necessário
        }


class WikipediaSummaryTool(BaseTool):
    """Ferramenta para obter um resumo de uma página da Wikipedia."""
    
    name: str = "Resumo da Wikipedia"
    description: str = "Obtém um resumo conciso de uma página da Wikipedia pelo título ou ID"
    
    def __init__(self, language: str = "pt"):
        """
        Inicializa a ferramenta de resumo da Wikipedia.
        
        Args:
            language (str): Código de idioma da Wikipedia (ex: 'pt' para português, 'en' para inglês)
        """
        super().__init__()
        self.language = language
        self.base_url = f"https://{language}.wikipedia.org/w/api.php"
    
    async def _arun(self, title: Optional[str] = None, pageid: Optional[int] = None) -> Dict[str, str]:
        """
        Executa a busca de resumo de forma assíncrona.
        
        Args:
            title (Optional[str]): Título da página da Wikipedia
            pageid (Optional[int]): ID da página da Wikipedia
            
        Returns:
            Dict[str, str]: Resumo da página da Wikipedia
        """
        if not title and not pageid:
            return {"error": "É necessário fornecer um título ou ID de página"}
        
        params = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,  # Apenas a introdução
            "explaintext": True,
            "format": "json",
            "utf8": 1,
            "redirects": 1
        }
        
        if title:
            params["titles"] = title
        elif pageid:
            params["pageids"] = str(pageid)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            data = response.json()
            
            if "error" in data:
                return {"error": data["error"].get("info", "Erro desconhecido")}
            
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return {"error": "Nenhuma página encontrada"}
            
            # A API da Wikipedia retorna um dicionário com IDs de página como chaves
            page_id = next(iter(pages))
            page = pages[page_id]
            
            if "missing" in page:
                return {"error": f"Página '{title}' não encontrada"}
            
            return {
                "title": page.get("title", ""),
                "summary": page.get("extract", ""),
                "pageid": page_id
            }
    
    def _run(self, title: Optional[str] = None, pageid: Optional[int] = None) -> Dict[str, str]:
        """
        Executa a busca de resumo de forma síncrona.
        
        Args:
            title (Optional[str]): Título da página da Wikipedia
            pageid (Optional[int]): ID da página da Wikipedia
            
        Returns:
            Dict[str, str]: Resumo da página da Wikipedia
        """
        if not title and not pageid:
            return {"error": "É necessário fornecer um título ou ID de página"}
        
        params = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,  # Apenas a introdução
            "explaintext": True,
            "format": "json",
            "utf8": 1,
            "redirects": 1
        }
        
        if title:
            params["titles"] = title
        elif pageid:
            params["pageids"] = str(pageid)
        
        with httpx.Client() as client:
            response = client.get(self.base_url, params=params)
            data = response.json()
            
            if "error" in data:
                return {"error": data["error"].get("info", "Erro desconhecido")}
            
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return {"error": "Nenhuma página encontrada"}
            
            # A API da Wikipedia retorna um dicionário com IDs de página como chaves
            page_id = next(iter(pages))
            page = pages[page_id]
            
            if "missing" in page:
                return {"error": f"Página '{title}' não encontrada"}
            
            return {
                "title": page.get("title", ""),
                "summary": page.get("extract", ""),
                "pageid": page_id
            }