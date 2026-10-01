import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Bell, AlertTriangle, CheckCircle2, Info, Check } from 'lucide-react';

export const AlertCenter: React.FC = () => {
  const { alerts, acknowledgeAlert } = useApp();
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');

  const filtered = alerts.filter(a => filterSeverity === 'ALL' || a.severity === filterSeverity);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Bell className="w-6 h-6 text-amber-600" />
            <span>Alert Center & Real-Time Broadcasts</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Hazard warnings, transit corridor closures, shelter capacity thresholds, and dispatch mobilization events.
          </p>
        </div>

        <div className="flex items-center gap-1.5 bg-white border border-slate-200 rounded px-2.5 py-1.5 shadow-xs text-xs">
          <select
            value={filterSeverity}
            onChange={e => setFilterSeverity(e.target.value)}
            className="bg-transparent border-none text-slate-800 focus:outline-none"
          >
            <option value="ALL">All Severities ({alerts.length})</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="WARNING">WARNING</option>
            <option value="INFO">INFO</option>
            <option value="SUCCESS">SUCCESS</option>
          </select>
        </div>
      </div>

      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="bg-white p-12 text-center text-xs text-slate-500 rounded-md border border-slate-200">
            No active alerts matching the selected severity filter.
          </div>
        ) : (
          filtered.map(alert => {
            const isCrit = alert.severity === 'CRITICAL';
            const isSuccess = alert.severity === 'SUCCESS';
            const isWarn = alert.severity === 'WARNING';

            return (
              <div
                key={alert.id}
                className={`p-4 rounded-md border text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition ${
                  isCrit
                    ? 'bg-red-50/50 border-red-200'
                    : isSuccess
                    ? 'bg-emerald-50/50 border-emerald-200'
                    : isWarn
                    ? 'bg-amber-50/50 border-amber-200'
                    : 'bg-white border-slate-200'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">
                    {isCrit && <AlertTriangle className="w-5 h-5 text-red-600" />}
                    {isSuccess && <CheckCircle2 className="w-5 h-5 text-emerald-600" />}
                    {isWarn && <AlertTriangle className="w-5 h-5 text-amber-600" />}
                    {!isCrit && !isSuccess && !isWarn && <Info className="w-5 h-5 text-blue-600" />}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-900 text-sm">{alert.title}</span>
                      <span className={`px-1.5 py-0.2 rounded font-bold text-[10px] ${
                        isCrit ? 'bg-red-100 text-red-800' : isSuccess ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'
                      }`}>
                        {alert.category}
                      </span>
                    </div>
                    <p className="mt-1 text-slate-600 leading-relaxed">{alert.message}</p>
                    <div className="text-[11px] text-slate-400 mt-1 font-mono">
                      Timestamp: {new Date(alert.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>

                <div className="shrink-0">
                  {alert.is_acknowledged ? (
                    <span className="text-slate-400 font-medium flex items-center gap-1 text-[11px]">
                      <Check className="w-3.5 h-3.5 text-emerald-600" />
                      Acknowledged
                    </span>
                  ) : (
                    <button
                      onClick={() => acknowledgeAlert(alert.id)}
                      className="px-3 py-1.5 rounded bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 font-semibold cursor-pointer shadow-xs"
                    >
                      Acknowledge
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
