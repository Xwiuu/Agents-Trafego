'use client';

import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  BrainCircuit,
  Clock,
  Cpu,
  Database,
  DollarSign,
  FileText,
  Loader2,
  Lock,
  Server,
  ShieldAlert,
  Target,
  Terminal as TerminalIcon,
  TrendingUp,
} from 'lucide-react';
import { TerminalChat } from '../terminal/TerminalChat';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type TabId = 'performance' | 'command' | 'audit';

interface AuditLog {
  timestamp: string;
  action: string;
  campaign_id: string;
  reason: string;
}

interface CampaignMetric {
  id: string;
  name: string;
  status: string;
  spend: number;
  conversions: number;
  cpa: number | null;
  roas: number;
}

interface MetricsResponse {
  date_preset: string;
  totals: {
    total_spend: number;
    total_conversions: number;
    average_cpa: number | null;
    overall_roas: number;
  };
  top_campaigns: CampaignMetric[];
}

const EMPTY_METRICS: MetricsResponse = {
  date_preset: 'last_7d',
  totals: {
    total_spend: 0,
    total_conversions: 0,
    average_cpa: null,
    overall_roas: 0,
  },
  top_campaigns: [],
};

const AGENTS = [
  { id: 'router', name: 'Router', icon: <Server size={14} /> },
  { id: 'research', name: 'Research', icon: <Database size={14} /> },
  { id: 'analyzer', name: 'Analyzer', icon: <TrendingUp size={14} /> },
  { id: 'operator', name: 'Operator', icon: <Cpu size={14} /> },
  { id: 'memory', name: 'Memory', icon: <BrainCircuit size={14} /> },
];

const TABS: Array<{ id: TabId; label: string; icon: React.ReactNode }> = [
  { id: 'performance', label: 'Dashboard de Performance', icon: <BarChart3 size={16} /> },
  { id: 'command', label: 'Command Center', icon: <TerminalIcon size={16} /> },
  { id: 'audit', label: 'Audit Log', icon: <FileText size={16} /> },
];

const formatCurrency = (value: number | null | undefined) => {
  if (value === null || value === undefined) return '--';

  return value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

const formatNumber = (value: number) => value.toLocaleString('pt-BR');

const formatRoas = (value: number | null | undefined) => {
  if (value === null || value === undefined) return '--';
  return `${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}x`;
};

const isActiveStatus = (status: string) => status.toUpperCase() === 'ACTIVE';

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
        console.error('Erro ao buscar logs de auditoria:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '--:--';
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
            <span className="text-[10px] font-mono uppercase tracking-widest text-center">Nenhuma ação autônoma<br />nas últimas 24h</span>
          </div>
        ) : (
          logs.map((log, i) => (
            <div key={`${log.timestamp}-${i}`} className="group relative flex items-start space-x-3 p-3 rounded-xl bg-zinc-950/50 border border-zinc-800/30 hover:border-orange-500/30 transition-all duration-300 shadow-sm">
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

const MetricCard: React.FC<{
  label: string;
  value: string;
  icon: React.ReactNode;
  tone: string;
}> = ({ label, value, icon, tone }) => (
  <div className="bg-zinc-900/70 border border-zinc-800 p-5 rounded-xl shadow-sm min-h-[132px] flex flex-col justify-between">
    <div className="flex items-center justify-between">
      <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">{label}</span>
      <span className={tone}>{icon}</span>
    </div>
    <div className="text-2xl font-black tracking-tight text-zinc-50 break-words">{value}</div>
  </div>
);

const PerformanceDashboard: React.FC<{
  metrics: MetricsResponse;
  isLoading: boolean;
  error: string | null;
}> = ({ metrics, isLoading, error }) => {
  const cards = useMemo(() => [
    {
      label: 'Investimento Total',
      value: formatCurrency(metrics.totals.total_spend),
      icon: <DollarSign size={20} />,
      tone: 'text-orange-500',
    },
    {
      label: 'Conversões',
      value: formatNumber(metrics.totals.total_conversions),
      icon: <Target size={20} />,
      tone: 'text-emerald-500',
    },
    {
      label: 'CPA Médio',
      value: formatCurrency(metrics.totals.average_cpa),
      icon: <Activity size={20} />,
      tone: 'text-blue-500',
    },
    {
      label: 'ROAS Geral',
      value: formatRoas(metrics.totals.overall_roas),
      icon: <TrendingUp size={20} />,
      tone: 'text-purple-500',
    },
  ], [metrics]);

  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6 custom-scrollbar">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 className="text-xl font-black tracking-tight uppercase">Dashboard de Performance</h2>
          <p className="text-xs font-mono text-zinc-500 uppercase tracking-widest">Meta Ads - últimos 7 dias</p>
        </div>
        {isLoading && (
          <div className="flex items-center gap-2 text-[10px] font-mono text-orange-500 uppercase tracking-widest">
            <Loader2 size={14} className="animate-spin" />
            Carregando métricas
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-3 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">
          <AlertTriangle size={18} className="text-red-400 flex-shrink-0" />
          <span className="font-mono text-xs">{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {cards.map((card) => (
          <MetricCard key={card.label} {...card} />
        ))}
      </div>

      <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl overflow-hidden shadow-2xl shadow-black/40">
        <div className="px-5 py-4 border-b border-zinc-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-zinc-200 uppercase tracking-wider">Top 10 campanhas</h3>
            <p className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">Ordenadas por gasto no período</p>
          </div>
          <BarChart3 size={18} className="text-zinc-600" />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-left">
            <thead className="bg-zinc-950/60 text-[10px] font-mono uppercase tracking-widest text-zinc-500">
              <tr>
                <th className="px-5 py-3 font-semibold">Nome</th>
                <th className="px-5 py-3 font-semibold">Status</th>
                <th className="px-5 py-3 font-semibold text-right">Gasto</th>
                <th className="px-5 py-3 font-semibold text-right">ROAS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/70">
              {metrics.top_campaigns.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-5 py-12 text-center text-xs font-mono uppercase tracking-widest text-zinc-600">
                    Nenhuma campanha encontrada no período
                  </td>
                </tr>
              ) : (
                metrics.top_campaigns.map((campaign) => (
                  <tr key={campaign.id} className="hover:bg-zinc-800/30 transition-colors">
                    <td className="px-5 py-4">
                      <div className="font-semibold text-sm text-zinc-100 truncate max-w-[420px]">{campaign.name}</div>
                      <div className="text-[10px] font-mono text-zinc-600">ID: {campaign.id}</div>
                    </td>
                    <td className="px-5 py-4">
                      <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[10px] font-mono font-bold uppercase tracking-wider ${
                        isActiveStatus(campaign.status)
                          ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                          : 'border-red-500/30 bg-red-500/10 text-red-400'
                      }`}>
                        {campaign.status}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-right font-mono text-sm text-zinc-200">{formatCurrency(campaign.spend)}</td>
                    <td className="px-5 py-4 text-right font-mono text-sm text-zinc-200">{formatRoas(campaign.roas)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const LockedPanel: React.FC = () => (
  <div className="h-full flex flex-col items-center justify-center space-y-4 p-8 text-center bg-zinc-900/20 backdrop-blur-sm rounded-2xl border border-zinc-800/60">
    <ShieldAlert size={52} className="text-orange-500 animate-pulse" />
    <div className="space-y-2">
      <h3 className="text-zinc-200 font-mono font-bold uppercase tracking-widest">Acesso Restrito</h3>
      <p className="text-zinc-500 font-mono text-xs max-w-sm mx-auto">
        Aguardando configuração de chaves válidas no Vault. As abas do hub permanecem bloqueadas pelo Gatekeeper.
      </p>
    </div>
  </div>
);

const CommandCenter: React.FC = () => (
  <div className="h-full bg-black/60 border border-zinc-800/50 rounded-2xl overflow-hidden backdrop-blur-sm shadow-2xl shadow-orange-500/5 flex flex-col">
    <div className="h-8 bg-zinc-900/80 border-b border-zinc-800 px-4 flex items-center space-x-2 flex-shrink-0">
      <div className="w-2 h-2 rounded-full bg-red-500/20 border border-red-500/40" />
      <div className="w-2 h-2 rounded-full bg-yellow-500/20 border border-yellow-500/40" />
      <div className="w-2 h-2 rounded-full bg-green-500/20 border border-green-500/40" />
      <div className="flex-1 text-center">
        <span className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest italic">LangGraph-Ads-Orchestrator_v2.0_stable</span>
      </div>
      <TerminalIcon size={12} className="text-zinc-600" />
    </div>
    <div className="flex-1 min-h-0 overflow-hidden">
      <TerminalChat />
    </div>
  </div>
);

export const DashboardOperator: React.FC = () => {
  const [activeAgent, setActiveAgent] = useState<string>('router');
  const [activeTab, setActiveTab] = useState<TabId>('performance');
  const [isConfigured, setIsConfigured] = useState<boolean | null>(null);
  const [metrics, setMetrics] = useState<MetricsResponse>(EMPTY_METRICS);
  const [isMetricsLoading, setIsMetricsLoading] = useState(true);
  const [metricsError, setMetricsError] = useState<string | null>(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`${API_URL}/api/settings`);
        if (res.ok) {
          const data = await res.json();
          setIsConfigured(Boolean(data.is_fully_configured));
        } else {
          setIsConfigured(false);
        }
      } catch {
        setIsConfigured(false);
      }
    };

    checkStatus();
  }, []);

  useEffect(() => {
    const fetchMetrics = async () => {
      if (isConfigured === null) return;

      if (!isConfigured) {
        setIsMetricsLoading(false);
        return;
      }

      setIsMetricsLoading(true);
      setMetricsError(null);

      try {
        const res = await fetch(`${API_URL}/api/metrics`, { cache: 'no-store' });
        if (!res.ok) {
          const payload = await res.json().catch(() => null);
          throw new Error(payload?.detail || 'Falha ao carregar métricas Meta.');
        }

        const data = await res.json();
        setMetrics(data);
      } catch (err: any) {
        setMetrics(EMPTY_METRICS);
        setMetricsError(err.message || 'Falha ao carregar métricas Meta.');
      } finally {
        setIsMetricsLoading(false);
      }
    };

    fetchMetrics();
  }, [isConfigured]);

  useEffect(() => {
    const interval = setInterval(() => {
      const randomAgent = AGENTS[Math.floor(Math.random() * AGENTS.length)].id;
      setActiveAgent(randomAgent);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const renderTabContent = () => {
    if (isConfigured === null) {
      return (
        <div className="h-full flex items-center justify-center rounded-2xl border border-zinc-800/60 bg-zinc-900/20">
          <div className="flex items-center gap-3 text-[10px] font-mono text-orange-500 uppercase tracking-widest">
            <Loader2 size={16} className="animate-spin" />
            Verificando Vault
          </div>
        </div>
      );
    }

    if (!isConfigured) return <LockedPanel />;

    return (
      <div className="h-full">
        <section className={activeTab === 'performance' ? 'h-full' : 'hidden'}>
          <PerformanceDashboard metrics={metrics} isLoading={isMetricsLoading} error={metricsError} />
        </section>
        <section className={activeTab === 'command' ? 'h-full' : 'hidden'}>
          <CommandCenter />
        </section>
        <section className={activeTab === 'audit' ? 'h-full' : 'hidden'}>
          <MorningReport />
        </section>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-white flex flex-col overflow-x-hidden">
      <header className="border-b border-zinc-900 bg-zinc-950/70 backdrop-blur-xl p-4 z-20 sticky top-0">
        <div className="max-w-[1600px] mx-auto flex flex-col xl:flex-row items-center justify-between gap-5">
          <div className="flex items-center space-x-4 w-full xl:w-auto">
            <div className="w-10 h-10 bg-orange-500/10 border border-orange-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <Activity className="text-orange-500 animate-pulse" size={24} />
            </div>
            <div>
              <h1 className="text-lg font-black tracking-tighter uppercase">Omnichannel Traffic AI Hub</h1>
              <div className="flex items-center space-x-2">
                <div className={`w-1.5 h-1.5 rounded-full ${isConfigured ? 'bg-emerald-500 animate-pulse' : isConfigured === false ? 'bg-red-500' : 'bg-orange-500 animate-pulse'}`} />
                <span className={`text-[10px] font-mono uppercase font-bold tracking-widest ${isConfigured ? 'text-emerald-500' : isConfigured === false ? 'text-red-400' : 'text-orange-500'}`}>
                  {isConfigured ? 'System Online' : isConfigured === false ? 'Vault Locked' : 'Checking Vault'}
                </span>
              </div>
            </div>
          </div>

          <nav className="flex w-full xl:w-auto rounded-xl border border-zinc-800 bg-zinc-900/60 p-1 overflow-x-auto">
            {TABS.map((tab) => {
              const isActive = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  type="button"
                  disabled={isConfigured !== true}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 whitespace-nowrap rounded-lg px-4 py-2 text-xs font-mono font-bold uppercase tracking-wider transition-all disabled:cursor-not-allowed disabled:opacity-45 ${
                    isActive
                      ? 'bg-orange-500 text-black shadow-[0_0_20px_rgba(249,115,22,0.2)]'
                      : 'text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100'
                  }`}
                >
                  {isConfigured !== true ? <Lock size={14} /> : tab.icon}
                  {tab.label}
                </button>
              );
            })}
          </nav>

          <div className="flex items-center bg-zinc-900/60 border border-zinc-800 px-4 py-2 rounded-full space-x-4 w-full xl:w-auto justify-center">
            <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-[0.2em]">Squad:</span>
            <div className="flex space-x-2">
              {AGENTS.map((agent) => (
                <div
                  key={agent.id}
                  title={agent.name}
                  className={`w-7 h-7 rounded-full flex items-center justify-center border transition-all duration-500 ${
                    isConfigured === true && activeAgent === agent.id
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

      <main className="flex-1 relative overflow-hidden min-h-0">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#18181b_1px,transparent_1px),linear-gradient(to_bottom,#18181b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />
        <div className="relative z-10 h-full max-w-[1600px] mx-auto p-4">
          {renderTabContent()}
        </div>
      </main>

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
