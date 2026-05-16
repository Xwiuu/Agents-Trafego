'use client';

import React, { useState, useEffect } from 'react';
import { SettingsVault } from './components/vault/SettingsVault';
import { DashboardOperator } from './components/dashboard/DashboardOperator';
import { WifiOff, Loader2, ShieldAlert } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null);
  const [isVaultConfigured, setIsVaultConfigured] = useState<boolean>(false);
  const [isChecking, setIsChecking] = useState(true);

  const checkStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/health`, { cache: 'no-store' });
      if (res.ok) {
        setIsBackendOnline(true);
        // Check vault status
        const settingsRes = await fetch(`${API_URL}/api/settings`);
        if (settingsRes.ok) {
          const status = await settingsRes.json();
          setIsVaultConfigured(status.is_fully_configured);
        } else {
          // Se o backend retornar erro (ex: 401 ou 500), bloqueia o acesso
          setIsVaultConfigured(false);
        }
      } else {
        setIsBackendOnline(false);
        setIsVaultConfigured(false);
      }
    } catch (err) {
      setIsBackendOnline(false);
      setIsVaultConfigured(false);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSetupComplete = () => {
    setIsVaultConfigured(true);
  };

  if (isChecking) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 text-orange-500 animate-spin mx-auto" />
          <p className="text-zinc-500 font-mono text-sm tracking-widest uppercase">Initializing Tactical Link...</p>
        </div>
      </div>
    );
  }

  if (isBackendOnline === false) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-6 text-center">
        <div className="max-w-md space-y-6">
          <div className="w-20 h-20 bg-red-500/10 border border-red-500/30 rounded-full flex items-center justify-center mx-auto text-red-500">
            <WifiOff size={40} />
          </div>
          <h2 className="text-2xl font-black uppercase tracking-tighter">Conexão Perdida</h2>
          <p className="text-zinc-400 font-mono text-sm">
            O Cérebro (Python API) não foi detectado. <br />
            Certifique-se de que o backend está rodando em <span className="text-white">{API_URL}</span>.
          </p>
          <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-lg text-left">
            <code className="text-xs text-orange-500 font-mono">python main.py</code>
          </div>
        </div>
      </div>
    );
  }

  // SPA Routing: If not configured, lock user in SettingsVault
  if (!isVaultConfigured) {
    return (
      <div className="min-h-screen bg-zinc-950 relative overflow-hidden">
        {/* Security Overlay Background */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(249,115,22,0.05)_0%,transparent_70%)] pointer-events-none" />
        
        <div className="relative z-10">
          <div className="pt-12 px-6 flex flex-col items-center">
            <div className="flex items-center space-x-3 mb-8 bg-red-500/10 border border-red-500/20 px-4 py-2 rounded-full text-red-500">
              <ShieldAlert size={16} />
              <span className="text-[10px] font-mono font-black uppercase tracking-widest">Acesso Restrito: Configuração Obrigatória</span>
            </div>
          </div>
          <SettingsVault onSetupComplete={handleSetupComplete} onBack={() => {}} />
        </div>
      </div>
    );
  }

  // If everything is OK, render the Operator Dashboard
  return <DashboardOperator />;
}
