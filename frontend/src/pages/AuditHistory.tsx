import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { History, ShieldCheck, Terminal, User, Cpu, Sliders } from 'lucide-react';
import type { AuditLog } from '../types';

export const AuditHistory: React.FC = () => {
  const { auditLogs } = useApp();
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <History className="w-6 h-6 text-slate-800" />
          <span>Audit Trail & Immutable Decision History</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Cryptographically recorded state transitions, human dispatch sign-offs, agent plan formulations, and route invalidations.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Table of Audit Logs (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-md border border-slate-200 shadow-xs overflow-hidden">
          <div className="overflow-x-auto max-h-[600px]">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-50 border-b border-slate-200 sticky top-0 font-bold text-slate-600 text-[11px] uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Action</th>
                  <th className="py-2.5 px-3">Actor</th>
                  <th className="py-2.5 px-3">Target</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {auditLogs.map((log) => {
                  const isSelected = selectedLog?.id === log.id;
                  const isAgent = log.actor_type === 'AGENT';
                  const isUser = log.actor_type === 'USER';

                  return (
                    <tr
                      key={log.id}
                      onClick={() => setSelectedLog(log)}
                      className={`hover:bg-slate-50 cursor-pointer transition ${
                        isSelected ? 'bg-blue-50/50' : ''
                      }`}
                    >
                      <td className="py-2.5 px-3 text-slate-500 font-mono text-[11px]">
                        {new Date(log.created_at).toLocaleTimeString()}
                      </td>

                      <td className="py-2.5 px-3 font-semibold text-slate-800">
                        {log.action}
                      </td>

                      <td className="py-2.5 px-3">
                        <span className={`inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-bold ${
                          isUser ? 'bg-blue-50 text-blue-800 border border-blue-200' : 'bg-slate-100 text-slate-700'
                        }`}>
                          {isUser ? <User className="w-2.5 h-2.5" /> : <Cpu className="w-2.5 h-2.5" />}
                          <span>{log.actor_type}</span>
                        </span>
                      </td>

                      <td className="py-2.5 px-3 text-slate-600 font-mono text-[11px]">
                        {log.target_entity}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Log Inspector (5 cols) */}
        <div className="lg:col-span-5">
          {selectedLog ? (
            <div className="bg-white rounded-md border border-slate-200 shadow-xs p-5 space-y-4 text-xs">
              <div className="border-b border-slate-200 pb-3">
                <span className="text-[10px] font-mono text-slate-400 block">RECORD ID: {selectedLog.id}</span>
                <h3 className="font-bold text-slate-900 text-base mt-0.5">{selectedLog.action}</h3>
                <div className="text-slate-500 text-[11px] mt-1">
                  Actor: <b>{selectedLog.actor_id}</b> ({selectedLog.actor_type})
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Operational Summary:</label>
                <div className="p-3 rounded bg-slate-50 border border-slate-200 text-slate-800 leading-relaxed">
                  {selectedLog.summary}
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1 flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-blue-600" />
                  <span>State Payload & Context:</span>
                </label>
                <pre className="p-3 bg-slate-900 text-slate-200 rounded text-[11px] font-mono overflow-x-auto max-h-[220px]">
                  {(() => {
                    try {
                      return JSON.stringify(JSON.parse(selectedLog.details_json || '{}'), null, 2);
                    } catch {
                      return selectedLog.details_json || '{}';
                    }
                  })()}
                </pre>
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500 bg-white rounded border border-slate-200 text-xs">
              Select an audit record to inspect the captured state diff and actor credentials.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
