import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Flame, AlertCircle, Cpu, CheckCircle2, MessageSquare, Copy } from 'lucide-react';
import type { Incident } from '../types';

export const IncidentIntelligence: React.FC = () => {
  const { incidents, runIncidentPipeline } = useApp();
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(incidents[0] || null);
  const [runningId, setRunningId] = useState<string | null>(null);

  const handleRunPipeline = async (id: string) => {
    setRunningId(id);
    try {
      await runIncidentPipeline(id);
    } finally {
      setRunningId(null);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Flame className="w-6 h-6 text-red-600" />
          <span>Incident Intelligence & Triage Ingestion</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Multi-channel ingestion of emergency calls and sensor alerts. The Situation Intelligence Agent automatically
          de-duplicates reports, while the Triage Agent computes life-threat acuity.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Incident List (5 Cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-500 px-1">
            Active Verified Incidents ({incidents.length})
          </div>

          <div className="space-y-2.5">
            {incidents.map((inc) => {
              const isSelected = selectedIncident?.id === inc.id;
              const isCrit = inc.severity === 'CRITICAL';

              return (
                <div
                  key={inc.id}
                  onClick={() => setSelectedIncident(inc)}
                  className={`p-4 rounded-md border text-xs cursor-pointer transition ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50/40 shadow-xs'
                      : 'border-slate-200 bg-white hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-bold text-slate-900 text-sm">{inc.title}</div>
                      <div className="text-slate-500 mt-0.5">{inc.address} ({inc.sector})</div>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                        isCrit ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {inc.severity}
                    </span>
                  </div>

                  <div className="mt-3 flex items-center justify-between text-slate-600 border-t border-slate-100 pt-2 text-[11px]">
                    <div>
                      Priority Score: <b className="text-slate-900">{inc.priority_score.toFixed(1)}/100</b>
                    </div>
                    <div className="flex items-center gap-2">
                      <span>Trapped: <b className="text-red-700">{inc.trapped_count}</b></span>
                      <span>Critical: <b>{inc.medical_critical_count}</b></span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Incident Intelligence Deep-Dive (7 Cols) */}
        <div className="lg:col-span-7">
          {selectedIncident ? (
            <div className="bg-white rounded-md border border-slate-200 shadow-xs p-6 space-y-6 text-xs">
              <div className="flex items-start justify-between border-b border-slate-200 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-bold text-[10px] border border-blue-200 uppercase">
                      {selectedIncident.disaster_type}
                    </span>
                    <span className="text-slate-400">ID: {selectedIncident.id.slice(0, 8)}</span>
                  </div>
                  <h2 className="text-xl font-bold text-slate-900 mt-1">{selectedIncident.title}</h2>
                  <p className="text-slate-600 mt-1">{selectedIncident.description}</p>
                </div>

                <button
                  onClick={() => handleRunPipeline(selectedIncident.id)}
                  disabled={runningId === selectedIncident.id}
                  className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-bold flex items-center gap-1.5 cursor-pointer shadow-xs disabled:opacity-50"
                >
                  <Cpu className="w-4 h-4" />
                  <span>{runningId === selectedIncident.id ? 'Running 7 Agents...' : 'Run Agent Pipeline'}</span>
                </button>
              </div>

              {/* Triage Justification Card */}
              <div className="p-4 rounded bg-slate-50 border border-slate-200">
                <div className="font-bold text-slate-900 mb-1 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Triage & Life-Threat Acuity Evaluation</span>
                </div>
                <p className="text-slate-700 leading-relaxed">
                  {selectedIncident.triage_rationale ||
                    'Calculated based on life threat (trapped * 2.5 + medical_critical * 4.0) with environmental vulnerability factors.'}
                </p>
                <div className="mt-3 flex gap-4 text-slate-600 font-mono text-[11px]">
                  <span>Trapped Headcount: <b>{selectedIncident.trapped_count}</b></span>
                  <span>Acuity Casework: <b>{selectedIncident.medical_critical_count}</b></span>
                  <span>Total Affected: <b>{selectedIncident.affected_count}</b></span>
                </div>
              </div>

              {/* Incoming Caller Reports & De-Duplication */}
              <div>
                <div className="font-bold text-slate-900 mb-2 flex items-center gap-1.5">
                  <MessageSquare className="w-4 h-4 text-blue-600" />
                  <span>Multi-Source Distress Reports (De-duplicated)</span>
                </div>

                {selectedIncident.reports && selectedIncident.reports.length > 0 ? (
                  <div className="space-y-2">
                    {selectedIncident.reports.map((rep) => (
                      <div key={rep.id} className="p-3 rounded border border-slate-200 bg-white">
                        <div className="flex items-center justify-between text-[11px] text-slate-500 mb-1">
                          <span className="font-semibold text-slate-700">{rep.source}</span>
                          <span>{new Date(rep.created_at).toLocaleTimeString()}</span>
                        </div>
                        <p className="text-slate-800 font-mono text-[11px] bg-slate-50 p-2 rounded border border-slate-100">
                          "{rep.raw_text}"
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 rounded border border-dashed border-slate-200 text-slate-500 text-center">
                    Primary dispatch report ingested. Secondary field reports will appear as callers contact dispatch.
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500 bg-white rounded border border-slate-200">
              Select an incident from the queue to inspect detailed telemetry and run agent workflows.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
