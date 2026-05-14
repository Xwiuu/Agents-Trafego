import os
from typing import Any, List, Optional, Dict
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign as MetaCampaign
from facebook_business.adobjects.adsinsights import AdsInsights
from domain.entities import Campaign, Metrics
from domain.enums import PlatformEnum
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from infrastructure.logger import global_logs, logger

class MetaAdsClient:
    @staticmethod
    def _to_float(value: Any) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _extract_conversions(actions: List[Dict[str, Any]]) -> int:
        conversion_types = {
            "purchase",
            "omni_purchase",
            "offsite_conversion.fb_pixel_purchase",
            "lead",
            "offsite_conversion.fb_pixel_lead",
        }
        for action in actions or []:
            if action.get("action_type") in conversion_types:
                try:
                    return int(float(action.get("value", 0)))
                except (TypeError, ValueError):
                    return 0
        return 0

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
            FacebookAdsApi.init(app_id, app_secret, access_token, api_version='v19.0')
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
        """Busca campanhas ativas e retorna só campos úteis para o LLM."""
        try:
            account = self._init_api()
            fields = [
                MetaCampaign.Field.id,
                MetaCampaign.Field.name,
                MetaCampaign.Field.status,
            ]
            params = {
                'effective_status': ['ACTIVE'],
            }
            
            meta_campaigns = account.get_campaigns(fields=fields, params=params)
            campaigns = []
            for c in meta_campaigns:
                campaigns.append(Campaign(
                    id=str(c['id']),
                    name=str(c['name']),
                    platform=PlatformEnum.META,
                    status=str(c['status']),
                    budget=0.0,
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
    def get_active_campaign_summaries(self) -> List[Dict[str, Any]]:
        """Retorna campanhas ativas em formato compacto: id, nome, status e KPIs essenciais."""
        try:
            account = self._init_api()
            limit = int(os.getenv("META_CAMPAIGN_SUMMARY_LIMIT", "25"))
            campaign_fields = [
                MetaCampaign.Field.id,
                MetaCampaign.Field.name,
                MetaCampaign.Field.status,
            ]
            campaign_params = {
                "effective_status": ["ACTIVE"],
                "limit": limit,
            }
            active_campaigns = list(account.get_campaigns(fields=campaign_fields, params=campaign_params))
            if not active_campaigns:
                return []

            summaries = {
                str(c.get("id")): {
                    "id": str(c.get("id")),
                    "name": str(c.get("name", "")),
                    "status": str(c.get("status", "ACTIVE")),
                    "spend": 0.0,
                    "clicks": 0,
                    "conversions": 0,
                    "cpa": None,
                }
                for c in active_campaigns
            }

            insight_fields = [
                AdsInsights.Field.campaign_id,
                AdsInsights.Field.clicks,
                AdsInsights.Field.spend,
                AdsInsights.Field.actions,
            ]
            params = {
                "date_preset": "last_7d",
                "level": "campaign",
                "filtering": [{
                    "field": "campaign.id",
                    "operator": "IN",
                    "value": list(summaries.keys()),
                }],
                "limit": limit,
            }

            insights = account.get_insights(fields=insight_fields, params=params)
            for row in insights:
                campaign_id = str(row.get("campaign_id", ""))
                if campaign_id not in summaries:
                    continue
                spend = self._to_float(row.get("spend"))
                clicks = int(self._to_float(row.get("clicks")))
                conversions = self._extract_conversions(row.get("actions", []))
                summaries[campaign_id].update({
                    "spend": round(spend, 2),
                    "clicks": clicks,
                    "conversions": conversions,
                    "cpa": round(spend / conversions, 2) if conversions else None,
                })
            return list(summaries.values())
        except Exception as e:
            logger.error(f"Error fetching compact Meta campaign summaries: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def get_campaign_performance_summaries(self, limit: int = 50, date_preset: str = "last_7d") -> List[Dict[str, Any]]:
        """Retorna campanhas Meta com KPIs para dashboard, sem acionar LLM."""
        try:
            account = self._init_api()
            campaign_fields = [
                MetaCampaign.Field.id,
                MetaCampaign.Field.name,
                MetaCampaign.Field.status,
            ]
            campaign_params = {
                "effective_status": ["ACTIVE", "PAUSED"],
                "limit": limit,
            }
            campaigns = list(account.get_campaigns(fields=campaign_fields, params=campaign_params))
            if not campaigns:
                return []

            summaries = {
                str(c.get("id")): {
                    "id": str(c.get("id")),
                    "name": str(c.get("name", "")),
                    "status": str(c.get("status", "UNKNOWN")),
                    "spend": 0.0,
                    "conversions": 0,
                    "cpa": None,
                    "roas": 0.0,
                }
                for c in campaigns
            }

            insight_fields = [
                AdsInsights.Field.campaign_id,
                AdsInsights.Field.spend,
                AdsInsights.Field.actions,
                AdsInsights.Field.purchase_roas,
            ]
            params = {
                "date_preset": date_preset,
                "level": "campaign",
                "filtering": [{
                    "field": "campaign.id",
                    "operator": "IN",
                    "value": list(summaries.keys()),
                }],
                "limit": limit,
            }

            insights = account.get_insights(fields=insight_fields, params=params)
            for row in insights:
                campaign_id = str(row.get("campaign_id", ""))
                if campaign_id not in summaries:
                    continue

                spend = self._to_float(row.get("spend"))
                conversions = self._extract_conversions(row.get("actions", []))
                roas = 0.0
                for item in row.get("purchase_roas", []) or []:
                    if item.get("action_type") in {"purchase", "omni_purchase"}:
                        roas = self._to_float(item.get("value"))
                        break

                summaries[campaign_id].update({
                    "spend": round(spend, 2),
                    "conversions": conversions,
                    "cpa": round(spend / conversions, 2) if conversions else None,
                    "roas": round(roas, 2),
                })

            return list(summaries.values())
        except Exception as e:
            logger.error(f"Error fetching Meta dashboard metrics: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def get_campaign_insights(self, campaign_id: str) -> Optional[Metrics]:
        """Busca métricas de performance para uma campanha específica."""
        if not str(campaign_id).isdigit():
            logger.warning(f"⚠️ [Meta Client] ID de campanha inválido ignorado: {campaign_id}")
            return None

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
            
            conversions = self._extract_conversions(data.get('actions', []))
            
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
        if not str(campaign_id).isdigit():
            logger.error(f"❌ [Meta Client] Tentativa de pausar com ID inválido: {campaign_id}")
            return False

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
        if not str(campaign_id).isdigit():
            logger.error(f"❌ [Meta Client] Tentativa de alterar budget com ID inválido: {campaign_id}")
            return False

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
