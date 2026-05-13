from langchain_core.tools import tool
from infrastructure.api_clients.meta_ads_client import MetaAdsClient

meta_client = MetaAdsClient()

@tool
def tool_pause_campaign(campaign_id: str) -> str:
    """Pausa uma campanha ativa no Meta Ads. 
    O parâmetro 'campaign_id' deve ser o ID exato da campanha (string).
    Use esta ferramenta quando o usuário solicitar explicitamente para parar ou pausar uma campanha."""
    success = meta_client.pause_campaign(campaign_id)
    if success:
        return f"A campanha {campaign_id} foi pausada com sucesso no Meta Ads."
    else:
        return f"Erro: Não foi possível pausar a campanha {campaign_id}. Verifique os logs para mais detalhes."

@tool
def tool_increase_budget(campaign_id: str, new_budget: float) -> str:
    """Atualiza (aumenta ou altera) o orçamento diário de uma campanha no Meta Ads.
    O 'campaign_id' deve ser uma string e o 'new_budget' um valor numérico (float) representando o novo valor diário em Reais (R$).
    Exemplo: Para alterar para R$ 100,00, passe 100.0.
    Use esta ferramenta quando o usuário pedir para aumentar, diminuir ou ajustar o investimento de uma campanha."""
    success = meta_client.update_campaign_budget(campaign_id, new_budget)
    if success:
        return f"O orçamento da campanha {campaign_id} foi atualizado para R$ {new_budget:.2f} com sucesso."
    else:
        return f"Erro: Não foi possível atualizar o orçamento da campanha {campaign_id}."
