import json
from langchain_core.tools import tool
from infrastructure.api_clients.meta_ads_client import MetaAdsClient

meta_client = MetaAdsClient()

def _get_active_campaigns_payload() -> str:
    campaigns = meta_client.get_active_campaign_summaries()
    if not campaigns:
        return "Nenhuma campanha ativa encontrada no Meta Ads."

    return json.dumps(campaigns, ensure_ascii=False, separators=(",", ":"))

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
    campaign_id = str(campaign_id).strip()
    metrics = meta_client.get_campaign_insights(campaign_id)
    if not metrics:
        return f"Não foi possível encontrar métricas para a campanha com ID {campaign_id}."
    
    data = {
        "campaign_id": campaign_id,
        "ctr": round(metrics.ctr, 4),
        "cpc": round(metrics.cpc, 2),
        "roas": round(metrics.roas, 2),
        "conversions": metrics.conversions,
        "clicks": metrics.clicks,
        "spend": round(metrics.spend, 2),
        "cpa": round(metrics.spend / metrics.conversions, 2) if metrics.conversions else None,
    }
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
