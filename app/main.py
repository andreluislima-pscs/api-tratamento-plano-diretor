from pathlib import Path
from fastapi import FastAPI
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.dom_eliseu import analisar

app = FastAPI(title="Mantis 29943 - Tratamento de erros em planilha - Plano Diretor", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return FileResponse(Path(__file__).resolve().parent.parent / "pagina_web.html")


@app.post("/api/processar")
async def processar(arquivo:UploadFile = File(...)):
    try:
        conteudo = await arquivo.read()
        
        resultado, _= analisar(conteudo)
        
        return resultado

    except ValueError as erro:
        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )