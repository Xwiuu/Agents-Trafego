'use client';

import React, { useEffect, useRef, useState } from 'react';
import { 
  Activity, 
  Terminal as TerminalIcon, 
  TrendingUp, 
  DollarSign, 
  Target, 
  Zap,
  Cpu,
  Database,
  BrainCircuit,
  Server,
  Clock,
  ShieldAlert,
  AlertTriangle
} from 'lucide-react';
import gsap from 'gsap';
import { TerminalChat } from '../terminal/TerminalChat';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface AuditLog {
  timestamp: string;
  action: string;
  campaign_id: string;
  reason: string;
}

const KPI_DATA = [
  { label: 'Gasto do Dia', value: '1,450.00', icon: <DollarSign size={20} />, suffix: 'BRL', color: 'text-orange-500' },
  { label: 'ROAS Global', value: '4.2', icon: <TrendingUp size={20} />, suffix: 'x', color: 'text-emerald-500' },
  { label: 'CPA Médio', value: '12.40', icon: <Target size={20} />, suffix: 'BRL', color: 'text-blue-500' },
  { label: 'Campanhas Ativas', value: '12', icon: <Zap size={20} />, suffix: '', color: 'text-purple-500' },
];

const AGENTS = [
  { id: 'router', name: 'Router', icon: <Server size={14} /> },
  { id: 'research', name: 'Research', icon: <Database size={14} /> },
  { id: 'analyzer', name: 'Analyzer', icon: <TrendingUp size={14} /> },
  { id: 'operator', name: 'Operator', icon: <Cpu size={14} /> },
  { id: 'memory', name: 'Memory', icon: <BrainCircuit size={14} /> },
];

const MorningReport: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await fetch(`${API_URL}/api/audit-logs`);
        if (res.ok) {
          const data = await res.json();
          setLogs(data);
        }
      } catch (err) {
        console.error("Erro ao buscar logs de auditoria:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 30000); // Atualiza a cada 30s
    return () => clearInterval(interval);
  }, []);

  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    } catch {
      return "--:--";
    }
  };

  return (
    <div className="bg-zinc-900/40 border border-zinc-800/50 rounded-2xl flex flex-col h-full overflow-hidden backdrop-blur-md shadow-lg shadow-black/50">
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/40">
        <div className="flex items-center space-x-2">
          <Clock size={16} className="text-orange-500" />
          <h2 className="text-xs font-mono font-bold uppercase tracking-widest text-zinc-300">Relatório Matinal</h2>
        </div>
        <div className="px-2 py-0.5 rounded-full bg-orange-500/10 border border-orange-500/20 text-[9px] font-mono text-orange-500 uppercase font-bold tracking-tighter">
          Histórico Autônomo
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
        {isLoading ? (
          <div className="flex items-center justify-center h-full text-zinc-600 font-mono text-[10px] animate-pulse">
            Sincronizando registros...
          </div>
        ) : logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full space-y-2 opacity-30 grayscale py-10">
             <ShieldAlert size={32} />
             <span className="text-[10px] font-mono uppercase tracking-widest text-center">Nenhuma ação autônoma<br/>nas últimas 24h</span>
          </div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="group relative flex items-start space-x-3 p-3 rounded-xl bg-zinc-950/50 border border-zinc-800/30 hover:border-orange-500/30 transition-all duration-300 shadow-sm">
              <div className={`mt-1 w-8 h-8 rounded-lg flex items-center justify-center border ${
                log.action === 'Pausa' ? 'bg-red-500/10 border-red-500/20 text-red-500' :
                log.action === 'Escala' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500' :
                'bg-orange-500/10 border-orange-500/20 text-orange-500'
              }`}>
                {log.action === 'Pausa' ? <AlertTriangle size={16} /> : 
                 log.action === 'Escala' ? <TrendingUp size={16} /> : 
                 <ShieldAlert size={16} />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-[10px] font-mono font-bold text-zinc-200 uppercase tracking-tight truncate">
                    {log.action === 'Pausa' ? 'Campanha Pausada' : log.action === 'Escala' ? 'Recomendação de Escala' : log.action}
                  </span>
                  <span className="text-[9px] font-mono text-zinc-500">{formatTime(log.timestamp)}</span>
                </div>
                <p className="text-[10px] text-zinc-500 font-mono truncate mb-1">ID: {log.campaign_id}</p>
                <div className="text-[9px] font-mono text-orange-500/70 italic flex items-center space-x-1">
                  <Activity size={10} />
                  <span>Motivo: {log.reason}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export const DashboardOperator: React.FC = () => {
  const [activeAgent, setActiveAgent] = useState<string>('router');
  const kpiRefs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    // GSAP Animation for KPIs
    kpiRefs.current.forEach((ref, i) => {
      if (ref) {
        const valueElement = ref.querySelector('.kpi-value');
        if (valueElement) {
          const targetValue = parseFloat(valueElement.getAttribute('data-value') || '0');
          const obj = { val: 0 };
          gsap.to(obj, {
            val: targetValue,
            duration: 1.5,
            delay: i * 0.1,
            ease: 'power3.out',
            onUpdate: () => {
              valueElement.textContent = obj.val.toLocaleString('pt-BR', {
                minimumFractionDigits: targetValue % 1 === 0 ? 0 : 2,
                maximumFractionDigits: 2,
              });
            },
          });
        }
        gsap.from(ref, {
          y: 20,
          opacity: 0,
          duration: 0.6,
          delay: i * 0.1,
          ease: 'power2.out'
        });
      }
    });

    // Simulação de pulso de agentes
    const interval = setInterval(() => {
      const randomAgent = AGENTS[Math.floor(Math.random() * AGENTS.length)].id;
      setActiveAgent(randomAgent);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-zinc-950 text-white flex flex-col overflow-hidden">
      {/* Top Header / KPI Bar */}
      <header className="border-b border-zinc-900 bg-zinc-950/50 backdrop-blur-xl p-4 z-20">
        <div className="max-w-[1600px] mx-auto flex flex-col lg:flex-row items-center justify-between gap-6">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-orange-500/10 border border-orange-500/20 rounded-lg flex items-center justify-center">
              <Activity className="text-orange-500 animate-pulse" size={24} />
            </div>
            <div>
              <h1 className="text-lg font-black tracking-tighter uppercase">Command Center 2.0</h1>
              <div className="flex items-center space-x-2">
                <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                <span className="text-[10px] font-mono text-emerald-500 uppercase font-bold tracking-widest">System Online</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 flex-1 max-w-4xl">
            {KPI_DATA.map((kpi, i) => (
              <div 
                key={i}
                ref={(el) => { kpiRefs.current[i] = el; }}
                className="bg-zinc-900/40 border border-zinc-800/50 p-3 rounded-xl flex flex-col shadow-sm"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider">{kpi.label}</span>
                  <span className={kpi.color}>{kpi.icon}</span>
                </div>
                <div className="flex items-baseline space-x-1">
                  <span 
                    className="text-xl font-black kpi-value" 
                    data-value={kpi.value.replace(',', '')}
                  >
                    0
                  </span>
                  <span className="text-[10px] font-mono text-zinc-500">{kpi.suffix}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Squad Status Widget */}
          <div className="flex items-center bg-zinc-900/60 border border-zinc-800 px-4 py-2 rounded-full space-x-4">
            <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-[0.2em]">Squad:</span>
            <div className="flex space-x-2">
              {AGENTS.map((agent) => (
                <div 
                  key={agent.id}
                  title={agent.name}
                  className={`w-7 h-7 rounded-full flex items-center justify-center border transition-all duration-500 ${
                    activeAgent === agent.id 
                      ? 'bg-orange-500 border-orange-400 text-black scale-110 shadow-[0_0_15px_rgba(249,115,22,0.4)]' 
                      : 'bg-zinc-800 border-zinc-700 text-zinc-500 opacity-50'
                  }`}
                >
                  {agent.icon}
                </div>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Main Operational Area */}
      <main className="flex-1 relative flex overflow-hidden">
        {/* Background Grid Decoration */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#18181b_1px,transparent_1px),linear-gradient(to_bottom,#18181b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

        <div className="relative z-10 w-full flex items-stretch p-4 gap-4">
          {/* Main Terminal Area */}
          <div className="flex-[2] bg-black/40 border border-zinc-800/50 rounded-2xl overflow-hidden backdrop-blur-sm shadow-2xl shadow-orange-500/5 flex flex-col">
            <div className="h-8 bg-zinc-900/80 border-b border-zinc-800 px-4 flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-red-500/20 border border-red-500/40" />
              <div className="w-2 h-2 rounded-full bg-yellow-500/20 border border-yellow-500/40" />
              <div className="w-2 h-2 rounded-full bg-green-500/20 border border-green-500/40" />
              <div className="flex-1 text-center">
                <span className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest italic"> LangGraph-Ads-Orchestrator_v2.0_stable</span>
              </div>
              <TerminalIcon size={12} className="text-zinc-600" />
            </div>
            
            <div className="flex-1 overflow-hidden">
              <TerminalChat />
            </div>
          </div>

          {/* Audit Log Sidebar */}
          <div className="flex-1 max-w-md hidden xl:flex flex-col">
            <MorningReport />
          </div>
        </div>
      </main>

      {/* Footer Info */}
      <footer className="h-8 border-t border-zinc-900 bg-zinc-950 px-6 flex items-center justify-between text-[9px] font-mono text-zinc-600 uppercase tracking-widest">
        <div className="flex items-center space-x-4">
          <span>Local Node: 127.0.0.1</span>
          <span className="text-orange-500/50">●</span>
          <span>Latency: 24ms</span>
        </div>
        <div className="flex items-center space-x-4">
          <span>Groq Llama-3-70b-Versatile</span>
          <span className="text-orange-500/50">●</span>
          <span>© 2026 Meta Ads Agent</span>
        </div>
      </footer>
    </div>
  );
};
