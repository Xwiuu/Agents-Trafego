'use client';

import React from 'react';
import { Github, LayoutDashboard, Terminal, Shield } from 'lucide-react';

interface NavbarProps {
  onHome: () => void;
  onDashboard: () => void;
  onVault: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onHome, onDashboard, onVault }) => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-black/60 backdrop-blur-md border-b border-zinc-800">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <button onClick={onHome} className="flex items-center space-x-2 group">
          <span className="text-white text-2xl font-mono font-black tracking-tighter uppercase group-hover:text-orange-500 transition-colors">coda</span>
          <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
        </button>

        <div className="flex items-center space-x-6">
          <button
            onClick={onDashboard}
            className="flex items-center space-x-2 text-zinc-400 hover:text-orange-500 transition-colors duration-300 group"
          >
            <LayoutDashboard size={20} className="group-hover:scale-110 transition-transform" />
            <span className="text-sm font-medium hidden sm:inline">Dashboard</span>
          </button>
          
          <button
            onClick={onVault}
            className="flex items-center space-x-2 text-zinc-400 hover:text-orange-500 transition-colors duration-300 group"
          >
            <Shield size={20} className="group-hover:scale-110 transition-transform" />
            <span className="text-sm font-medium hidden sm:inline">Vault</span>
          </button>

          <a
            href="https://github.com/william-reis/traffic-agents"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 text-zinc-400 hover:text-orange-500 transition-colors duration-300 group"
          >
            <Github size={20} className="group-hover:scale-110 transition-transform" />
            <span className="text-sm font-medium hidden sm:inline">Contribua no GitHub</span>
          </a>
        </div>
      </div>
    </nav>
  );
};
