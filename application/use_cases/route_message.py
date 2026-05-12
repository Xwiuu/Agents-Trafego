from typing import List
from domain.enums import PlatformEnum

def route_message(message: str) -> List[PlatformEnum]:
    """
    Determina quais plataformas devem ser acionadas com base na mensagem do usuário.
    Esta função seria expandida para analisar a mensagem e identificar plataformas relevantes.
    """
    # Lógica de roteamento - por enquanto uma implementação simples
    # que retorna todas as plataformas
    return [PlatformEnum.META, PlatformEnum.GOOGLE, PlatformEnum.TIKTOK, PlatformEnum.PINTEREST, PlatformEnum.LINKEDIN]