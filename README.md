<div align="center">

# 🚀 OMNICHANNEL TRAFFIC AI SQUAD
### The Open Source Multi-Agent Ecosystem for High-Performance Traffic Management

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.100+-05998b?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C?style=for-the-badge&logo=langchain)](https://langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3-f55036?style=for-the-badge&logo=groq)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-00d1b2?style=for-the-badge)](https://www.trychroma.com/)

---

**Omnichannel Traffic AI Squad** é uma plataforma de orquestração multi-agente projetada para revolucionar a gestão de tráfego pago. Rodando **100% localmente**, o sistema utiliza inteligência artificial de última geração para analisar, otimizar e escalar campanhas em Meta, Google, TikTok, Pinterest e LinkedIn.

[Explore o Dashboard](#-arquitetura) • [Instalação Rápida](#-guia-passo-a-passo) • [Contribua](#-créditos)

</div>

---

## 🔥 O Que Há de Novo (v2.0)

A versão 2.0 traz recursos de nível enterprise para o ecossistema local:

- **🚀 Visualizador de Orquestração**: Acompanhe em tempo real a troca de mensagens entre os agentes (`Router`, `Research`, `Analyzer`, `Memory`) através de um mapa de nós interativo e animado.
- **🛡️ Vault Gatekeeper**: Sistema de segurança rigoroso. A interface e o dashboard permanecem bloqueados e monitorados até que todas as chaves de API sejam configuradas localmente.
- **📡 Health Checks Nativos**: Monitoramento contínuo da saúde do backend FastAPI, com alertas visuais imediatos em caso de desconexão do Cérebro (Python).
- **📊 LangSmith Tracing**: Rastreamento completo de execuções nativo, permitindo auditar cada pensamento, ferramenta e token utilizado pelos agentes.

---

## 🏛️ Arquitetura (Clean Architecture)

Desenvolvido sob os princípios da **Clean Architecture**, garantindo separação de preocupações e alta escalabilidade:

*   **Domain**: Entidades de negócio, modelos core e lógica de tráfego agnóstica a frameworks.
*   **Application**: Casos de uso e orquestração do Grafo Neural (LangGraph) que coordena o squad de agentes.
*   **Infrastructure**: Clientes de API (Ads Platforms), Banco Vetorial (ChromaDB) e integrações de LLM (Groq).
*   **Interfaces**: API REST de alta performance (FastAPI) e UI Cyber-Premium (Next.js).

---

## 🤖 O Squad de Agentes

Nosso ecossistema opera através de um time de especialistas coordenados:

- **Router (O Capitão)**: Orquestração neural e roteamento inteligente.
- **Research (O Pesquisador)**: Extração de dados via Graph APIs e análise de benchmarks.
- **Analyzer (O Analista)**: Detecção de anomalias e escovação de métricas de performance.
- **Strategist (O Estrategista)**: Geração de planos de ação focados em ROI e Escala.
- **Memory Keeper (O Guardião)**: Gestão de memória semântica e histórico de aprendizado.

---

## 🛠️ Guia Passo a Passo (Setup Local)

Esqueça a configuração manual de arquivos `.env`. Nosso fluxo de **First-Time Setup (Vault)** cuida de tudo através da interface.

### 1. Clonar o Repositório
```bash
git clone https://github.com/Xwiuu/Agents-Trafego.git
cd Agents-Trafego
```

### 2. Backend (FastAPI)
```bash
# Crie e ative o ambiente virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Instale as dependências e inicie o servidor
pip install -r requirements.txt
python interfaces/api.py
```

### 3. Frontend (Next.js)
```bash
# Em um novo terminal
npm install
npm run dev
```

### 4. Ativação (Vault)
Acesse **[http://localhost:3000](http://localhost:3000)**. O sistema detectará que é sua primeira vez e abrirá o **Vault Access**. Insira suas chaves (Groq, Meta Ads e LangChain) e o esquadrão estará online!

---

## 💎 Design System
A interface foi construída com foco na experiência do usuário **Premium**:
- **Estética Cyber/Dark**: Utilizando `bg-zinc-950` e acentos em `Orange-500`.
- **Animações GSAP & Framer Motion**: Micro-interações fluídas e visualização de fluxo de agentes.
- **Dashboard Neural**: Monitoramento em tempo real do status de cada agente e métricas de processamento.

---

## ❤️ Créditos

Um agradecimento especial à **Comunidade Coda** por inspirar este projeto.

**Link Oficial:** [https://github.com/Xwiuu/Agents-Trafego](https://github.com/Xwiuu/Agents-Trafego)

**Autor Principal:** [William Reis](https://github.com/Xwiuu)

---
<div align="center">
  <sub>Open Source with Love 💚. This project is intended for educational and performance optimization purposes.</sub>
</div>
