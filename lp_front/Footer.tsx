'use client';

import React from 'react';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-black border-t border-zinc-900 py-12">
      <div className="max-w-7xl mx-auto px-6 flex flex-col items-center">
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-white text-xl font-mono font-black tracking-tighter uppercase">coda</span>
          <div className="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
        </div>
        
        <p className="text-zinc-500 text-sm font-mono text-center">
          {currentYear} • Plataforma de Tráfego Omnichannel Open Source
        </p>
        <p className="text-zinc-600 text-xs mt-2">
          Desenvolvido por <span className="text-zinc-400">William Reis - Coda</span>
        </p>
      </div>
    </footer>
  );
};
