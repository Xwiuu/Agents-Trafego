import os
from typing import List, Optional, Dict
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign as MetaCampaign
from facebook_business.adobjects.adsinsights import AdsInsights
from domain.entities import Campaign, Metrics
from domain.enums import PlatformEnum

class MetaAdsClient:
    def __init__(self):
        self.app_id = os.getenv("META_APP_ID")
        self.app_secret = os.getenv("META_APP_SECRET")
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.ad_account_id = os.getenv("AD_ACCOUNT_ID")
        
        if not all([self.app_id, self.app_secret, self.access_token, self.ad_account_id]):
            print("Warning: Meta Ads credentials not fully configured in environment variables.")
        
        try:
            FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            self.account = AdAccount(f"act_{self.ad_account_id}")
        except Exception as e:
            print(f"Error initializing Meta Ads API: {e}")

    def get_active_campaigns(self) -> List[Campaign]:
        """Busca campanhas com status 'ACTIVE' e mapeia para a entidade de domínio."""
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
        
        try:
            meta_campaigns = self.account.get_campaigns(fields=fields, params=params)
            campaigns = []
            for c in meta_campaigns:
                # Meta retorna orçamentos em centavos (dividir por 100)
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
            print(f"Error fetching active Meta campaigns: {e}")
            return []

    def get_campaign_insights(self, campaign_id: str) -> Optional[Metrics]:
        """Busca métricas de performance para uma campanha específica."""
        fields = [
            AdsInsights.Field.impressions,
            AdsInsights.Field.clicks,
            AdsInsights.Field.spend,
            AdsInsights.Field.inline_link_click_ctr,
            AdsInsights.Field.cost_per_inline_link_click,
            AdsInsights.Field.purchase_roas,
            AdsInsights.Field.actions,
        ]
        
        try:
            campaign = MetaCampaign(campaign_id)
            insights = campaign.get_insights(fields=fields)
            
            if not insights:
                return None
            
            data = insights[0]
            
            # Extrair conversões (compras)
            conversions = 0
            actions = data.get('actions', [])
            for action in actions:
                if action['action_type'] in ['purchase', 'offsite_conversion.fb_pixel_purchase']:
                    conversions = int(action['value'])
                    break
            
            # ROAS (Return on Ad Spend)
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
            print(f"Error fetching Meta insights for campaign {campaign_id}: {e}")
            return None
