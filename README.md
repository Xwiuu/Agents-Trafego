# Omnichannel Traffic AI Squad 🤖📈

![Status: Stable/Production Ready](https://img.shields.io/badge/Status-Stable%2FProduction%20Ready-green)
![Version](https://img.shields.io/badge/Version-2.1-blue)
![Python](https://img.shields.io/badge/Python-FastAPI-yellow)
![Next.js](https://img.shields.io/badge/Next.js-React-black)

O primeiro sistema de agentes autônomos para Meta Ads focado em ROI real, segurança ofensiva e otimização extrema de recursos.

---

## 🚀 Visão Geral

O **Omnichannel Traffic AI Squad** é uma solução de engenharia de IA de ponta, projetada para gerenciar e otimizar campanhas de tráfego pago com autonomia total e supervisão rigorosa. A arquitetura resiliente é focada em performance, segurança e eficiência de custos computacionais.

---

## 💎 Funcionalidades Principais

- 🔐 **Iron Gatekeeper:** Sistema de Vault blindado com handshake ativo de chaves (Groq/Meta). Garante que nenhuma credencial seja exposta e valida a conectividade em tempo real.
- 🎛️ **Architecture Split:** Separação clara entre o **Dashboard de Performance** (visualização de métricas em tempo real) e o **Command Center** (interface de orquestração de agentes via LangGraph).
- 🌙 **Turno da Madrugada:** Rotina autônoma de inspeção que opera 24/7, identificando e pausando campanhas com ROAS abaixo do limite crítico sem intervenção humana.
- 📉 **Token Optimization (Anti 413 TPM):** Estratégia avançada de gerenciamento de contexto, poda agressiva de payload e limitação de leitura no Meta (Top 5 campanhas), garantindo máxima eficiência e zero gargalos de Rate Limit na Groq.
- 📜 **Audit Log:** Rastreabilidade total. Cada decisão tomada pela IA é registrada, permitindo auditorias detalhadas de performance e segurança.

---

## 🛠️ Stack Tecnológica

- **Backend:** Python (FastAPI)
- **Engine de Agentes:** LangGraph (Stateful Multi-Agent Orchestration)
- **Frontend:** Next.js, Tailwind CSS
- **APIs de Ad Network:** Meta Graph API v19.0 (Estabilizada)
- **LLM Provider:** Groq (Llama 3.1 & Llama 3.3)
- **Database:** ChromaDB (Memória Vetorial)

---

## 🛡️ Segurança e Integridade

Camadas avançadas de proteção:
- **Blindagem de Logs:** Filtros inteligentes que impedem o vazamento de informações sensíveis ou tokens em logs de execução.
- **Validação Rigorosa de IDs:** Mecanismo de defesa que ignora placeholders ou strings inválidas, exigindo IDs numéricos reais para qualquer operação na Graph API.
- **Circuit Breaker:** Proteção contra chamadas excessivas ou falhas em cascata nas APIs de terceiros.
- **Isolamento de Ferramentas:** Lógica de negócio isolada das validações do LangChain, prevenindo `TypeErrors` e permitindo chamadas independentes.

---

## 📅 Histórico de Versões (Changelog)

### **v2.1 - Performance & Stability Update (Atual)**
- **Correção Crítica de TypeError:** Desacoplamento da lógica de negócios dos decoradores `@tool` no `meta_tools.py`, corrigindo o erro `StructuredTool object is not callable`.
- **Prevenção de Rate Limit (413 TPM):** 
  - Limite severo (Top 5) de campanhas enviadas ao LLM via Meta Graph API, com serialização de payload ultradensa.
  - Poda agressiva no State do LangGraph (`orchestrator.py`), mantendo no histórico apenas a rodada de iteração atual.
- **Hibridização de Modelos:** Otimização no roteamento entre os modelos rápidos (`llama-3.1-8b`) e analíticos (`llama-3.3-70b`) dentro do LangGraph.

### **v2.0 - Mission Critical Edition**
- Introdução do Vault (Iron Gatekeeper) e handshakes de API.
- Lançamento do "Turno da Madrugada" para pausing automatizado de ROAS baixo.
- Arquitetura segregada: Painel Visual VS Console de Agentes.
- Transição para o ecossistema LangGraph e ChromaDB integrado.

### **v1.0 - MVP Base**
- Orquestração linear de prompts simples via LangChain.
- Conexão básica de leitura com a Meta API.
- Interface genérica e dependência direta do modelo sem otimizações de token.

---

## 📦 Instalação e Execução

1.  **Clonar o repositório:**
    ```bash
    git clone <repository-url>
    ```
2.  **Configurar o Ambiente:**
    Crie um arquivo `.env` na raiz com suas credenciais (Meta App ID, Secret, Access Token, Ad Account ID e Groq API Key).
3.  **Instalar Dependências:**
    ```bash
    npm install
    pip install -r requirements.txt
    ```
4.  **Iniciar o Backend e Frontend:**
    *Inicie o backend:*
    ```bash
    python -m interfaces.api
    ```
    *Inicie o frontend (em outro terminal):*
    ```bash
    npm run dev
    ```

---
*Desenvolvido para operações de escala que não aceitam margem para erro.*
