"""
API principal para geração de artigos com CrewAI.
"""
import os
import time
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from crewai import Process

from app.crew.article_crew import ArticleCrew
from app.models.article import ArticleRequest, ArticleResponse, Article


# Carrega variáveis de ambiente
load_dotenv()

# Configura o modelo LLM
DEFAULT_LLM = os.getenv("DEFAULT_LLM", "groq")

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="Wiki Article Generator API",
    description="API para geração de artigos baseados em tópicos da Wikipedia usando CrewAI",
    version="1.0.0"
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento temporário de tarefas em andamento
tasks_status = {}


@app.get("/")
def read_root():
    """
    Rota raiz da API.
    """
    return {
        "message": "Wiki Article Generator API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.post("/generate", response_model=dict)
async def generate_article(request: ArticleRequest, background_tasks: BackgroundTasks):
    """
    Gera um artigo com base no tópico fornecido.
    
    Args:
        request (ArticleRequest): Parâmetros para geração do artigo
        background_tasks (BackgroundTasks): Gerenciador de tarefas em segundo plano
        
    Returns:
        dict: ID da tarefa para acompanhamento
    """
    # Gera um ID de tarefa único
    task_id = f"task_{int(time.time())}"
    
    # Inicializa o status da tarefa
    tasks_status[task_id] = {
        "status": "processing",
        "topic": request.topic,
        "created_at": time.time(),
        "result": None
    }
    
    # Adiciona a tarefa de geração do artigo para execução em segundo plano
    background_tasks.add_task(
        run_article_generation,
        task_id,
        request.topic,
        request.min_words,
        request.sections_count,
        request.language
    )
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": f"Geração do artigo sobre '{request.topic}' iniciada. Use o task_id para verificar o status."
    }


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Verifica o status de uma tarefa de geração de artigo.
    
    Args:
        task_id (str): ID da tarefa
        
    Returns:
        dict: Status atual da tarefa
    """
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    task_data = tasks_status[task_id]
    
    if task_data["status"] == "completed":
        return {
            "task_id": task_id,
            "status": "completed",
            "topic": task_data["topic"],
            "created_at": task_data["created_at"],
            "completed_at": task_data.get("completed_at"),
            "processing_time": task_data.get("processing_time"),
            "article": task_data["result"].get("article") if task_data["result"] else None
        }
    elif task_data["status"] == "error":
        return {
            "task_id": task_id,
            "status": "error",
            "topic": task_data["topic"],
            "error": task_data.get("error"),
            "created_at": task_data["created_at"],
            "completed_at": task_data.get("completed_at"),
            "processing_time": task_data.get("processing_time")
        }
    else:
        # Status em processamento
        return {
            "task_id": task_id,
            "status": "processing",
            "topic": task_data["topic"],
            "created_at": task_data["created_at"],
            "message": "Artigo em geração"
        }


def run_article_generation(
    task_id: str,
    topic: str,
    min_words: int = 300,
    sections_count: Optional[int] = None,
    language: str = "pt"
):
    """
    Executa a geração do artigo em segundo plano.
    
    Args:
        task_id (str): ID da tarefa
        topic (str): Tópico do artigo
        min_words (int): Número mínimo de palavras
        sections_count (Optional[int]): Número desejado de seções
        language (str): Idioma do artigo
    """
    try:
        # Cria e executa a Crew
        crew = ArticleCrew(
            llm=DEFAULT_LLM,
            language=language,
            verbose=True,
            process=Process.sequential
        )
        
        # Executa a geração do artigo
        result = crew.run(topic, min_words, sections_count)
        
        # Atualiza o status da tarefa
        tasks_status[task_id]["status"] = "completed"
        tasks_status[task_id]["result"] = result
        tasks_status[task_id]["completed_at"] = time.time()
        tasks_status[task_id]["processing_time"] = result.get("processing_time")
        
    except Exception as e:
        # Em caso de erro, atualiza o status
        tasks_status[task_id]["status"] = "error"
        tasks_status[task_id]["error"] = str(e)
        tasks_status[task_id]["completed_at"] = time.time()
        tasks_status[task_id]["processing_time"] = time.time() - tasks_status[task_id]["created_at"]


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run("app.main:app", host=host, port=port, reload=True)