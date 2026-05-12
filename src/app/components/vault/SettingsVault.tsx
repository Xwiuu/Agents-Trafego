'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Shield, KeyRound, BrainCircuit, Globe, ArrowRight, Lock, CheckCircle2, AlertCircle, Zap } from 'lucide-react';
import gsap from 'gsap';

interface SettingsStatus {
  has_groq_key: boolean;
  has_meta_app_id: boolean;
  has_meta_app_secret: boolean;
  has_meta_access_token: boolean;
  has_ad_account_id: boolean;
  has_langchain_key: boolean;
  is_fully_configured: boolean;
}

interface SettingsForm {
  groq_api_key: string;
  meta_app_id: string;
  meta_app_secret: string;
  meta_access_token: string;
  ad_account_id: string;
  langchain_api_key: string;
}

interface SettingsVaultProps {
  onSetupComplete: () => void;
  onBack: () => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const SettingsVault: React.FC<SettingsVaultProps> = ({ onSetupComplete, onBack }) => {
  const [status, setStatus] = useState<SettingsStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [form, setForm] = useState<SettingsForm>({
    groq_api_key: '',
    meta_app_id: '',
    meta_app_secret: '',
    meta_access_token: '',
    ad_account_id: '',
    langchain_api_key: '',
  });
  const [toast, setToast] = useState<{ show: boolean; message: string; type: 'success' | 'error' }>({ show: false, message: '', type: 'success' });
  const toastRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchSettingsStatus();
    animateEntry();
  }, []);

  const animateEntry = () => {
    if (formRef.current) {
      gsap.fromTo(
        formRef.current,
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.8, ease: 'power4.out' }
      );
    }
  };

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ show: true, message, type });
    if (toastRef.current) {
      gsap.fromTo(
        toastRef.current,
        { y: 50, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5, ease: 'back.out(1.7)' }
      );
      setTimeout(() => {
        if (toastRef.current) {
          gsap.to(toastRef.current, { y: 50, opacity: 0, duration: 0.3 });
        }
        setToast((prev) => ({ ...prev, show: false }));
      }, 4000);
    }
  };

  const fetchSettingsStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/api/settings`);
      if (!res.ok) throw new Error('Failed to fetch settings');
      const data = await res.json();
      setStatus(data);
    } catch (err) {
      showToast('Conexão com o backend falhou. Verifique se o servidor está online.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      const res = await fetch(`${API_URL}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Erro ao salvar configurações');
      }

      showToast('Sistemas Online. Configurações armazenadas no Vault.', 'success');
      setForm({ groq_api_key: '', meta_app_id: '', meta_app_secret: '', meta_access_token: '', ad_account_id: '', langchain_api_key: '' });
      await fetchSettingsStatus();
      setTimeout(() => onSetupComplete(), 2000);
    } catch (err: any) {
      showToast(err.message || 'Erro ao conectar. Verifique a porta do backend.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="flex items-center space-x-3 text-orange-500 animate-pulse">
          <Zap size={24} />
          <span className="font-mono text-lg tracking-widest">INICIANDO VAULT...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-white flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-orange-500/5 rounded-full blur-[100px] pointer-events-none" />

      <div ref={formRef} className="relative z-10 w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-zinc-900 border border-zinc-800 rounded-2xl mb-6">
            <Shield size={32} className="text-orange-500" />
          </div>
          <h1 className="text-4xl md:text-5xl font-black tracking-tight mb-4">
            <span className="bg-gradient-to-b from-white to-zinc-500 bg-clip-text text-transparent">VAULT ACCESS</span>
          </h1>
          <p className="text-zinc-400 font-mono text-sm max-w-lg mx-auto">
            Configure as chaves de acesso para ativar o Esquadrão de Agentes. Todas as credenciais são criptografadas localmente.
          </p>
        </div>

        {/* Status indicators */}
        {status && (
          <div className="flex flex-wrap items-center justify-center gap-2 mb-8">
            <button 
              onClick={onBack}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md border border-zinc-800 bg-zinc-900/50 text-zinc-500 hover:text-white hover:border-zinc-700 transition-colors text-xs font-mono uppercase tracking-wider mr-2"
            >
              <ArrowRight size={12} className="rotate-180" />
              <span>Back</span>
            </button>
            {[
              { label: 'Groq', active: status.has_groq_key },
              { label: 'LangChain', active: status.has_langchain_key },
              { label: 'App ID', active: status.has_meta_app_id },
              { label: 'Secret', active: status.has_meta_app_secret },
              { label: 'Token', active: status.has_meta_access_token },
              { label: 'Account', active: status.has_ad_account_id },
            ].map((item) => (
              <div
                key={item.label}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md border text-xs font-mono font-bold tracking-wider uppercase ${
                  item.active
                    ? 'bg-orange-500/10 border-orange-500/30 text-orange-400'
                    : 'bg-zinc-900/50 border-zinc-800 text-zinc-600'
                }`}
              >
                {item.active ? <CheckCircle2 size={12} /> : <Lock size={12} />}
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Brain Section */}
          <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center space-x-3 mb-4">
              <BrainCircuit size={20} className="text-orange-500" />
              <h2 className="text-sm font-mono font-bold tracking-widest uppercase text-orange-500">Seção Cérebro</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono text-zinc-400 mb-2 uppercase tracking-wider">Groq API Key (Llama 3)</label>
                <div className="relative">
                  <KeyRound size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600" />
                  <input
                    type="password"
                    name="groq_api_key"
                    value={form.groq_api_key}
                    onChange={handleChange}
                    className="w-full bg-zinc-950 text-white pl-10 pr-4 py-3 rounded-xl border border-zinc-800 focus:border-orange-500/50 focus:outline-none font-mono text-sm transition-all"
                    placeholder="gsk_..."
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-mono text-zinc-400 mb-2 uppercase tracking-wider">LangChain API Key (Tracing)</label>
                <div className="relative">
                  <KeyRound size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600" />
                  <input
                    type="password"
                    name="langchain_api_key"
                    value={form.langchain_api_key}
                    onChange={handleChange}
                    className="w-full bg-zinc-950 text-white pl-10 pr-4 py-3 rounded-xl border border-zinc-800 focus:border-orange-500/50 focus:outline-none font-mono text-sm transition-all"
                    placeholder="lsv2_..."
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Meta Ads Section */}
          <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center space-x-3 mb-4">
              <Globe size={20} className="text-orange-500" />
              <h2 className="text-sm font-mono font-bold tracking-widest uppercase text-orange-500">Seção Meta Ads</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono text-zinc-400 mb-2 uppercase tracking-wider">App ID</label>
                <div className="relative">
                  <Lock size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600" />
                  <input
                    type="password"
                    name="meta_app_id"
                    value={form.meta_app_id}
                    onChange={handleChange}
                    className="w-full bg-zinc-950 text-white pl-9 pr-4 py-3 rounded-xl border border-zinc-800 focus:border-orange-500/50 focus:outline-none font-mono text-sm transition-all"
                    placeholder=""
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-mono text-zinc-400 mb-2 uppercase tracking-wider">App Secret</label>
                <div className="relative">
                  <Lock size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600" />
                  <input
                    type="password"
                    name="meta_app_secret"
                    value={form.meta_app_secret}
                    onChange={handleChange}
                    className="w-full bg-zinc-950 text-white pl-9 pr-4 py-3 rounded-xl border border-zinc-800 focus:border-orange-500/50 focus:outline-none font-mono text-sm transition-all"
                    placeholder=""
                  />
                </div>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono text-zinc-400 mb-2 uppercase tracking-wider">Access Token</label>
                <div className="relative">
                  <Lock size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600" />
                  <input
                    type="password"
                    name="meta_access_token"
                    value={form.meta_access_token}
                    onChange={handleChange}
                    className="w-full bg-zinc-950 text-white pl-9 pr-4 py-3 rounded-xl border border-zinc-800 focus:border-orange-500/50 focus:outline-none font-mono text-sm transition-all"
                    placeholder=""
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-mono text-zinc-400 mb-2 uppercase tracking-wider">Ad Account ID</label>
                <div className="relative">
                  <Lock size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600" />
                  <input
                    type="password"
                    name="ad_account_id"
                    value={form.ad_account_id}
                    onChange={handleChange}
                    className="w-full bg-zinc-950 text-white pl-9 pr-4 py-3 rounded-xl border border-zinc-800 focus:border-orange-500/50 focus:outline-none font-mono text-sm transition-all"
                    placeholder=""
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSaving}
            className="w-full bg-orange-500 hover:bg-orange-600 disabled:bg-zinc-800 text-black font-bold py-4 rounded-xl flex items-center justify-center space-x-2 transition-all duration-300 group"
          >
            {isSaving ? (
              <>
                <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                <span>CONECTANDO...</span>
              </>
            ) : (
              <>
                <span>Conectar Esquadrão</span>
                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </form>
      </div>

      {/* Toast */}
      {toast.show && (
        <div
          ref={toastRef}
          className={`fixed bottom-8 left-1/2 -translate-x-1/2 px-6 py-3 rounded-xl border font-mono text-sm font-bold flex items-center space-x-3 z-50 shadow-2xl ${
            toast.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/30 text-emerald-400'
              : 'bg-red-950/90 border-red-500/30 text-red-400'
          }`}
        >
          {toast.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
          <span>{toast.message}</span>
        </div>
      )}
    </div>
  );
};
