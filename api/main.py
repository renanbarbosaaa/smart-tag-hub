from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from domain.validators import is_valid_slug

app = FastAPI(title="Smart Tag Hub - Encurtador NFC", version="1.0")

# temporary in memory data base, specially for validating the web rote
FAKE_DB = {
    "aX7b9Y": "https://www.pathto.com/test1a"
}

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao backend do encurtador pathto.com.br"}

@app.get("/{slug}")
def redirect_to_target(slug: str):
    # 1. validatin the slug format with or business rule
    if not is_valid_slug(slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug com formato inválido."
        )
    
    # 2. searching on temporary dictionary
    target_url = FAKE_DB.get(slug)
    
    if not target_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link não encontrado."
        )
    
    # 3. HTTP 307 redirecting (Temporary Redirect) based on my system design
    return RedirectResponse(url=target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)