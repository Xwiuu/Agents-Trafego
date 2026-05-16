'use client';

import React from 'react';
import { Navbar } from '../Navbar';
import { HubScreen } from '../hub/HubScreen';
import { Footer } from '../Footer';

export default function Home() {
  const handleRedirectToApp = () => {
    // Redireciona para o Dashboard principal se configurado, ou apenas loga
    const appUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';
    window.location.href = appUrl;
  };

  return (
    <main className="min-h-screen">
      <Navbar 
        onHome={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        onDashboard={handleRedirectToApp}
        onVault={handleRedirectToApp}
      />
      <HubScreen 
        onOpenTerminal={handleRedirectToApp}
        onNeedSetup={handleRedirectToApp}
        onOpenDashboard={handleRedirectToApp}
      />
      <Footer />
    </main>
  );
}
