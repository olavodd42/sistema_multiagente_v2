"""
Modelos Pydantic para estruturar os dados do artigo.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ArticleSection(BaseModel):
    """Seção de um artigo com título e conteúdo."""
    title: str = Field(..., description="Título da seção")
    content: str = Field(..., description="Conteúdo da seção")

    @validator('content')
    def content_min_length(cls, v):
        """Valida se o conteúdo tem pelo menos 50 caracteres."""
        if len(v) < 50:
            raise ValueError('O conteúdo da seção deve ter pelo menos 50 caracteres')
        return v


class ArticleMetadata(BaseModel):
    """Metadados do artigo."""
    keywords: List[str] = Field(..., description="Palavras-chave relacionadas ao artigo")
    sources: List[str] = Field(..., description="Fontes de informação utilizadas")
    generated_at: datetime = Field(default_factory=datetime.now, description="Data de geração do artigo")


class Article(BaseModel):
    """Modelo completo do artigo."""
    title: str = Field(..., description="Título principal do artigo")
    summary: str = Field(..., description="Resumo do artigo")
    sections: List[ArticleSection] = Field(..., description="Seções do artigo")
    metadata: ArticleMetadata = Field(..., description="Metadados do artigo")
    
    @property
    def word_count(self) -> int:
        """Calcula o número de palavras no artigo completo."""
        text = self.summary + " " + " ".join(section.content for section in self.sections)
        return len(text.split())
    
    @validator('sections')
    def minimum_sections(cls, v):
        """Valida se o artigo tem pelo menos 2 seções."""
        if len(v) < 2:
            raise ValueError('O artigo deve ter pelo menos 2 seções')
        return v
    
    @validator('summary')
    def summary_min_length(cls, v):
        """Valida se o resumo tem pelo menos 100 caracteres."""
        if len(v) < 100:
            raise ValueError('O resumo deve ter pelo menos 100 caracteres')
        return v
    
    def validate_min_words(self, min_words: int = 300) -> bool:
        """Valida se o artigo tem o número mínimo de palavras requerido."""
        return self.word_count >= min_words


class ArticleRequest(BaseModel):
    """Modelo para solicitação de geração de artigo."""
    topic: str = Field(..., description="Tópico principal do artigo")
    min_words: int = Field(default=300, description="Número mínimo de palavras do artigo")
    sections_count: Optional[int] = Field(default=3, description="Número desejado de seções")
    language: str = Field(default="pt", description="Idioma do artigo (código ISO)")


class ArticleResponse(BaseModel):
    """Modelo para resposta de geração de artigo."""
    article: Article = Field(..., description="Artigo gerado")
    processing_time: float = Field(..., description="Tempo de processamento em segundos")
    status: str = Field(default="success", description="Status da geração")