'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Terminal, ArrowLeft, Loader2 } from 'lucide-react';
import gsap from 'gsap';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'system';
  timestamp: Date;
}

interface TerminalChatProps {
  onBack: () => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const TerminalChat: React.FC<TerminalChatProps> = ({ onBack }) => {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: '📡 [Capitão Router] Inicializando sistema multi-agente...', sender: 'system', timestamp: new Date() },
    { id: 2, text: '✅ [System] Ecossistema pronto. Aguardando comandos.', sender: 'system', timestamp: new Date() },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      gsap.fromTo(
        '.message-line',
        { opacity: 0, x: -20 },
        { opacity: 1, x: 0, duration: 0.5, stagger: 0.1, ease: 'power2.out' }
      );
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() === '') return;

    const userMsg: Message = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          sender: 'user',
        }),
      });

      if (!res.ok) {
        throw new Error('Erro ao comunicar com o backend');
      }

      const data = await res.json();

      const botMsg: Message = {
        id: Date.now() + 1,
        text: data.response || 'Nenhuma resposta do agente.',
        sender: 'system',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: Date.now() + 1,
        text: `❌ [Erro] ${err.message}`,
        sender: 'system',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-black">
      <div className="flex items-center justify-between px-6 py-3 border-b border-zinc-900 bg-zinc-950/50">
        <div className="flex items-center space-x-4">
          <button onClick={onBack} className="flex items-center text-zinc-400 hover:text-orange-500 transition-colors">
            <ArrowLeft size={16} />
          </button>
          <div className="flex items-center space-x-2">
            <Terminal size={16} className="text-orange-500" />
            <span className="text-xs font-mono text-zinc-400 uppercase tracking-widest">Neural Terminal v1.0.4</span>
          </div>
        </div>
        <div className="flex space-x-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-zinc-800"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-zinc-800"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-orange-500/50"></div>
        </div>
      </div>

      <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-6 font-mono text-sm space-y-4">
        {messages.map((message) => (
          <div key={message.id} className="message-line">
            <div className="flex items-start space-x-3">
              <span
                className={`mt-1 text-[10px] px-1.5 py-0.5 rounded uppercase font-bold ${
                  message.sender === 'user' ? 'bg-orange-500 text-black' : 'bg-zinc-800 text-zinc-400'
                }`}
              >
                {message.sender === 'user' ? 'USR' : 'SYS'}
              </span>
              <div
                className={`${
                  message.sender === 'user' ? 'text-white' : 'text-orange-500/80'
                } leading-relaxed max-w-4xl`}
              >
                {message.text}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex items-center space-x-2 text-zinc-500 text-xs">
            <Loader2 size={14} className="animate-spin" />
            <span>Processando com Groq (Llama 3)...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-6 bg-zinc-950 border-t border-zinc-900">
        <div className="relative flex items-center">
          <span className="absolute left-4 text-orange-500 font-bold">$</span>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            className="w-full bg-zinc-900/50 text-white pl-10 pr-12 py-4 rounded-xl border border-zinc-800 focus:border-orange-500/50 focus:outline-none font-mono transition-all"
            placeholder="Execute command or prompt agent..."
          />
          <button
            type="submit"
            disabled={isLoading}
            className="absolute right-3 p-2 text-zinc-500 hover:text-orange-500 transition-colors disabled:opacity-50"
          >
            <Send size={18} />
          </button>
        </div>
      </form>
    </div>
  );
};
