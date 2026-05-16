'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Github, Terminal, ArrowRight, Layers, Cpu, Database, Network, LayoutDashboard, ShieldCheck, Activity, Eye } from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/dist/ScrollTrigger';

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

interface HubScreenProps {
  onOpenTerminal: () => void;
  onNeedSetup: () => void;
  onOpenDashboard: () => void;
  isBackendOffline?: boolean;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const HubScreen: React.FC<HubScreenProps> = ({ 
  onOpenTerminal, 
  onNeedSetup, 
  onOpenDashboard,
  isBackendOffline = false 
}) => {
  const heroRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);
  const architectureRef = useRef<HTMLDivElement>(null);
  const [setupStatus, setSetupStatus] = useState<{ is_fully_configured: boolean; has_groq_key: boolean } | null>(null);

  useEffect(() => {
    if (!isBackendOffline) {
      checkInitialStatus();
    }
    const ctx = gsap.context(() => {
      // Hero Animations
      gsap.from('.hero-title', {
        y: 50,
        opacity: 0,
        duration: 1,
        ease: 'power4.out',
      });

      gsap.from('.hero-badge', {
        scale: 0.8,
        opacity: 0,
        duration: 0.8,
        delay: 0.2,
        ease: 'back.out(1.7)',
      });

      gsap.from('.hero-cta', {
        y: 20,
        opacity: 0,
        duration: 0.8,
        delay: 0.4,
        stagger: 0.1,
        ease: 'power3.out',
      });

      // Concept section animation
      gsap.from('.concept-text', {
        scrollTrigger: {
          trigger: '.concept-section',
          start: 'top 80%',
        },
        y: 30,
        opacity: 0,
        duration: 0.8,
        ease: 'power3.out',
      });

      // Squad Cards Animations
      gsap.from('.agent-card', {
        scrollTrigger: {
          trigger: cardsRef.current,
          start: 'top 80%',
        },
        y: 40,
        opacity: 0,
        duration: 0.6,
        stagger: 0.1,
        ease: 'power2.out',
      });

      // Icon Pulse Animation
      gsap.to('.platform-icon', {
        scale: 1.1,
        repeat: -1,
        yoyo: true,
        duration: 1.5,
        ease: 'sine.inOut',
        stagger: {
          each: 0.2,
          from: 'random'
        }
      });

      // Architecture Layers Animation
      gsap.from('.arch-layer', {
        scrollTrigger: {
          trigger: architectureRef.current,
          start: 'top 70%',
        },
        x: -50,
        opacity: 0,
        duration: 0.8,
        stagger: 0.2,
        ease: 'power3.out',
      });
    }, [heroRef, cardsRef, architectureRef]);

    return () => ctx.revert();
  }, [isBackendOffline]);

  const checkInitialStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/api/settings`);
      if (res.ok) {
        const data = await res.json();
        setSetupStatus(data);
      }
    } catch (err) {
      console.error('Falha ao checar status inicial:', err);
    }
  };

  const handleTerminalOrSetup = async () => {
    if (isBackendOffline) return;
    try {
      const res = await fetch(`${API_URL}/api/settings`);
      if (!res.ok) {
        onNeedSetup();
        return;
      }
      const settings = await res.json();
      if (settings.is_fully_configured) {
        onOpenTerminal();
      } else {
        onNeedSetup();
      }
    } catch (err) {
      onNeedSetup();
    }
  };

  const agents = [
    { name: 'Capitão Router', platform: 'System', description: 'Orquestração central e roteamento inteligente de tarefas entre agentes.' },
    { name: 'Agente Meta', platform: 'Meta', description: 'Otimização de ROAS e escala de criativos em tempo real via Meta Graph API.' },
    { name: 'Agente Google', platform: 'Google', description: 'Gerenciamento de lances e performance Max em buscas e rede de display.' },
    { name: 'Agente TikTok', platform: 'TikTok', description: 'Monitoramento de tendências e escala acelerada de campanhas virais.' },
    { name: 'Agente LinkedIn', platform: 'LinkedIn', description: 'Segmentação B2B de alta precisão e automação de funis corporativos.' },
    { name: 'Agente Pinterest', platform: 'Pinterest', description: 'Otimização visual e descoberta de produtos com foco em conversão.' },
  ];

  const archLayers = [
    { name: 'Interfaces', icon: <Terminal size={24} />, color: 'orange', desc: 'API REST (FastAPI) e Dashboard em tempo real.' },
    { name: 'Infrastructure', icon: <Database size={24} />, color: 'zinc', desc: 'Memória Vetorial (ChromaDB) e Clientes de API (Ads Platforms).' },
    { name: 'Application', icon: <Cpu size={24} />, color: 'orange', desc: 'Orquestração LangGraph e Lógica Multi-Agente.' },
    { name: 'Domain', icon: <Layers size={24} />, color: 'zinc', desc: 'Entidades, Modelos e Regras de Negócio Core.' },
  ];

  const features = [
    { 
        title: "Visualizador Neural", 
        desc: "Acompanhe os agentes trocando dados e tomando decisões em tempo real através do nosso mapa de nós animado.", 
        icon: <Eye className="text-orange-500" size={24} /> 
    },
    { 
        title: "Vault Gatekeeper", 
        desc: "Segurança local first. Suas chaves nunca saem da máquina e o acesso é bloqueado até a configuração completa.", 
        icon: <ShieldCheck className="text-orange-500" size={24} /> 
    },
    { 
        title: "LangSmith Tracing", 
        desc: "Total transparência. Rastreamento nativo para auditar cada token e pensamento da Inteligência Artificial.", 
        icon: <Activity className="text-orange-500" size={24} /> 
    }
  ];

  return (
    <div className="bg-zinc-950 text-white selection:bg-orange-500/30 selection:text-orange-200">
      {/* Hero Section */}
      <section ref={heroRef} className="relative min-h-[90vh] flex flex-col items-center justify-center px-6 overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-orange-500/10 rounded-full blur-[120px] pointer-events-none"></div>

        <div className="relative z-10 text-center max-w-5xl">
          <div className="hero-badge inline-flex items-center space-x-2 bg-zinc-900 border border-zinc-800 px-4 py-1.5 rounded-full mb-8">
            <span className="text-orange-500">💚</span>
            <span className="text-orange-500 font-medium text-sm">Feito pela Comunidade Coda</span>
          </div>

          <h1 className="hero-title text-6xl md:text-8xl font-black tracking-tighter mb-8 bg-gradient-to-b from-white to-zinc-500 bg-clip-text text-transparent leading-none">
            OMNICHANNEL<br />TRAFFIC AI SQUAD
          </h1>

          <p className="hero-cta text-zinc-400 text-xl md:text-2xl mb-12 max-w-3xl mx-auto leading-relaxed">
            O primeiro ecossistema Open Source de Inteligência Artificial Multi-Agente para Gestão de Tráfego de Alta Performance.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={handleTerminalOrSetup}
              disabled={isBackendOffline}
              className={`hero-cta w-full sm:w-auto font-bold px-8 py-4 rounded-lg flex items-center justify-center space-x-2 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed ${
                setupStatus?.is_fully_configured === false 
                ? 'bg-zinc-900 border border-orange-500/50 text-orange-500 hover:bg-orange-500/10' 
                : 'bg-orange-500 hover:bg-orange-600 text-black'
              }`}
            >
              <Terminal size={20} />
              <span>
                {isBackendOffline ? 'Backend Offline' : (setupStatus?.is_fully_configured === false ? 'Config Required' : 'Init System')}
              </span>
              {!isBackendOffline && <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />}
            </button>

            <button
              onClick={onOpenDashboard}
              disabled={isBackendOffline}
              className={`hero-cta w-full sm:w-auto bg-zinc-900 border border-zinc-800 hover:border-orange-500/50 text-white font-bold px-8 py-4 rounded-lg flex items-center justify-center space-x-2 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <LayoutDashboard size={20} />
              <span>Dashboard</span>
            </button>

            <a
              href="https://github.com/Xwiuu/Agents-Trafego"
              target="_blank"
              rel="noopener noreferrer"
              className="hero-cta w-full sm:w-auto bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-white font-bold px-8 py-4 rounded-lg flex items-center justify-center space-x-2 transition-all duration-300"
            >
              <Github size={20} />
              <span>Ver no GitHub</span>
            </a>
          </div>
        </div>
      </section>

      {/* Features Highlight */}
      <section className="py-20 bg-zinc-900/30 border-y border-zinc-900">
        <div className="max-w-7xl mx-auto px-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {features.map((feature, i) => (
                    <div key={i} className="flex flex-col items-start p-6 rounded-2xl bg-zinc-950 border border-zinc-800/50 hover:border-orange-500/30 transition-all duration-500 group">
                        <div className="w-12 h-12 rounded-xl bg-zinc-900 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                            {feature.icon}
                        </div>
                        <h3 className="text-xl font-bold mb-3 group-hover:text-orange-500 transition-colors">{feature.title}</h3>
                        <p className="text-zinc-500 text-sm leading-relaxed">
                            {feature.desc}
                        </p>
                    </div>
                ))}
            </div>
        </div>
      </section>

      {/* Concept Section */}
      <section className="concept-section py-32 bg-black border-y border-zinc-900">
        <div className="max-w-4xl mx-auto px-6">
          <div className="flex items-center space-x-4 mb-8">
            <div className="h-px flex-1 bg-zinc-800"></div>
            <span className="text-orange-500 font-mono text-sm tracking-widest uppercase">The Concept</span>
            <div className="h-px flex-1 bg-zinc-800"></div>
          </div>

          <div className="concept-text space-y-8 text-lg md:text-xl font-mono leading-relaxed">
            <p className="text-white">
              <span className="text-orange-500">01.</span> A complexidade de gerenciar orçamentos e regras em Meta, Google, TikTok e LinkedIn manualmente é insustentável. Nosso objetivo é democratizar a orquestração de tráfego omnichannel.
            </p>
            <p className="text-zinc-400">
              <span className="text-orange-500">02.</span> Usamos um time de agentes de IA orquestrados por <span className="text-white">LangGraph</span> (com Llama 3 via Groq) e <span className="text-white">Memória Vetorial (ChromaDB)</span> para tomar decisões de lance, pausa e expansão em milissegundos.
            </p>
            <p className="text-zinc-500">
              <span className="text-orange-500">03.</span> Gerando análises profundas de ROAS que nenhum humano consegue ver simultaneamente, garantindo eficiência máxima em cada centavo investido.
            </p>
          </div>
        </div>
      </section>

      {/* Squad Section */}
      <section className="py-32 px-6 overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="mb-20">
            <h2 className="text-4xl md:text-5xl font-black mb-4">O ESQUADRÃO</h2>
            <p className="text-zinc-400 font-mono">Agentes especializados em cada camada do seu funil.</p>
          </div>

          <div ref={cardsRef} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent, i) => (
              <div key={i} className="agent-card group bg-zinc-900/50 border border-zinc-800 p-8 rounded-2xl hover:bg-zinc-900 hover:border-orange-500/50 transition-all duration-500">
                <div className="flex items-start justify-between mb-6">
                  <div className="platform-icon w-12 h-12 bg-zinc-800 rounded-xl flex items-center justify-center text-orange-500 group-hover:bg-orange-500 group-hover:text-black transition-colors duration-500">
                    <Network size={24} />
                  </div>
                  <div className="text-[10px] font-mono text-zinc-600 bg-zinc-950 px-2 py-1 rounded-md tracking-tighter uppercase">
                    Agent v1.0
                  </div>
                </div>
                <h3 className="text-xl font-bold mb-3">{agent.name}</h3>
                <p className="text-zinc-500 text-sm leading-relaxed mb-6">
                  {agent.description}
                </p>
                <div className="pt-6 border-t border-zinc-800/50 flex items-center justify-between">
                  <span className="text-[10px] font-mono text-orange-500 uppercase tracking-widest">{agent.platform} Optimized</span>
                  <div className="flex space-x-1">
                    <div className="w-1 h-1 bg-orange-500 rounded-full"></div>
                    <div className="w-1 h-1 bg-orange-500/30 rounded-full"></div>
                    <div className="w-1 h-1 bg-orange-500/30 rounded-full"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section ref={architectureRef} className="py-32 bg-black border-t border-zinc-900">
        <div className="max-w-7xl mx-auto px-6">
          <div className="mb-20 text-center">
            <h2 className="text-4xl md:text-5xl font-black mb-4">ARQUITETURA</h2>
            <p className="text-zinc-400 font-mono">Clean Architecture para alta escalabilidade.</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-4">
              {archLayers.map((layer, i) => (
                <div key={i} className="arch-layer flex items-center p-6 bg-zinc-900/30 border border-zinc-800 rounded-xl hover:bg-zinc-900 transition-colors group">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center mr-6 ${layer.color === 'orange' ? 'bg-orange-500 text-black' : 'bg-zinc-800 text-white'}`}>
                    {layer.icon}
                  </div>
                  <div>
                    <h4 className="font-bold text-lg mb-1 group-hover:text-orange-500 transition-colors">{layer.name}</h4>
                    <p className="text-zinc-500 text-sm">{layer.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="relative aspect-square lg:aspect-video bg-zinc-900/50 border border-zinc-800 rounded-3xl p-8 flex items-center justify-center overflow-hidden">
               {/* Visual representation of layers */}
               <div className="relative w-full h-full flex items-center justify-center">
                  <div className="absolute w-2/3 h-2/3 border-2 border-orange-500/20 rounded-full animate-[spin_20s_linear_infinite]"></div>
                  <div className="absolute w-1/2 h-1/2 border-2 border-zinc-700/30 rounded-full animate-[spin_15s_linear_infinite_reverse]"></div>
                  <div className="relative z-10 text-center">
                    <div className="text-6xl font-black text-orange-500 mb-2">CORE</div>
                    <div className="text-sm font-mono text-zinc-500 uppercase tracking-widest italic">Protected Domain</div>
                  </div>
               </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
