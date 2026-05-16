import os
from typing import Optional, Tuple
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from dotenv import set_key, load_dotenv

from langchain_groq import ChatGroq

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

router = APIRouter(prefix="/api/settings", tags=["settings"])

GROQ_HANDSHAKE_MODEL = "llama-3.3-70b-versatile"
GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"
GROQ_ANALYZER_MODEL = "llama-3.3-70b-versatile"


def _extract_groq_error_message(error: Exception) -> str:
    response = getattr(error, "response", None)
    if response is not None:
        try:
            payload = response.json()
            message = payload.get("error", {}).get("message")
            if message:
                return message
        except Exception:
            pass

    body = getattr(error, "body", None)
    if isinstance(body, dict):
        error_payload = body.get("error", {})
        message = error_payload.get("message") if isinstance(error_payload, dict) else error_payload
        message = message or body.get("message")
        if message:
            return str(message)

    return str(error)


def _validate_groq_key(api_key: str) -> Tuple[bool, Optional[str]]:
    """Valida a chave do Groq fazendo uma chamada simples à API com timeout."""
    masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
    print(f"🔍 [Handshake] Testando Chave Groq: {masked_key}")
    try:
        # Força o override para garantir que estamos testando a chave que acabou de chegar
        load_dotenv(override=True)
        # Usamos uma temperatura 0 e um modelo leve para um ping rápido
        llm = ChatGroq(groq_api_key=api_key, model_name=GROQ_HANDSHAKE_MODEL, timeout=10)
        llm.invoke("ping")
        print(f"✅ [Handshake] Chave Groq validada com sucesso.")
        return True, None
    except Exception as e:
        error_message = _extract_groq_error_message(e)
        print(f"❌ [Handshake] Erro na validação da chave Groq ({masked_key}): {error_message}")
        return False, error_message

import requests

def _validate_meta_keys(app_id: str, app_secret: str, access_token: str, ad_account_id: str) -> bool:
    """Valida as chaves da Meta tentando uma chamada real à Graph API."""
    masked_token = f"{access_token[:6]}...{access_token[-4:]}" if len(access_token) > 10 else "***"
    print(f"🔍 [Handshake] Testando Credenciais Meta (Token: {masked_token})")
    try:
        load_dotenv(override=True)
        # Teste 1: Inicialização da SDK
        FacebookAdsApi.init(app_id, app_secret, access_token)
        account = AdAccount(f"act_{ad_account_id}")
        
        # Teste 2: Chamada real à Graph API (mais confiável que apenas init)
        url = f"https://graph.facebook.com/v21.0/me?fields=id&access_token={access_token}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ [Handshake] Erro Graph API: {response.json()}")
            return False

        # Teste 3: Acesso à conta de anúncios
        account.get_campaigns(fields=['id'], params={'limit': 1})
        
        print(f"✅ [Handshake] Credenciais Meta validadas com sucesso.")
        return True
    except Exception as e:
        print(f"❌ [Handshake] Erro na validação das chaves Meta: {e}")
        return False

def _validate_langchain_key(api_key: str) -> bool:
    """Valida o formato básico da chave LangChain."""
    if not api_key or not api_key.startswith("lsv2_"):
        return False
    return len(api_key) > 20

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
    groq_default_model: Optional[str] = Field(None, description="Modelo Groq padrão")
    groq_analyzer_model: Optional[str] = Field(None, description="Modelo Groq para o Analyzer")
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

    # Agora são 6 chaves obrigatórias
    status.is_fully_configured = all([
        status.has_groq_key,
        status.has_meta_app_id,
        status.has_meta_app_secret,
        status.has_meta_access_token,
        status.has_ad_account_id,
        status.has_langchain_key
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
    # Validação de campos vazios
    essential_fields = {
        "Groq API Key": settings.groq_api_key,
        "Meta App ID": settings.meta_app_id,
        "Meta App Secret": settings.meta_app_secret,
        "Meta Access Token": settings.meta_access_token,
        "Ad Account ID": settings.ad_account_id,
        "LangChain API Key": settings.langchain_api_key,
    }
    
    invalid = []
    for name, val in essential_fields.items():
        if not val or not val.strip():
            invalid.append(f"{name} (vazio)")

    if invalid:
        raise HTTPException(
            status_code=400, 
            detail=f"Falha de Validação: {', '.join(invalid)}"
        )

    # Validação REAL da chave Groq
    if settings.groq_api_key:
        is_valid_groq_key, groq_error = _validate_groq_key(settings.groq_api_key)
        if not is_valid_groq_key:
            error_detail = groq_error or "O servidor recusou a conexão. Verifique suas credenciais."
            return JSONResponse(
                status_code=401,
                content={"error": f"❌ Chave Groq Inválida: {error_detail}"}
            )

    # Validação REAL da chave LangChain
    if settings.langchain_api_key:
        if not _validate_langchain_key(settings.langchain_api_key):
            return JSONResponse(
                status_code=401,
                content={"error": "❌ Chave LangChain Inválida: Formato incorreto (deve começar com lsv2_)."}
            )

    # Validação REAL das chaves Meta
    if all([settings.meta_app_id, settings.meta_app_secret, settings.meta_access_token, settings.ad_account_id]):
        if not _validate_meta_keys(
            settings.meta_app_id, 
            settings.meta_app_secret, 
            settings.meta_access_token, 
            settings.ad_account_id
        ):
            return JSONResponse(
                status_code=401,
                content={"error": "❌ Credenciais Meta Inválidas: O servidor recusou o token ou o acesso à conta."}
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
        "GROQ_DEFAULT_MODEL": settings.groq_default_model,
        "GROQ_ANALYZER_MODEL": settings.groq_analyzer_model,
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
