'use client';

import React, { useState, useEffect } from 'react';
import { HubScreen } from './components/hub/HubScreen';
import { TerminalChat } from './components/terminal/TerminalChat';
import { SettingsVault } from './components/vault/SettingsVault';
import { DashboardOrchestration } from './components/dashboard/DashboardOrchestration';
import { Navbar } from './components/Navbar';
import { AlertTriangle, WifiOff, Loader2 } from 'lucide-react';

type View = 'hub' | 'setup' | 'terminal' | 'dashboard';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [view, setView] = useState<View>('hub');
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null);
  const [isVaultConfigured, setIsVaultConfigured] = useState<boolean>(false);
  const [isChecking, setIsChecking] = useState(true);

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_URL}/health`, { cache: 'no-store' });
      if (res.ok) {
        setIsBackendOnline(true);
        // If backend is online, check vault status
        const settingsRes = await fetch(`${API_URL}/api/settings`);
        if (settingsRes.ok) {
          const status = await settingsRes.json();
          setIsVaultConfigured(status.is_fully_configured);
        }
      } else {
        setIsBackendOnline(false);
      }
    } catch (err) {
      setIsBackendOnline(false);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleOpenTerminal = () => setView('terminal');
  
  const handleOpenDashboard = () => {
    if (!isBackendOnline) return;
    if (!isVaultConfigured) {
      setView('setup');
    } else {
      setView('dashboard');
    }
  };

  const handleOpenHub = () => setView('hub');
  const handleSetupComplete = () => {
    setIsVaultConfigured(true);
    setView('dashboard');
  };
  const handleNeedSetup = () => setView('setup');
  const handleOpenVault = () => setView('setup');

  const renderView = () => {
    switch (view) {
      case 'terminal':
        return (
          <div className="h-[calc(100vh-64px)] bg-zinc-950 text-white flex flex-col">
            <div className="flex-1 overflow-hidden">
              <TerminalChat onBack={handleOpenDashboard} />
            </div>
          </div>
        );
      case 'setup':
        return <SettingsVault onSetupComplete={handleSetupComplete} onBack={handleOpenHub} />;
      case 'dashboard':
        return <DashboardOrchestration onOpenTerminal={handleOpenTerminal} />;
      default:
        return (
          <HubScreen 
            onOpenTerminal={handleOpenTerminal} 
            onNeedSetup={handleNeedSetup} 
            onOpenDashboard={handleOpenDashboard} 
            isBackendOffline={isBackendOnline === false}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      {/* Health Banner */}
      {isBackendOnline === false && (
        <div className="fixed top-0 left-0 right-0 z-[100] bg-red-600 text-white py-2 px-4 flex items-center justify-center space-x-3 font-mono text-sm font-bold animate-pulse">
          <WifiOff size={18} />
          <span>⚠️ Backend Offline: Inicie a API com 'python interfaces/api.py'</span>
        </div>
      )}

      <Navbar onHome={handleOpenHub} onDashboard={handleOpenDashboard} onVault={handleOpenVault} />
      
      <main className={(view === 'hub' ? '' : 'pt-16') + (isBackendOnline === false ? ' pt-10' : '')}>
        {renderView()}
      </main>

      {/* Global Overlay for Offline State when in critical views */}
      {(view === 'dashboard' || view === 'terminal') && isBackendOnline === false && (
        <div className="fixed inset-0 z-[90] bg-black/80 backdrop-blur-md flex items-center justify-center p-6 text-center">
          <div className="max-w-md space-y-6">
            <div className="w-20 h-20 bg-red-500/10 border border-red-500/30 rounded-full flex items-center justify-center mx-auto text-red-500">
              <AlertTriangle size={40} />
            </div>
            <h2 className="text-2xl font-black">CONEXÃO PERDIDA</h2>
            <p className="text-zinc-400 font-mono text-sm">
              O link com o Cérebro (Python API) foi interrompido. Reestabeleça a conexão para continuar a orquestração.
            </p>
            <button 
              onClick={() => setView('hub')}
              className="px-8 py-3 bg-white text-black font-bold rounded-lg hover:bg-zinc-200 transition-colors"
            >
              Voltar ao Hub
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
