# Omnichannel Traffic AI Squad v2.0 - Mission Critical Edition

![Status: Stable/Production Ready](https://img.shields.io/badge/Status-Stable%2FProduction%20Ready-green)

O primeiro sistema de agentes autônomos para Meta Ads focado em ROI real e segurança ofensiva.

## 🚀 Visão Geral
O **Omnichannel Traffic AI Squad v2.0** é uma solução de engenharia de IA de ponta, projetada para gerenciar e otimizar campanhas de tráfego pago com autonomia total e supervisão rigorosa. A versão 2.0 marca a transição para uma arquitetura resiliente, focada em performance, segurança e eficiência de custos.

## 💎 Novas Funcionalidades 2.0

- **Iron Gatekeeper:** Sistema de Vault blindado com handshake ativo de chaves (Groq/Meta). Garante que nenhuma credencial seja exposta e valida a conectividade em tempo real.
- **Architecture Split:** Separação clara entre o **Dashboard de Performance** (visualização de métricas em tempo real) e o **Command Center** (interface de orquestração de agentes via LangGraph).
- **Turno da Madrugada:** Rotina autônoma de inspeção que opera 24/7, identificando e pausando campanhas com ROAS abaixo do limite crítico sem intervenção humana.
- **Token Optimization:** Estratégia avançada de gerenciamento de contexto e redução de payload, garantindo máxima eficiência e menor latência ao utilizar modelos Llama 3.1 na Groq.
- **Audit Log:** Rastreabilidade total. Cada decisão tomada pela IA é registrada, permitindo auditorias detalhadas de performance e segurança.

## 🛠️ Stack Tecnológica

- **Backend:** Python (FastAPI)
- **Engine de Agentes:** LangGraph (Stateful Multi-Agent Orchestration)
- **Frontend:** Next.js, Tailwind CSS
- **APIs de Ad Network:** Meta Graph API v19.0 (Estabilizada)
- **LLM Provider:** Groq (Llama 3.1)
- **Database:** ChromaDB (Memória Vetorial)

## 🛡️ Segurança e Integridade

Nesta versão, implementamos camadas adicionais de proteção:
- **Blindagem de Logs:** Filtros inteligentes que impedem o vazamento de informações sensíveis ou tokens em logs de execução.
- **Validação Rigorosa de IDs:** Mecanismo de defesa que ignora placeholders ou strings inválidas, exigindo IDs numéricos reais para qualquer operação de leitura ou escrita na Graph API.
- **Circuit Breaker:** Proteção contra chamadas excessivas ou falhas em cascata nas APIs de terceiros.

---

### 📦 Instalação e Execução

1.  **Clonar o repositório:**
    ```bash
    git clone <repository-url>
    ```
2.  **Configurar o Ambiente:**
    Crie um arquivo `.env` com suas credenciais (Meta App ID, Secret, Access Token, Ad Account ID e Groq API Key).
3.  **Instalar Dependências:**
    ```bash
    npm install
    pip install -r requirements.txt
    ```
4.  **Iniciar o Sistema:**
    ```bash
    python main.py
    ```

---
*Desenvolvido para operações de escala que não aceitam margem para erro.*
