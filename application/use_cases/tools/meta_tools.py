import json
from langchain_core.tools import tool
from infrastructure.api_clients.meta_ads_client import MetaAdsClient

meta_client = MetaAdsClient()

@tool
def tool_get_active_campaigns() -> str:
    """Busca todas as campanhas que estão atualmente com status 'ACTIVE' (ativas) no Meta Ads. 
    Use esta ferramenta para ter uma visão geral do que está rodando antes de analisar métricas específicas."""
    campaigns = meta_client.get_active_campaigns()
    if not campaigns:
        return "Nenhuma campanha ativa encontrada no Meta Ads."
    
    # Formata para JSON amigável para o Llama 3
    data = [
        {
            "id": c.id,
            "name": c.name,
            "status": c.status,
            "budget": f"R$ {c.budget:.2f}"
        }
        for c in campaigns
    ]
    return json.dumps(data, indent=2, ensure_ascii=False)

@tool
def tool_get_campaign_metrics(campaign_id: str) -> str:
    """Analisa a performance de uma campanha específica do Meta Ads usando seu ID.
    Retorna métricas cruciais como ROAS, CPC, CTR, Impressões, Cliques e Gasto Total.
    Use esta ferramenta para diagnósticos detalhados e otimização de campanhas baseada em dados reais."""
    metrics = meta_client.get_campaign_insights(campaign_id)
    if not metrics:
        return f"Não foi possível encontrar métricas para a campanha com ID {campaign_id}."
    
    data = {
        "campaign_id": campaign_id,
        "ctr": f"{metrics.ctr:.2%}",
        "cpc": f"R$ {metrics.cpc:.2f}",
        "roas": f"{metrics.roas:.2f}x",
        "conversions": metrics.conversions,
        "impressions": metrics.impressions,
        "clicks": metrics.clicks,
        "spend": f"R$ {metrics.spend:.2f}"
    }
    return json.dumps(data, indent=2, ensure_ascii=False)
