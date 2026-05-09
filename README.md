# 🚀 Meta Ads Multi-Agent System (V4 Stable)

Um sistema inteligente de automação e análise de Meta Ads baseado em uma arquitetura de **5 Agentes Especializados** utilizando **LangGraph**, **Groq (Llama 3.1 8B)** e **ChromaDB**. Este projeto foi desenhado para profissionais de tráfego pago que buscam transformar dados brutos em estratégias acionáveis com memória de longo prazo.

---

## 🧠 A Arquitetura: O Time de Especialistas

O sistema opera como um squad de marketing digital, onde cada agente possui responsabilidades e ferramentas únicas:

1.  **Router (O Capitão) 👨‍✈️**: Analisa a pergunta do usuário e define o fluxo de execução. Ele decide quem deve agir e garante que o processo termine de forma eficiente.
2.  **Research (O Pesquisador) 🔍**: Conecta-se à **Meta Ads API** para buscar dados reais, consulta o histórico no **ChromaDB** e traz benchmarks do mercado.
3.  **Analyzer (O Analista) 📊**: Realiza a "escovação de bits". Ele identifica padrões matemáticos, tendências de queda/ascensão e detecta anomalias (como picos de gasto sem conversão).
4.  **Strategist (O Estrategista) 💡**: Transforma a análise em planos práticos. Define prioridades baseadas em ROI vs Risco e sugere ações como escalonamento ou troca de criativos.
5.  **Memory Keeper (O Guardião) 📚**: Responsável pela inteligência de longo prazo. Salva os aprendizados de cada ciclo no banco de dados vetorial para que o sistema fique "mais esperto" a cada consulta.

---

## 🛠️ Tecnologias Utilizadas

*   **LangGraph**: Orquestração de estado e agentes em grafo.
*   **Groq (Llama 3.1 8B)**: Processamento de linguagem natural ultra-rápido.
*   **Meta Business SDK**: Integração oficial com a API de anúncios.
*   **ChromaDB**: Banco de dados vetorial para memória persistente.
*   **HuggingFace Embeddings**: Para representação vetorial semântica de alta qualidade.

---

## ⚙️ Configuração e Instalação

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/meta-ads-agent.git
cd meta-ads-agent
```

### 2. Configurar o Ambiente Virtual
```bash
python -m venv venv
# No Windows:
.\venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Variáveis de Ambiente (.env)
Crie um arquivo `.env` na raiz do projeto com as seguintes chaves:
```env
META_ACCESS_TOKEN=seu_token_aqui
META_APP_ID=seu_app_id
META_APP_SECRET=seu_app_secret
AD_ACCOUNT_ID=act_sua_conta
GROQ_API_KEY=sua_chave_groq
```

---

## 🚀 Como Usar

Basta executar o script principal:
```bash
python main.py
```

### Exemplo de Perguntas:
*   "Como está a performance da última semana e o que devo otimizar?"
*   "Compare meus resultados atuais com os aprendizados da campanha de Black Friday anterior."
*   "Gere uma estratégia de escala para as campanhas que estão com ROAS acima de 3."

---

## 🛡️ Diferenciais Técnicos (Blindagem)

*   **Rota Determinística**: O sistema encerra automaticamente após o Memory Keeper, evitando loops infinitos e desperdício de tokens.
*   **Context Trimming**: Função inteligente que limpa o histórico de mensagens para manter a IA rápida e evitar erros de limite de contexto.
*   **Resiliência por Agente**: Cada agente possui tratamento de erros individualizado; se um falha, o sistema reporta o erro e continua disponível para a próxima tarefa.

---

## 🤝 Contribuições

Este é um projeto Open Source! Sinta-se à vontade para:
1. Abrir **Issues** com bugs ou sugestões.
2. Enviar **Pull Requests** com novos agentes (ex: um Agente Copywriter ou Agente de Relatórios PDF).
3. Melhorar os prompts dos agentes existentes.

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---
*Desenvolvido para a comunidade de automação e tráfego pago.* 🚀
