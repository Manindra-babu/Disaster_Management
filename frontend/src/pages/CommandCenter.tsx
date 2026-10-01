import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { GisMap } from '../components/GisMap';
import { KpiStrip } from '../components/KpiStrip';
import { InjectHazardModal } from '../components/Modals/InjectHazardModal';
import { CommanderApprovalModal } from '../components/Modals/CommanderApprovalModal';
import {
  AlertTriangle, Play, Pause, RotateCcw, FastForward,
  ShieldAlert, CheckCircle2, ChevronRight, Truck, Home, Cpu
} from 'lucide-react';
import type { Incident, ResponsePlan } from '../types';

export const CommandCenter: React.FC = () => {
  const {
    currentScenario,
    incidents,
    plans,
    alerts,
    currentUser,
    startSimulation,
    pauseSimulation,
    resetSimulation,
    advanceTick,
    runIncidentPipeline
  } = useApp();

  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [approvalPlan, setApprovalPlan] = useState<ResponsePlan | null>(null);
  const [isHazardModalOpen, setIsHazardModalOpen] = useState(false);
  const [pipelineLoading, setPipelineLoading] = useState<string | null>(null);

  const handleRunPipeline = async (incidentId: string) => {
    setPipelineLoading(incidentId);
    try {
      await runIncidentPipeline(incidentId);
    } finally {
      setPipelineLoading(null);
    }
  };

  const isSimRunning = currentScenario?.status === 'RUNNING';

  return (
    <div className="flex flex-col min-h-[calc(100vh-100px)] bg-[#F8FAFC]">
      {/* Authoritative KPI Strip */}
      <KpiStrip />

      {/* Main Operational Grid */}
      <div className="flex-1 p-4 grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Column: GIS Map & Fleet Overview (7 Cols) */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          {/* Map Header & Fast Controls */}
          <div className="bg-white p-3 rounded-md border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-800">Suryanagar Geographic Operations</span>
              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono text-[11px]">
                {currentScenario?.weather_summary ?? 'Clear'}
              </span>
            </div>

            {/* Simulation Clock Controls */}
            <div className="flex items-center gap-1.5">
              {isSimRunning ? (
                <button
                  onClick={pauseSimulation}
                  className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium flex items-center gap-1 cursor-pointer"
                >
                  <Pause className="w-3 h-3 text-slate-600" />
                  <span>Pause</span>
                </button>
              ) : (
                <button
                  onClick={startSimulation}
                  className="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-700 text-white font-medium flex items-center gap-1 cursor-pointer"
                >
                  <Play className="w-3 h-3" />
                  <span>Start</span>
                </button>
              )}

              <button
                onClick={advanceTick}
                className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium flex items-center gap-1 cursor-pointer"
                title="Advance simulation by 1 tick"
              >
                <FastForward className="w-3 h-3 text-slate-600" />
                <span>Next Tick</span>
              </button>

              <button
                onClick={() => setIsHazardModalOpen(true)}
                className="px-2.5 py-1 rounded bg-red-50 hover:bg-red-100 text-red-700 font-semibold border border-red-200 flex items-center gap-1 cursor-pointer"
                title="Inject road closure to test automated continuous replanning"
              >
                <ShieldAlert className="w-3 h-3 text-red-600" />
                <span>Inject Hazard</span>
              </button>

              <button
                onClick={resetSimulation}
                className="p-1 rounded text-slate-500 hover:text-slate-800 hover:bg-slate-100 cursor-pointer"
                title="Reset simulation to initial baseline"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Interactive GIS Map */}
          <GisMap
            height="460px"
            onSelectIncident={setSelectedIncident}
          />

          {/* Active Response Plans Drawer */}
          <div className="bg-white rounded-md border border-slate-200 shadow-xs p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wide">
                  Active Response Plans ({plans.length})
                </h3>
              </div>
              <span className="text-[11px] text-slate-500">
                Awaiting Commander Authorization: {plans.filter(p => p.status === 'AWAITING_APPROVAL').length}
              </span>
            </div>

            {plans.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded border border-dashed border-slate-200">
                No active response plans formulated yet. Trigger the multi-agent pipeline on an incident in the priority queue to generate a verified plan.
              </div>
            ) : (
              <div className="space-y-2.5">
                {plans.map(plan => {
                  const isAwaiting = plan.status === 'AWAITING_APPROVAL';
                  const isRerouted = plan.title.includes('Rerouted');

                  return (
                    <div
                      key={plan.id}
                      className={`p-3 rounded border text-xs flex flex-col md:flex-row md:items-center justify-between gap-3 transition ${
                        isRerouted
                          ? 'bg-amber-50/70 border-amber-300'
                          : isAwaiting
                          ? 'bg-blue-50/50 border-blue-200'
                          : 'bg-white border-slate-200'
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-900">{plan.title}</span>
                          <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                            plan.status === 'DISPATCHED'
                              ? 'bg-emerald-100 text-emerald-800'
                              : plan.status === 'AWAITING_APPROVAL'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-slate-100 text-slate-700'
                          }`}>
                            {plan.status}
                          </span>
                          {isRerouted && (
                            <span className="px-1.5 py-0.2 rounded bg-purple-100 text-purple-800 font-bold text-[10px]">
                              CONTINUOUS REPLAN
                            </span>
                          )}
                        </div>
                        <p className="text-slate-600 line-clamp-1">{plan.summary}</p>
                        <div className="flex items-center gap-4 text-[11px] text-slate-500">
                          <span>Verification: <b>{plan.verification_score ?? 95}/100</b></span>
                          <span>Units: <b>{plan.resource_assignments?.length ?? 0} assigned</b></span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        {isAwaiting && (
                          <button
                            onClick={() => setApprovalPlan(plan)}
                            className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs cursor-pointer shadow-xs"
                          >
                            Review & Approve Dispatch
                          </button>
                        )}
                        {plan.status === 'DISPATCHED' && (
                          <span className="text-emerald-700 font-bold text-xs flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Units Mobilized
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Priority Triage Queue & Operational Alerts (5 Cols) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          {/* Priority Incident Queue */}
          <div className="bg-white rounded-md border border-slate-200 shadow-xs p-4 flex-1 flex flex-col">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-600" />
                <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wide">
                  Incident Priority Triage Queue
                </h3>
              </div>
              <span className="text-[11px] text-slate-500 font-medium">Sorted by Acuity</span>
            </div>

            <div className="space-y-3 overflow-y-auto max-h-[460px] pr-1">
              {incidents.map(inc => {
                const isCrit = inc.severity === 'CRITICAL';
                const isSelected = selectedIncident?.id === inc.id;

                return (
                  <div
                    key={inc.id}
                    onClick={() => setSelectedIncident(inc)}
                    className={`p-3 rounded border text-xs cursor-pointer transition ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50/40 shadow-xs'
                        : isCrit
                        ? 'border-red-200 bg-red-50/20 hover:bg-red-50/40'
                        : 'border-slate-200 bg-white hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-1.5 font-bold text-slate-900">
                          <span>{inc.title}</span>
                        </div>
                        <p className="text-[11px] text-slate-500 mt-0.5">{inc.address}</p>
                      </div>

                      <div className="flex flex-col items-end shrink-0">
                        <span className={`px-1.5 py-0.5 rounded font-black text-[10px] ${
                          isCrit ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'
                        }`}>
                          {inc.severity} ({inc.priority_score.toFixed(0)})
                        </span>
                        <span className="text-[10px] text-slate-400 mt-1 uppercase">{inc.status}</span>
                      </div>
                    </div>

                    <div className="mt-2.5 flex items-center justify-between text-[11px] border-t border-slate-100 pt-2">
                      <div className="flex items-center gap-3 text-slate-600">
                        <span>Trapped: <b className="text-red-700">{inc.trapped_count}</b></span>
                        <span>Casualties: <b>{inc.medical_critical_count}</b></span>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRunPipeline(inc.id);
                        }}
                        disabled={pipelineLoading === inc.id}
                        className="px-2.5 py-1 rounded bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold border border-blue-200 flex items-center gap-1 cursor-pointer disabled:opacity-50"
                      >
                        <Cpu className="w-3 h-3" />
                        <span>{pipelineLoading === inc.id ? 'Coordinating...' : 'Run Agents'}</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Operational Alerts & Radio Feed */}
          <div className="bg-white rounded-md border border-slate-200 shadow-xs p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold text-slate-900 text-xs uppercase tracking-wide">
                Operational Telemetry & Broadcast Feed
              </span>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            </div>

            <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
              {alerts.slice(0, 5).map(alert => (
                <div
                  key={alert.id}
                  className={`p-2 rounded border text-[11px] ${
                    alert.severity === 'CRITICAL'
                      ? 'bg-red-50 border-red-200 text-red-900'
                      : alert.severity === 'SUCCESS'
                      ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                      : 'bg-slate-50 border-slate-200 text-slate-800'
                  }`}
                >
                  <div className="font-bold flex items-center justify-between">
                    <span>{alert.title}</span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {new Date(alert.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="mt-0.5 text-slate-600 leading-snug">{alert.message}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      <InjectHazardModal
        isOpen={isHazardModalOpen}
        onClose={() => setIsHazardModalOpen(false)}
      />

      <CommanderApprovalModal
        plan={approvalPlan}
        onClose={() => setApprovalPlan(null)}
      />
    </div>
  );
};
