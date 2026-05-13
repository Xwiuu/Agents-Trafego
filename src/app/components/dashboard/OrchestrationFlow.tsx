'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Server, Database, TrendingUp, BrainCircuit, ArrowRight } from 'lucide-react';

interface NodeProps {
  id: string;
  label: string;
  icon: React.ReactNode;
  isActive: boolean;
}

const Node: React.FC<NodeProps> = ({ label, icon, isActive }) => {
  return (
    <div className="relative flex flex-col items-center">
      <motion.div
        animate={{
          scale: isActive ? 1.1 : 1,
          borderColor: isActive ? 'rgba(249, 115, 22, 0.5)' : 'rgba(39, 39, 42, 1)',
          boxShadow: isActive ? '0 0 20px rgba(249, 115, 22, 0.3)' : 'none',
        }}
        className={`w-20 h-20 rounded-2xl bg-zinc-900 border-2 flex items-center justify-center transition-colors duration-500 z-10 ${
          isActive ? 'text-orange-500' : 'text-zinc-600'
        }`}
      >
        {icon}
        {isActive && (
          <motion.div
            layoutId="glow"
            className="absolute inset-0 rounded-2xl bg-orange-500/20 blur-xl"
            initial={false}
            animate={{ opacity: [0.5, 0.8, 0.5] }}
            transition={{ repeat: Infinity, duration: 2 }}
          />
        )}
      </motion.div>
      <span className={`mt-3 font-mono text-[10px] font-bold tracking-widest uppercase ${isActive ? 'text-orange-500' : 'text-zinc-500'}`}>
        {label}
      </span>
    </div>
  );
};

interface OrchestrationFlowProps {
  activeNode: string;
}

export const OrchestrationFlow: React.FC<OrchestrationFlowProps> = ({ activeNode = 'Router' }) => {
  const nodes = [
    { id: 'Router', label: 'Router', icon: <Server size={32} /> },
    { id: 'Research', label: 'Research', icon: <Database size={32} /> },
    { id: 'Analyzer', label: 'Analyzer', icon: <TrendingUp size={32} /> },
    { id: 'Memory', label: 'Memory', icon: <BrainCircuit size={32} /> },
  ];

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-10 flex flex-col items-center justify-center overflow-hidden">
      <div className="w-full flex items-center justify-between max-w-2xl relative">
        {/* Connection Lines Background */}
        <div className="absolute top-10 left-10 right-10 h-0.5 bg-zinc-800 -z-0"></div>
        
        {/* Active Line Progress */}
        <div className="absolute top-10 left-10 right-10 h-0.5 -z-0 overflow-hidden">
            <motion.div 
                className="h-full bg-gradient-to-r from-transparent via-orange-500 to-transparent w-40"
                animate={{ 
                    left: ['-20%', '120%'] 
                }}
                transition={{ 
                    repeat: Infinity, 
                    duration: 3, 
                    ease: "linear" 
                }}
                style={{ position: 'absolute' }}
            />
        </div>

        {nodes.map((node, i) => (
          <React.Fragment key={node.id}>
            <Node 
              id={node.id} 
              label={node.label} 
              icon={node.icon} 
              isActive={activeNode === node.id} 
            />
          </React.Fragment>
        ))}
      </div>

      <div className="mt-12 flex items-center space-x-4 bg-zinc-950/50 px-6 py-3 rounded-full border border-zinc-800/50">
        <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
            <span className="text-[10px] font-mono font-bold text-zinc-400 uppercase tracking-widest">Active Agent:</span>
        </div>
        <AnimatePresence mode="wait">
          <motion.span
            key={activeNode}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="text-[10px] font-mono font-black text-orange-500 uppercase tracking-widest"
          >
            {activeNode}
          </motion.span>
        </AnimatePresence>
      </div>
    </div>
  );
};
