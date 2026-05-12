'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface Agent {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  color: string;
}

const agents: Agent[] = [
  { id: 'router', name: 'Router', status: 'active', color: 'text-green-400' },
  { id: 'meta', name: 'Meta', status: 'inactive', color: 'text-blue-400' },
  { id: 'google', name: 'Google', status: 'inactive', color: 'text-red-400' },
  { id: 'tiktok', name: 'TikTok', status: 'inactive', color: 'text-pink-400' },
  { id: 'linkedin', name: 'LinkedIn', status: 'inactive', color: 'text-blue-300' },
  { id: 'pinterest', name: 'Pinterest', status: 'inactive', color: 'text-red-300' },
];

export const ArchitectureMap: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-zinc-950 text-white p-8">
      <h1 className="text-3xl font-bold mb-12 text-center text-green-400">Arquitetura do Sistema</h1>
      
      <div className="relative w-full max-w-4xl">
        {/* Central Router Agent */}
        <motion.div 
          className="flex justify-center mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="bg-zinc-800 border-2 border-green-500 rounded-xl p-6 shadow-lg shadow-green-500/30">
            <div className="text-2xl font-bold text-green-400">Router Agent</div>
          </div>
        </motion.div>
        
        {/* Platform Agents */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
          {agents.slice(1).map((agent, index) => (
            <motion.div
              key={agent.id}
              className="bg-zinc-800 border border-zinc-700 rounded-lg p-4 text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 * (index + 1) }}
            >
              <div className={`text-xl font-bold ${agent.color}`}>{agent.name}</div>
              <div className="text-green-400">Online</div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};