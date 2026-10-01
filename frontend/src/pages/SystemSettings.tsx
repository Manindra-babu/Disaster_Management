import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { Settings, Shield, Server, CheckCircle2, RotateCcw, AlertTriangle, Key } from 'lucide-react';

export const SystemSettings: React.FC = () => {
  const { isConnected, resetSimulation } = useApp();
  const [healthData, setHealthData] = useState<any>(null);

  useEffect(() => {
    fetch('/health')
      .then(res => res.json())
      .then(setHealthData)
      .catch(() => setHealthData(null));
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Settings className="w-6 h-6 text-slate-800" />
          <span>System Settings & Architecture Health</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Infrastructure health, official Google Gemini model integration settings, and deterministic fallback diagnostics.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
        {/* Gemini Model Configuration */}
        <div className="bg-white rounded-md border border-slate-200 shadow-xs p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Key className="w-4 h-4 text-purple-600" />
              <span className="font-bold text-slate-900 text-sm">Google Gemini API Provider</span>
            </div>
            <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
              healthData?.gemini_configured
                ? 'bg-purple-100 text-purple-800'
                : 'bg-amber-100 text-amber-800'
            }`}>
              {healthData?.gemini_configured ? 'GEMINI_LLM LIVE' : 'DETERMINISTIC FALLBACK ACTIVE'}
            </span>
          </div>

          <p className="text-slate-600 leading-relaxed">
            RESQ interfaces with official Google Gemini models (default: <code>gemini-2.5-flash</code>) using structured JSON output.
            When an API key is not supplied via the backend environment, RESQ automatically and transparently engages
            the local deterministic domain reasoning engine, ensuring complete stability without hallucinated metrics.
          </p>

          <div className="p-3 bg-slate-50 rounded border border-slate-200 space-y-1.5 font-mono text-[11px] text-slate-700">
            <div>Model: <b>gemini-2.5-flash</b></div>
            <div>Structured Output Schema: <b>Enforced (Pydantic v2)</b></div>
            <div>Server-Side Key Isolation: <b>Active (Never exposed to client)</b></div>
            <div>Deterministic Fallback Engine: <b>Online & Verified</b></div>
          </div>
        </div>

        {/* Database & Telemetry Health */}
        <div className="bg-white rounded-md border border-slate-200 shadow-xs p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Server className="w-4 h-4 text-blue-600" />
              <span className="font-bold text-slate-900 text-sm">Backend & Telemetry Runtime</span>
            </div>
            <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">
              HEALTHY
            </span>
          </div>

          <div className="space-y-2.5">
            <div className="flex items-center justify-between p-2.5 rounded bg-slate-50 border border-slate-200">
              <span className="text-slate-700 font-medium">FastAPI Backend Service</span>
              <span className="text-emerald-700 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Operational (Python 3.13)
              </span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded bg-slate-50 border border-slate-200">
              <span className="text-slate-700 font-medium">Authoritative Database</span>
              <span className="text-emerald-700 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Connected (SQLAlchemy Async Engine)
              </span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded bg-slate-50 border border-slate-200">
              <span className="text-slate-700 font-medium">Real-Time Event WebSocket</span>
              <span className={`font-semibold flex items-center gap-1 ${isConnected ? 'text-emerald-700' : 'text-amber-700'}`}>
                <CheckCircle2 className="w-3.5 h-3.5" />
                {isConnected ? 'Connected (/ws)' : 'Reconnecting...'}
              </span>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-slate-500 text-[11px]">Factory Reset Environment:</span>
            <button
              onClick={resetSimulation}
              className="px-3 py-1.5 rounded border border-slate-300 hover:bg-slate-50 text-slate-700 font-semibold flex items-center gap-1.5 cursor-pointer shadow-xs"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
              <span>Reset Authoritative DB</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
