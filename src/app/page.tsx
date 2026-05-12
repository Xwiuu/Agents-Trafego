'use client';

import React, { useState, useEffect } from 'react';
import { HubScreen } from './components/hub/HubScreen';
import { TerminalChat } from './components/terminal/TerminalChat';
import { SettingsVault } from './components/vault/SettingsVault';
import { DashboardOrchestration } from './components/dashboard/DashboardOrchestration';
import { Navbar } from './components/Navbar';

type View = 'hub' | 'setup' | 'terminal' | 'dashboard';

export default function Home() {
  const [view, setView] = useState<View>('hub');

  const handleOpenTerminal = () => setView('terminal');
  const handleOpenDashboard = () => setView('dashboard');
  const handleOpenHub = () => setView('hub');
  const handleSetupComplete = () => setView('dashboard');
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
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      <Navbar onHome={handleOpenHub} onDashboard={handleOpenDashboard} onVault={handleOpenVault} />
      <main className={view === 'hub' ? '' : 'pt-16'}>
        {renderView()}
      </main>
    </div>
  );
}
