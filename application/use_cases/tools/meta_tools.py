import json
from langchain_core.tools import tool
from infrastructure.api_clients.meta_ads_client import MetaAdsClient

meta_client = MetaAdsClient()

def _get_active_campaigns_payload() -> str:
    payload = meta_client.get_active_campaign_summaries()
    return payload

def _get_campaign_metrics_logic(campaign_id: str) -> str:
    campaign_id = str(campaign_id).strip()
    m = meta_client.get_campaign_insights(campaign_id)
    if not m:
        return f"ID:{campaign_id}|Erro:Não encontrado"
    
    return f"ID:{campaign_id}|CTR:{round(m.ctr,4)}|CPC:{round(m.cpc,2)}|ROAS:{round(m.roas,2)}|Conv:{m.conversions}|Gasto:{round(m.spend,2)}"

@tool
def tool_get_active_campaign_metrics(campaign_id: str) -> str:
    """Retorna KPIs compactos de uma campanha Meta pelo ID."""
    return _get_campaign_metrics_logic(campaign_id)

@tool
def tool_get_active_campaigns() -> str:
    """Lista campanhas ativas da Meta com KPIs essenciais dos últimos 7 dias."""
    return _get_active_campaigns_payload()

@tool
def tool_get_campaigns() -> str:
    """Alias de leitura para listar campanhas Meta ativas com KPIs essenciais."""
    return _get_active_campaigns_payload()

@tool
def tool_get_campaign_metrics(campaign_id: str) -> str:
    """Retorna KPIs de uma campanha Meta pelo ID."""
    return _get_campaign_metrics_logic(campaign_id)
