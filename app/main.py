import io
from pathlib import Path
from fastapi import FastAPI
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.processador_plano_diretor import analisar

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
    return FileResponse(Path(__file__).resolve().parent.parent / "index.html")


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
    
@app.post("/api/baixar")    
async def baixar(arquivo: UploadFile = File(...)):
    try:
        conteudo = await arquivo.read()
    
        resultado, arquivo_corrigido = analisar(
            conteudo,
            exportar=True
        )
        
        if arquivo_corrigido is None:
            raise HTTPException(
                status_code=422,
                detail={
                    "mensagem":"A planilha apresenta erros que impedem a exportação.",
                    "totalErros":resultado["totalErros"],
                    "erros":resultado["erros"]
                }
            )
        return StreamingResponse(
            io.BytesIO(arquivo_corrigido),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": 'attachment; filename="plano_diretor_corrigido.xlsx"'
            }
        )
        
    except ValueError as erro:
        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )