import os
from typing import Dict, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from dotenv import set_key, load_dotenv

router = APIRouter(prefix="/api/settings", tags=["settings"])

# Chaves que o sistema gerencia
REQUIRED_KEYS = {
    "GROQ_API_KEY": "groq_api_key",
    "META_APP_ID": "meta_app_id",
    "META_APP_SECRET": "meta_app_secret",
    "META_ACCESS_TOKEN": "meta_access_token",
    "AD_ACCOUNT_ID": "ad_account_id",
    "LANGCHAIN_API_KEY": "langchain_api_key",
}


def _get_env_path() -> str:
    """Retorna o caminho absoluto para o arquivo .env na raiz do projeto."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, ".env")


class SettingsInput(BaseModel):
    """Modelo de entrada para atualização de configurações."""
    groq_api_key: Optional[str] = Field(None, description="Groq API Key (Llama 3)")
    meta_app_id: Optional[str] = Field(None, description="Meta App ID")
    meta_app_secret: Optional[str] = Field(None, description="Meta App Secret")
    meta_access_token: Optional[str] = Field(None, description="Meta Access Token")
    ad_account_id: Optional[str] = Field(None, description="Ad Account ID")
    langchain_api_key: Optional[str] = Field(None, description="LangChain API Key (Tracing)")


class SettingsStatus(BaseModel):
    """Modelo de saída para verificação de configurações."""
    has_groq_key: bool = Field(False, description="Se a Groq API Key está configurada")
    has_meta_app_id: bool = Field(False, description="Se o Meta App ID está configurado")
    has_meta_app_secret: bool = Field(False, description="Se o Meta App Secret está configurado")
    has_meta_access_token: bool = Field(False, description="Se o Meta Access Token está configurado")
    has_ad_account_id: bool = Field(False, description="Se o Ad Account ID está configurado")
    has_langchain_key: bool = Field(False, description="Se a LangChain API Key está configurada")
    is_fully_configured: bool = Field(False, description="Se todas as chaves obrigatórias estão configuradas")


def _get_current_status() -> SettingsStatus:
    """Helper to read .env and populate SettingsStatus."""
    env_path = _get_env_path()
    load_dotenv(dotenv_path=env_path, override=True)

    status = SettingsStatus()
    status.has_groq_key = bool(os.getenv("GROQ_API_KEY", "").strip())
    status.has_meta_app_id = bool(os.getenv("META_APP_ID", "").strip())
    status.has_meta_app_secret = bool(os.getenv("META_APP_SECRET", "").strip())
    status.has_meta_access_token = bool(os.getenv("META_ACCESS_TOKEN", "").strip())
    status.has_ad_account_id = bool(os.getenv("AD_ACCOUNT_ID", "").strip())
    status.has_langchain_key = bool(os.getenv("LANGCHAIN_API_KEY", "").strip())

    status.is_fully_configured = all([
        status.has_groq_key,
        status.has_meta_app_id,
        status.has_meta_app_secret,
        status.has_meta_access_token,
        status.has_ad_account_id,
    ])
    return status


@router.get("", response_model=SettingsStatus)
async def get_settings_status():
    """
    Verifica quais chaves essenciais já estão configuradas no .env.
    Nunca retorna as chaves em texto plano, apenas status booleano.
    """
    return _get_current_status()


@router.post("")
async def update_settings(settings: SettingsInput):
    """
    Recebe as chaves do usuário e escreve no arquivo .env.
    Retorna o status atualizado de todas as chaves.
    """
    # Validação Blindada: Impedir chaves vazias ou muito curtas para campos essenciais
    essential_fields = {
        "Groq API Key": settings.groq_api_key,
        "Meta App ID": settings.meta_app_id,
        "Meta App Secret": settings.meta_app_secret,
        "Meta Access Token": settings.meta_access_token,
        "Ad Account ID": settings.ad_account_id,
    }
    
    invalid = []
    for name, val in essential_fields.items():
        if not val or not val.strip():
            invalid.append(f"{name} (vazio)")
        elif len(val.strip()) < 8:
            invalid.append(f"{name} (muito curto)")

    if invalid:
        raise HTTPException(
            status_code=400, 
            detail=f"Falha de Validação de Segurança: {', '.join(invalid)}"
        )

    env_path = _get_env_path()

    # Garantir que o arquivo .env existe
    if not os.path.exists(env_path):
        try:
            with open(env_path, "w") as f:
                pass
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao criar .env: {str(e)}")

    # Mapear campos do modelo para variáveis de ambiente
    updates = {
        "GROQ_API_KEY": settings.groq_api_key,
        "META_APP_ID": settings.meta_app_id,
        "META_APP_SECRET": settings.meta_app_secret,
        "META_ACCESS_TOKEN": settings.meta_access_token,
        "AD_ACCOUNT_ID": settings.ad_account_id,
        "LANGCHAIN_API_KEY": settings.langchain_api_key,
    }

    try:
        for key, value in updates.items():
            if value is not None and value.strip():
                set_key(env_path, key, value.strip())
                if key == "LANGCHAIN_API_KEY":
                    set_key(env_path, "LANGCHAIN_TRACING_V2", "true")

        # Recarga o .env para aplicar imediatamente no processo atual
        load_dotenv(dotenv_path=env_path, override=True)

        # Retorna o status atualizado
        new_status = _get_current_status()

        return {
            "status": "success", 
            "message": "Configurações salvas com sucesso. Sistemas atualizados.",
            "data": new_status.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar configurações: {str(e)}")
