'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Activity, Cpu, Database, Globe, Play, Pause, RotateCcw, Terminal, Zap, Server, Clock, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';
import gsap from 'gsap';

interface AgentStatus {
  name: string;
  status: 'online' | 'offline' | 'processing' | 'warning';
  lastPing: string;
  activeTasks: number;
  icon: React.ReactNode;
}

interface SystemMetrics {
  apiCalls: number;
  memoryUsage: number;
  activeAgents: number;
  uptime: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const AGENTS: AgentStatus[] = [
  { name: 'Router', status: 'online', lastPing: '2s ago', activeTasks: 0, icon: <Server size={16} /> },
  { name: 'Research', status: 'online', lastPing: '5s ago', activeTasks: 0, icon: <Database size={16} /> },
  { name: 'Analyzer', status: 'online', lastPing: '1s ago', activeTasks: 0, icon: <TrendingUp size={16} /> },
  { name: 'Strategist', status: 'online', lastPing: '3s ago', activeTasks: 0, icon: <Zap size={16} /> },
  { name: 'MemoryKeeper', status: 'online', lastPing: '7s ago', activeTasks: 0, icon: <Database size={16} /> },
];

interface DashboardProps {
  onOpenTerminal: () => void;
}

export const DashboardOrchestration: React.FC<DashboardProps> = ({ onOpenTerminal }) => {
  const [agents, setAgents] = useState<AgentStatus[]>(AGENTS);
  const [metrics, setMetrics] = useState<SystemMetrics>({
    apiCalls: 1247,
    memoryUsage: 42,
    activeAgents: 5,
    uptime: '2d 14h',
  });
  const [logs, setLogs] = useState<string[]>([
    '[SYS] Router online, awaiting commands...',
    '[SYS] MemoryKeeper loaded with ChromaDB v1.4',
    '[SYS] Meta API client initialized',
  ]);
  const [isAutoRefresh, setIsAutoRefresh] = useState(false);
  const dashboardRef = useRef<HTMLDivElement>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (dashboardRef.current) {
      gsap.fromTo(
        '.dash-section',
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.6, stagger: 0.1, ease: 'power3.out' }
      );
    }
  }, []);

  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isAutoRefresh) {
      interval = setInterval(() => {
        // Simulate metrics updates
        setMetrics((prev) => ({
          ...prev,
          apiCalls: prev.apiCalls + Math.floor(Math.random() * 5),
          memoryUsage: Math.min(100, Math.max(30, prev.memoryUsage + (Math.random() - 0.5) * 2)),
        }));
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [isAutoRefresh]);

  const handleResetMemory = () => {
    setLogs((prev) => [...prev, `[SYS] Memory Keeper reset initiated...`, `[SYS] ChromaDB collection cleared.`]);
  };

  const getStatusColor = (status: AgentStatus['status']) => {
    switch (status) {
      case 'online':
        return 'text-emerald-400';
      case 'processing':
        return 'text-orange-400';
      case 'warning':
        return 'text-yellow-400';
      default:
        return 'text-red-400';
    }
  };

  const getStatusDot = (status: AgentStatus['status']) => {
    switch (status) {
      case 'online':
        return 'bg-emerald-400 animate-pulse';
      case 'processing':
        return 'bg-orange-400 animate-pulse';
      case 'warning':
        return 'bg-yellow-400';
      default:
        return 'bg-red-400';
    }
  };

  return (
    <div ref={dashboardRef} className="min-h-screen bg-zinc-950 text-white p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-zinc-900 border border-zinc-800 rounded-xl flex items-center justify-center">
              <Activity size={24} className="text-orange-500" />
            </div>
            <div>
              <h1 className="text-2xl font-black tracking-tight">ORQUESTRAÇÃO</h1>
              <p className="text-zinc-400 font-mono text-xs tracking-widest uppercase">Painel de Controle do Esquadrão</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsAutoRefresh(!isAutoRefresh)}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg border font-mono text-xs font-bold tracking-wider uppercase transition-all ${
                isAutoRefresh
                  ? 'bg-orange-500 border-orange-500 text-black'
                  : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-white'
              }`}
            >
              {isAutoRefresh ? <Pause size={14} /> : <Play size={14} />}
              <span>{isAutoRefresh ? 'Monitorando' : 'Monitorar'}</span>
            </button>
            <button
              onClick={onOpenTerminal}
              className="flex items-center space-x-2 px-4 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white hover:border-orange-500/50 font-mono text-xs font-bold tracking-wider uppercase transition-all"
            >
              <Terminal size={14} />
              <span>Terminal</span>
            </button>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { label: 'API Calls', value: metrics.apiCalls.toLocaleString(), icon: <Globe size={18} />, color: 'text-orange-500' },
            { label: 'Memória Used', value: `${metrics.memoryUsage.toFixed(1)}%`, icon: <Cpu size={18} />, color: 'text-emerald-500' },
            { label: 'Agentes Ativos', value: metrics.activeAgents, icon: <CheckCircle2 size={18} />, color: 'text-blue-500' },
            { label: 'Uptime', value: metrics.uptime, icon: <Clock size={18} />, color: 'text-purple-500' },
          ].map((metric, i) => (
            <div
              key={i}
              className="dash-section bg-zinc-900/50 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider">{metric.label}</span>
                <span className={`${metric.color}`}>{metric.icon}</span>
              </div>
              <div className="text-2xl font-black">{metric.value}</div>
            </div>
          ))}
        </div>

        {/* Agents + Logs */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Agent Status */}
          <div className="lg:col-span-2 space-y-6">
            <div className="dash-section bg-zinc-900/50 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-sm font-mono font-bold tracking-widest uppercase text-orange-500">Status dos Agentes</h2>
                <button
                  onClick={handleResetMemory}
                  className="flex items-center space-x-2 text-xs font-mono font-bold text-zinc-400 hover:text-orange-500 transition-colors uppercase tracking-wider"
                >
                  <RotateCcw size={12} />
                  <span>Reset Memory</span>
                </button>
              </div>
              <div className="space-y-3">
                {agents.map((agent, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-4 bg-zinc-950/50 rounded-xl border border-zinc-800/50 hover:border-zinc-700 transition-all group"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-zinc-800 rounded-lg flex items-center justify-center text-zinc-400 group-hover:text-orange-500 transition-colors">{agent.icon}</div>
                      <div>
                        <div className="font-bold text-sm">{agent.name}</div>
                        <div className="text-xs text-zinc-500 font-mono">{agent.activeTasks} tasks active</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className="text-xs font-mono text-zinc-500">{agent.lastPing}</span>
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${getStatusDot(agent.status)}`} />
                        <span className={`text-xs font-mono font-bold ${getStatusColor(agent.status)} uppercase`}>{agent.status}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* System Logs */}
          <div className="dash-section bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 flex flex-col h-full min-h-[400px]">
            <h2 className="text-sm font-mono font-bold tracking-widest uppercase text-orange-500 mb-4">System Logs</h2>
            <div className="flex-1 overflow-y-auto font-mono text-xs space-y-2 pr-2 custom-scrollbar">
              {logs.map((log, i) => (
                <div key={i} className="flex items-start space-x-2 text-zinc-400">
                  <span className="text-zinc-600 shrink-0">{new Date().toISOString().split('T')[1].split('.')[0]}</span>
                  <span
                    className={
                      log.includes('ERROR')
                        ? 'text-red-400'
                        : log.includes('WARN')
                        ? 'text-yellow-400'
                        : 'text-zinc-300'
                    }
                  >
                    {log}
                  </span>
                </div>
              ))}
              <div ref={logEndRef} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
