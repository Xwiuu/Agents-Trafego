import os
from typing import List, Optional, Dict
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign as MetaCampaign
from facebook_business.adobjects.adsinsights import AdsInsights
from domain.entities import Campaign, Metrics
from domain.enums import PlatformEnum
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from infrastructure.logger import global_logs, logger

class MetaAdsClient:
    def _init_api(self):
        """Inicializa ou atualiza a conexão com a API da Meta usando as chaves atuais do .env."""
        global_logs.increment_api_calls() # Rastreia a tentativa de conexão para o Dashboard
        app_id = os.getenv("META_APP_ID")
        app_secret = os.getenv("META_APP_SECRET")
        access_token = os.getenv("META_ACCESS_TOKEN")
        ad_account_id = os.getenv("AD_ACCOUNT_ID")
        
        if not all([app_id, app_secret, access_token, ad_account_id]):
            logger.error("⚠️ [Meta API] Credenciais incompletas. Configure o Vault.")
            raise ValueError("⚠️ [Meta API] Credenciais incompletas. Configure o Vault.")
        
        try:
            FacebookAdsApi.init(app_id, app_secret, access_token)
            return AdAccount(f"act_{ad_account_id}")
        except Exception as e:
            logger.exception(f"Erro fatal ao conectar na Meta API: {str(e)}")
            raise Exception(f"Erro ao conectar na Meta API: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def get_active_campaigns(self) -> List[Campaign]:
        """Busca campanhas com status 'ACTIVE' e mapeia para a entidade de domínio."""
        try:
            account = self._init_api()
            fields = [
                MetaCampaign.Field.id,
                MetaCampaign.Field.name,
                MetaCampaign.Field.status,
                MetaCampaign.Field.daily_budget,
                MetaCampaign.Field.lifetime_budget,
            ]
            params = {
                'effective_status': ['ACTIVE'],
            }
            
            meta_campaigns = account.get_campaigns(fields=fields, params=params)
            campaigns = []
            for c in meta_campaigns:
                daily = float(c.get('daily_budget', 0))
                lifetime = float(c.get('lifetime_budget', 0))
                budget = (daily if daily > 0 else lifetime) / 100.0
                
                campaigns.append(Campaign(
                    id=str(c['id']),
                    name=str(c['name']),
                    platform=PlatformEnum.META,
                    status=str(c['status']),
                    budget=budget,
                    metrics={}
                ))
            return campaigns
        except Exception as e:
            logger.error(f"Error fetching active Meta campaigns: {e}")
            raise # Lança para o tenacity tentar novamente

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def get_campaign_insights(self, campaign_id: str) -> Optional[Metrics]:
        """Busca métricas de performance para uma campanha específica."""
        try:
            self._init_api()
            fields = [
                AdsInsights.Field.impressions,
                AdsInsights.Field.clicks,
                AdsInsights.Field.spend,
                AdsInsights.Field.inline_link_click_ctr,
                AdsInsights.Field.cost_per_inline_link_click,
                AdsInsights.Field.purchase_roas,
                AdsInsights.Field.actions,
            ]
            
            campaign = MetaCampaign(campaign_id)
            insights = campaign.get_insights(fields=fields)
            
            if not insights:
                return None
            
            data = insights[0]
            
            conversions = 0
            actions = data.get('actions', [])
            for action in actions:
                if action['action_type'] in ['purchase', 'offsite_conversion.fb_pixel_purchase']:
                    conversions = int(action['value'])
                    break
            
            roas_list = data.get('purchase_roas', [])
            roas = 0.0
            for r in roas_list:
                if r['action_type'] in ['purchase', 'omni_purchase']:
                    roas = float(r['value'])
                    break

            return Metrics(
                ctr=float(data.get('inline_link_click_ctr', 0)),
                cpc=float(data.get('cost_per_inline_link_click', 0)),
                roas=roas,
                conversions=conversions,
                impressions=int(data.get('impressions', 0)),
                clicks=int(data.get('clicks', 0)),
                spend=float(data.get('spend', 0))
            )
        except Exception as e:
            logger.error(f"Error fetching Meta insights for campaign {campaign_id}: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def pause_campaign(self, campaign_id: str) -> bool:
        """Altera o status de uma campanha para 'PAUSED' no Meta Ads."""
        try:
            self._init_api()
            campaign = MetaCampaign(campaign_id)
            campaign.remote_update(params={
                MetaCampaign.Field.status: MetaCampaign.Status.paused,
            })
            logger.info(f"Campanha {campaign_id} pausada com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Falha ao pausar campanha {campaign_id}: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def update_campaign_budget(self, campaign_id: str, new_daily_budget: float) -> bool:
        """Atualiza o orçamento diário de uma campanha. Meta espera o valor em centavos."""
        try:
            self._init_api()
            budget_in_cents = int(new_daily_budget * 100)
            
            campaign = MetaCampaign(campaign_id)
            campaign.remote_update(params={
                MetaCampaign.Field.daily_budget: budget_in_cents,
            })
            logger.info(f"Orçamento da campanha {campaign_id} atualizado para R$ {new_daily_budget:.2f}.")
            return True
        except Exception as e:
            logger.error(f"Falha ao atualizar orçamento da campanha {campaign_id}: {str(e)}")
            raise
