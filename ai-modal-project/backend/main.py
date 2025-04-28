from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import os
import json
import shutil
import uuid
import asyncio
from pathlib import Path
import base64
import httpx
import openai
import anthropic
from dotenv import load_dotenv

# Importer le module de génération de vidéos
from video_generator import generate_video, VideoGenerationError

# Charger les variables d'environnement depuis .env
load_dotenv()

# Vérifier les clés API
openai_api_key = os.getenv("OPENAI_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
default_provider = os.getenv("DEFAULT_AI_PROVIDER", "openai")

# Vérifier les configurations
if not openai_api_key and default_provider == "openai":
    print("ATTENTION: La clé API OpenAI n'est pas configurée. Utilisez un fichier .env avec OPENAI_API_KEY=votre_clé_api")

if not anthropic_api_key and default_provider == "anthropic":
    print("ATTENTION: La clé API Anthropic n'est pas configurée. Utilisez un fichier .env avec ANTHROPIC_API_KEY=votre_clé_api")

if not deepseek_api_key and default_provider == "deepseek":
    print("ATTENTION: La clé API DeepSeek n'est pas configurée. Utilisez un fichier .env avec DEEPSEEK_API_KEY=votre_clé_api")

# Configuration OpenAI
openai.api_key = openai_api_key

# Configuration Anthropic
anthropic_client = None
if anthropic_api_key:
    anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)

# Création du dossier uploads s'il n'existe pas
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="IA Modal API")

# Mount static files directory for uploaded videos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configuration CORS pour permettre au frontend de communiquer avec le backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les origines exactes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèle de données pour les requêtes
class AIRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 150
    model: Optional[str] = "gpt-3.5-turbo"  # Modèle par défaut pour OpenAI
    provider: Optional[str] = None  # Fournisseur d'IA: "openai", "anthropic", "deepseek"

# Modèle de données pour les réponses
class AIResponse(BaseModel):
    result: str
    provider: str

# Modèle pour les informations de vidéo
class VideoInfo(BaseModel):
    filename: str
    file_id: str
    file_path: str
    size_bytes: int
    content_type: str
    thumbnail: Optional[str] = None

# Modèle pour l'analyse de vidéo
class VideoAnalysisRequest(BaseModel):
    video_id: str
    prompt: str
    provider: Optional[str] = None

# Modèle pour la génération de vidéo
class VideoGenerationRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)

# Modèle pour le statut de génération de vidéo
class VideoGenerationStatus(BaseModel):
    task_id: str
    status: str
    progress: Optional[float] = None
    video_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/")
async def read_root():
    return {"message": "Bienvenue sur l'API IA Modal. Utilisez /api/process pour traiter les requêtes."}

async def process_with_openai(prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 150) -> str:
    """Traite une demande via l'API OpenAI."""
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="Clé API OpenAI non configurée")
        
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "Vous êtes un assistant IA utile."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur API OpenAI: {str(e)}")

async def process_with_anthropic(prompt: str, max_tokens: int = 150) -> str:
    """Traite une demande via l'API Anthropic (Claude)."""
    if not anthropic_client:
        raise HTTPException(status_code=500, detail="Clé API Anthropic non configurée")
    
    try:
        message = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return message.content[0].text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur API Anthropic: {str(e)}")

async def process_with_deepseek(prompt: str, max_tokens: int = 150) -> str:
    """Traite une demande via l'API DeepSeek."""
    if not deepseek_api_key:
        raise HTTPException(status_code=500, detail="Clé API DeepSeek non configurée")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {deepseek_api_key}"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "Vous êtes un assistant IA utile."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens
                },
                timeout=30.0
            )
            data = response.json()
            if response.status_code != 200:
                raise Exception(f"Erreur {response.status_code}: {data.get('error', {}).get('message', 'Erreur inconnue')}")
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur API DeepSeek: {str(e)}")

@app.post("/api/process", response_model=AIResponse)
async def process_ai(request: AIRequest):
    # Déterminer le fournisseur à utiliser
    provider = request.provider or default_provider
    
    try:
        if provider == "openai":
            result = await process_with_openai(request.prompt, request.model, request.max_tokens)
        elif provider == "anthropic":
            result = await process_with_anthropic(request.prompt, request.max_tokens)
        elif provider == "deepseek":
            result = await process_with_deepseek(request.prompt, request.max_tokens)
        else:
            raise HTTPException(status_code=400, detail=f"Fournisseur d'IA non supporté: {provider}")
        
        return AIResponse(result=result, provider=provider)
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur API: {str(e)}")

@app.post("/api/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """Endpoint pour uploader une vidéo."""
    # Vérifier le type de fichier
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une vidéo")
    
    # Générer un identifiant unique pour le fichier
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    new_filename = f"{file_id}{file_extension}"
    file_path = UPLOAD_DIR / new_filename
    
    # Sauvegarder le fichier
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Créer une miniature (à implémenter avec ffmpeg ou une bibliothèque similaire)
    # Pour cet exemple, nous n'implémentons pas la création de miniature
    
    # Retourner les informations sur la vidéo
    video_info = VideoInfo(
        filename=file.filename,
        file_id=file_id,
        file_path=str(file_path),
        size_bytes=os.path.getsize(file_path),
        content_type=file.content_type
    )
    
    return video_info

@app.get("/api/videos/{video_id}")
async def get_video(video_id: str):
    """Récupère les informations d'une vidéo par son ID."""
    # Rechercher le fichier vidéo
    for file_path in UPLOAD_DIR.glob(f"{video_id}*"):
        if file_path.is_file():
            # Déterminer le type de contenu
            content_type = "video/mp4"  # Par défaut
            if file_path.suffix == ".webm":
                content_type = "video/webm"
            elif file_path.suffix == ".ogg":
                content_type = "video/ogg"
            
            return FileResponse(
                path=str(file_path),
                media_type=content_type,
                filename=file_path.name
            )
    
    raise HTTPException(status_code=404, detail="Vidéo non trouvée")

@app.post("/api/analyze-video", response_model=AIResponse)
async def analyze_video(request: VideoAnalysisRequest):
    """Analyse une vidéo avec l'IA."""
    # Vérifier si la vidéo existe
    video_found = False
    for file_path in UPLOAD_DIR.glob(f"{request.video_id}*"):
        if file_path.is_file():
            video_found = True
            break
    
    if not video_found:
        raise HTTPException(status_code=404, detail="Vidéo non trouvée")
    
    # Formuler la requête pour l'IA
    analysis_prompt = f"Analyse la vidéo avec l'ID {request.video_id}. {request.prompt}"
    
    # Déterminer le fournisseur à utiliser
    provider = request.provider or default_provider
    
    try:
        if provider == "openai":
            result = await process_with_openai(analysis_prompt)
        elif provider == "anthropic":
            result = await process_with_anthropic(analysis_prompt)
        elif provider == "deepseek":
            result = await process_with_deepseek(analysis_prompt)
        else:
            raise HTTPException(status_code=400, detail=f"Fournisseur d'IA non supporté: {provider}")
        
        return AIResponse(result=result, provider=provider)
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur API: {str(e)}")

# Stocker les tâches de génération de vidéo en cours
video_generation_tasks = {}

async def generate_video_task(task_id: str, request: VideoGenerationRequest):
    """Tâche en arrière-plan pour générer une vidéo."""
    try:
        # Mise à jour du statut : en cours
        video_generation_tasks[task_id] = {
            "status": "running",
            "progress": 0.1,
            "video_info": None,
            "error": None
        }
        
        # Générer la vidéo
        video_info = await generate_video(
            prompt=request.prompt,
            provider=request.provider,
            settings=request.settings
        )
        
        # Mise à jour du statut : terminé
        video_generation_tasks[task_id] = {
            "status": "completed",
            "progress": 1.0,
            "video_info": video_info,
            "error": None
        }
    except Exception as e:
        # En cas d'erreur
        video_generation_tasks[task_id] = {
            "status": "failed",
            "progress": None,
            "video_info": None,
            "error": str(e)
        }

@app.post("/api/generate-video", response_model=VideoGenerationStatus)
async def request_video_generation(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Endpoint pour démarrer la génération d'une vidéo à partir d'un prompt."""
    # Générer un ID unique pour la tâche
    task_id = str(uuid.uuid4())
    
    # Initialiser le statut de la tâche
    video_generation_tasks[task_id] = {
        "status": "pending",
        "progress": 0.0,
        "video_info": None,
        "error": None
    }
    
    # Lancer la génération en arrière-plan
    background_tasks.add_task(generate_video_task, task_id, request)
    
    return VideoGenerationStatus(
        task_id=task_id,
        status="pending",
        progress=0.0
    )

@app.get("/api/video-generation-status/{task_id}", response_model=VideoGenerationStatus)
async def check_video_generation_status(task_id: str):
    """Vérifie le statut d'une tâche de génération de vidéo."""
    if task_id not in video_generation_tasks:
        raise HTTPException(status_code=404, detail="Tâche de génération non trouvée")
    
    task_info = video_generation_tasks[task_id]
    
    return VideoGenerationStatus(
        task_id=task_id,
        status=task_info["status"],
        progress=task_info["progress"],
        video_info=task_info["video_info"],
        error=task_info["error"]
    )

@app.post("/api/generate-video-sync", response_model=VideoInfo)
async def generate_video_sync(request: VideoGenerationRequest):
    """Endpoint synchrone pour la génération de vidéo (pour les cas d'utilisation simples)."""
    try:
        # Générer la vidéo
        video_info = await generate_video(
            prompt=request.prompt,
            provider=request.provider,
            settings=request.settings
        )
        
        return VideoInfo(
            filename=video_info["filename"],
            file_id=video_info["file_id"],
            file_path=video_info["file_path"],
            size_bytes=video_info["size_bytes"],
            content_type=video_info["content_type"]
        )
    except VideoGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
