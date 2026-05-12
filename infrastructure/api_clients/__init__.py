from typing import Dict, Any
from domain.entities import Campaign, Metrics
from domain.enums import PlatformEnum

class MetaAdsClient:
    def __init__(self, access_token: str, app_id: str, app_secret: str):
        self.access_token = access_token
        self.app_id = app_id
        self.app_secret = app_secret
        # Inicializar o cliente da API do Meta aqui
        
    def get_campaigns(self) -> list[Campaign]:
        # Implementar a lógica para buscar campanhas do Meta
        pass
        
    def get_metrics(self, campaign_id: str) -> Metrics:
        # Implementar a lógica para buscar métricas do Meta
        pass

class GoogleAdsClient:
    def __init__(self, credentials: str):
        self.credentials = credentials
        # Inicializar o cliente da API do Google aqui
        
    def get_campaigns(self) -> list[Campaign]:
        # Implementar a lógica para buscar campanhas do Google
        pass
        
    def get_metrics(self, campaign_id: str) -> Metrics:
        # Implementar a lógica para buscar métricas do Google
        pass

# Implementar classes similares para TikTok, LinkedIn e Pinterest
class TikTokAdsClient:
    pass

class LinkedInAdsClient:
    pass

class PinterestAdsClient:
    pass