'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Shield, KeyRound, BrainCircuit, ArrowRight, Lock, CheckCircle2, Zap } from 'lucide-react';
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
const VALIDATION_FAILED_MESSAGE = '⚠️ Validação Falhou: O servidor não aceitou uma ou mais chaves. Verifique os valores colados.';

export const SettingsVault: React.FC<SettingsVaultProps> = ({ onSetupComplete, onBack }) => {
  const [status, setStatus] = useState<SettingsStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Estados explícitos por campo (mais fácil de auditar e mapear)
  const [groqKey, setGroqKey] = useState('');
  const [langchainKey, setLangchainKey] = useState('');
  const [metaAppId, setMetaAppId] = useState('');
  const [metaAppSecret, setMetaAppSecret] = useState('');
  const [metaAccessToken, setMetaAccessToken] = useState('');
  const [adAccountId, setAdAccountId] = useState('');
  const [isValid, setIsValid] = useState(false);

  const [toast, setToast] = useState<{ show: boolean; message: string; type: 'success' | 'error' }>({ show: false, message: '', type: 'success' });
  const [hasAuthError, setHasAuthError] = useState(false);
  const [authErrorMessage, setAuthErrorMessage] = useState(VALIDATION_FAILED_MESSAGE);
  const toastRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLDivElement>(null);

  const validateForm = () =>
      groqKey.trim().length > 0 &&
      metaAppId.trim().length > 0 &&
      metaAppSecret.trim().length > 0 &&
      metaAccessToken.trim().length > 0 &&
      adAccountId.trim().length > 0 &&
      langchainKey.trim().length > 0;

  // Unificação da Validação: atualiza isValid em tempo real monitorando as 6 variáveis
  useEffect(() => {
    setIsValid(validateForm());
  }, [groqKey, metaAppId, metaAppSecret, metaAccessToken, adAccountId, langchainKey]);

  // Log de Depuração Temporário para monitorar o estado do Vault
  useEffect(() => {
    const debugPreview = (value: string) => {
      const trimmed = value.trim();
      return trimmed.length > 0 ? trimmed.slice(0, 3) : 'EMPTY';
    };

    console.log("🛡️ [Vault Debug] Estado dos Campos:", {
      groq: debugPreview(groqKey),
      langchain: debugPreview(langchainKey),
      appId: debugPreview(metaAppId),
      appSecret: debugPreview(metaAppSecret),
      token: debugPreview(metaAccessToken),
      accountId: debugPreview(adAccountId),
      isValid: isValid
    });
  }, [groqKey, langchainKey, metaAppId, metaAppSecret, metaAccessToken, adAccountId, isValid]);

  useEffect(() => {
    fetchSettingsStatus();
    animateEntry();
  }, []);

  // Inicializa variáveis de estado do formulário caso o backend retorne dados existentes
  useEffect(() => {
    if (!status) return;
    // Mantém compatibilidade caso a API retorne chaves diferentes
    // Preenche campos locais apenas se estiverem vazios
    setGroqKey((v) => v || (''));
    setLangchainKey((v) => v || (''));
    setMetaAppId((v) => v || (''));
    setMetaAppSecret((v) => v || (''));
    setMetaAccessToken((v) => v || (''));
    setAdAccountId((v) => v || (''));
  }, [status]);

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

  // Handlers são explícitos por campo para evitar erros de mapeamento
  const clearAuthError = () => {
    if (hasAuthError) setHasAuthError(false);
    if (authErrorMessage !== VALIDATION_FAILED_MESSAGE) setAuthErrorMessage(VALIDATION_FAILED_MESSAGE);
  };


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isValid) {
      showToast('ERRO: Preencha todos os campos obrigatórios.', 'error');
      return;
    }

    setIsSaving(true);
    setHasAuthError(false);

    const payload: SettingsForm = {
      groq_api_key: groqKey.trim(),
      meta_app_id: metaAppId.trim(),
      meta_app_secret: metaAppSecret.trim(),
      meta_access_token: metaAccessToken.trim(),
      ad_account_id: adAccountId.trim(),
      langchain_api_key: langchainKey.trim(),
    };

    try {
      const res = await fetch(`${API_URL}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        let errBody = {} as any;
        try { errBody = await res.json(); } catch (_) {}
        const errorMessage = errBody.error || errBody.detail || 'Erro ao salvar configurações';

        if (res.status === 401) {
          setHasAuthError(true);
          setAuthErrorMessage(errorMessage);
          showToast(errorMessage, 'error');
          return;
        }

        throw new Error(errorMessage);
      }

      const result = await res.json();
      const updatedStatus = result.data as SettingsStatus;

      setStatus(updatedStatus);

      if (updatedStatus.is_fully_configured) {
        showToast('Sistemas Online. Configurações armazenadas no Vault.', 'success');
        // limpa campos
        setGroqKey(''); setMetaAppId(''); setMetaAppSecret(''); setMetaAccessToken(''); setAdAccountId(''); setLangchainKey('');
        setTimeout(() => onSetupComplete(), 2000);
      } else {
        showToast('Configurações parciais salvas. Algumas chaves ainda estão pendentes.', 'error');
      }
    } catch (err: any) {
      showToast(err.message || 'Erro ao conectar. Verifique o servidor.', 'error');
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
    <div className="min-h-screen bg-zinc-950 text-white flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-orange-500/5 rounded-full blur-[100px] pointer-events-none" />

      <div ref={formRef} className="relative z-10 w-full max-w-xl bg-zinc-900 border border-zinc-800 rounded-3xl p-8 shadow-2xl shadow-black/50">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-zinc-950 border border-zinc-800 rounded-xl mb-4">
            <Shield size={24} className="text-orange-500" />
          </div>
          <h1 className="text-3xl font-black tracking-tighter mb-2">
            <span className="bg-gradient-to-b from-white to-zinc-500 bg-clip-text text-transparent uppercase">Vault Access</span>
          </h1>
          <p className="text-zinc-500 font-mono text-[10px] uppercase tracking-widest max-w-xs mx-auto">
            Credenciais Criptografadas: Validando Acesso ao Esquadrão
          </p>
        </div>

        {/* Error Pulse Warning */}
        {hasAuthError && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center space-x-3 animate-pulse">
            <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center text-red-500 flex-shrink-0">
              <Zap size={16} />
            </div>
            <p className="text-xs font-mono font-bold text-red-500 uppercase leading-tight">
              {authErrorMessage}
            </p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Brain Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest ml-1">Groq API Key (Llama 3)</label>
              <div className="relative group">
                <KeyRound size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600 group-focus-within:text-orange-500 transition-colors" />
                <input
                  type="password"
                  name="groq_api_key"
                  value={groqKey}
                  onChange={(e) => { setGroqKey(e.target.value); clearAuthError(); }}
                  className={`w-full bg-zinc-950 text-white pl-10 pr-12 py-3 rounded-xl border ${hasAuthError ? 'border-red-500/50' : 'border-zinc-800'} focus:border-orange-500/50 focus:outline-none font-mono text-sm transition-all`}
                  placeholder="gsk_..."
                  autoComplete="off"
                />
                <div className="absolute right-4 top-1/2 -translate-y-1/2">
                  {isSaving ? (
                    <div className="w-4 h-4 border-2 border-orange-500/30 border-t-orange-500 rounded-full animate-spin" />
                  ) : groqKey.trim().length > 0 ? (
                    <CheckCircle2 size={16} className="text-emerald-500" />
                  ) : (
                    <Lock size={16} className="text-zinc-700" />
                  )}
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest ml-1">LangChain API Key</label>
              <div className="relative group">
                <BrainCircuit size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600 group-focus-within:text-orange-500 transition-colors" />
                <input
                  type="password"
                  name="langchain_api_key"
                  value={langchainKey}
                  onChange={(e) => { setLangchainKey(e.target.value); clearAuthError(); }}
                  className={`w-full bg-zinc-950 text-white pl-10 pr-12 py-3 rounded-xl border ${hasAuthError ? 'border-red-500/50' : 'border-zinc-800'} focus:border-orange-500/50 focus:outline-none font-mono text-sm transition-all`}
                  placeholder="lsv2_..."
                  autoComplete="off"
                />
                <div className="absolute right-4 top-1/2 -translate-y-1/2">
                  {isSaving ? (
                    <div className="w-4 h-4 border-2 border-orange-500/30 border-t-orange-500 rounded-full animate-spin" />
                  ) : langchainKey.trim().length > 0 ? (
                    <CheckCircle2 size={16} className="text-emerald-500" />
                  ) : (
                    <Lock size={16} className="text-zinc-700" />
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Meta Ads Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest ml-1">Meta App ID</label>
              <div className="relative group">
                <input
                  type="password"
                  name="meta_app_id"
                  value={metaAppId}
                  onChange={(e) => setMetaAppId(e.target.value)}
                  className="w-full bg-zinc-950 text-white px-4 pr-10 py-3 rounded-xl border border-zinc-800 focus:border-orange-500/50 focus:outline-none font-mono text-sm transition-all"
                  autoComplete="off"
                />
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  {metaAppId.trim().length > 0 ? <CheckCircle2 size={14} className="text-emerald-500" /> : <Lock size={14} className="text-zinc-700" />}
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest ml-1">App Secret</label>
              <div className="relative group">
                <input
                  type="password"
                  name="meta_app_secret"
                  value={metaAppSecret}
                  onChange={(e) => setMetaAppSecret(e.target.value)}
                  className="w-full bg-zinc-950 text-white px-4 pr-10 py-3 rounded-xl border border-zinc-800 focus:border-orange-500/50 focus:outline-none font-mono text-sm transition-all"
                  autoComplete="off"
                />
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  {metaAppSecret.trim().length > 0 ? <CheckCircle2 size={14} className="text-emerald-500" /> : <Lock size={14} className="text-zinc-700" />}
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest ml-1">Access Token</label>
              <div className="relative group">
                <input
                  type="password"
                  name="meta_access_token"
                  value={metaAccessToken}
                  onChange={(e) => setMetaAccessToken(e.target.value)}
                  className="w-full bg-zinc-950 text-white px-4 pr-10 py-3 rounded-xl border border-zinc-800 focus:border-orange-500/50 focus:outline-none font-mono text-sm transition-all"
                  autoComplete="off"
                />
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  {metaAccessToken.trim().length > 0 ? <CheckCircle2 size={14} className="text-emerald-500" /> : <Lock size={14} className="text-zinc-700" />}
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest ml-1">Account ID</label>
              <div className="relative group">
                <input
                  type="password"
                  name="ad_account_id"
                  value={adAccountId}
                  onChange={(e) => setAdAccountId(e.target.value)}
                  className="w-full bg-zinc-950 text-white px-4 pr-10 py-3 rounded-xl border border-zinc-800 focus:border-orange-500/50 focus:outline-none font-mono text-sm transition-all"
                  autoComplete="off"
                />
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  {adAccountId.trim().length > 0 ? <CheckCircle2 size={14} className="text-emerald-500" /> : <Lock size={14} className="text-zinc-700" />}
                </div>
              </div>
            </div>
          </div>

          {/* Validation Feedback */}
          {!isValid && (
            <p className="text-[10px] font-mono text-orange-500/70 text-center animate-pulse uppercase tracking-widest">
              Aguardando preenchimento de todos os 6 campos obrigatórios...
            </p>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSaving || !isValid}
            className={`w-full mt-2 ${
              (isSaving || !isValid)
                ? 'bg-zinc-800 cursor-not-allowed text-zinc-500' 
                : 'bg-orange-500 hover:bg-orange-600 text-black shadow-[0_0_20px_rgba(249,115,22,0.3)]'
            } disabled:opacity-50 font-black uppercase tracking-tighter py-4 rounded-xl flex items-center justify-center space-x-2 transition-all duration-300 group`}
          >
            {isSaving ? (
              <>
                <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                <span>Executando Handshake...</span>
              </>
            ) : (
              <>
                <span>{hasAuthError ? 'Credenciais Inválidas' : 'Conectar Esquadrão'}</span>
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
          {toast.type === 'success' ? <CheckCircle2 size={18} /> : <Zap size={18} />}
          <span>{toast.message}</span>
        </div>
      )}
    </div>
  );
};
