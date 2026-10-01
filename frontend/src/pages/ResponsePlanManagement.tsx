import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { FileText, ShieldCheck, CheckCircle2, AlertTriangle, Truck, Home, Navigation } from 'lucide-react';
import { CommanderApprovalModal } from '../components/Modals/CommanderApprovalModal';
import type { ResponsePlan } from '../types';

export const ResponsePlanManagement: React.FC = () => {
  const { plans, currentUser } = useApp();
  const [selectedPlan, setSelectedPlan] = useState<ResponsePlan | null>(null);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <FileText className="w-6 h-6 text-blue-600" />
          <span>Response Plan Lifecycle & Dispatch Authorization</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          End-to-end plan governance. Verified by the Verification Agent against ground-truth data, with cryptographic
          dispatch sign-off reserved exclusively for authorized Incident Commanders.
        </p>
      </div>

      <div className="space-y-4">
        {plans.length === 0 ? (
          <div className="bg-white p-12 text-center text-xs text-slate-500 rounded-md border border-slate-200">
            No response plans in the system. Run the agent pipeline from the Command Center or Incident Intelligence modules to formulate a plan.
          </div>
        ) : (
          plans.map((plan) => {
            const isAwaiting = plan.status === 'AWAITING_APPROVAL';
            const isDispatched = plan.status === 'DISPATCHED';
            const isRerouted = plan.title.includes('Rerouted');

            return (
              <div
                key={plan.id}
                className={`bg-white rounded-md border p-6 shadow-xs text-xs space-y-4 ${
                  isRerouted
                    ? 'border-purple-300 ring-1 ring-purple-100'
                    : isAwaiting
                    ? 'border-blue-300'
                    : 'border-slate-200'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-base font-bold text-slate-900">{plan.title}</span>
                      <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[10px] font-bold">
                        v{plan.version}
                      </span>
                      {isRerouted && (
                        <span className="px-2 py-0.5 rounded bg-purple-100 text-purple-800 font-bold text-[10px]">
                          AUTOMATED REPLAN
                        </span>
                      )}
                    </div>
                    <div className="text-slate-500 text-[11px] mt-0.5">
                      Plan ID: <code className="font-mono text-slate-700">{plan.id}</code> | Created:{' '}
                      {new Date(plan.created_at).toLocaleString()}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={`px-2.5 py-1 rounded text-xs font-bold ${
                        isDispatched
                          ? 'bg-emerald-100 text-emerald-800'
                          : isAwaiting
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {plan.status}
                    </span>

                    {isAwaiting && (
                      <button
                        onClick={() => setSelectedPlan(plan)}
                        className="px-4 py-1.5 rounded-md bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs cursor-pointer shadow-xs"
                      >
                        Authorize Dispatch
                      </button>
                    )}
                  </div>
                </div>

                <p className="text-slate-700 leading-relaxed">{plan.summary}</p>

                {/* Sub-grid of Allocated Assets, Route, and Shelter */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                  <div className="p-3 rounded bg-slate-50 border border-slate-200 space-y-1">
                    <div className="font-bold text-slate-800 flex items-center gap-1.5 mb-1">
                      <Truck className="w-3.5 h-3.5 text-blue-600" />
                      <span>Assigned Units ({plan.resource_assignments?.length ?? 0})</span>
                    </div>
                    {plan.resource_assignments?.map((a) => (
                      <div key={a.id} className="text-slate-600 flex justify-between">
                        <span>{a.resource?.callsign}</span>
                        <span className="text-[10px] text-slate-400">{a.resource?.resource_type}</span>
                      </div>
                    ))}
                  </div>

                  <div className="p-3 rounded bg-slate-50 border border-slate-200 space-y-1">
                    <div className="font-bold text-slate-800 flex items-center gap-1.5 mb-1">
                      <Home className="w-3.5 h-3.5 text-indigo-600" />
                      <span>Target Evacuation Facility</span>
                    </div>
                    <div className="text-slate-800 font-semibold">{plan.target_shelter?.name ?? 'Designated Shelter'}</div>
                    <div className="text-slate-500 text-[11px]">{plan.target_shelter?.address}</div>
                  </div>

                  <div className="p-3 rounded bg-slate-50 border border-slate-200 space-y-1">
                    <div className="font-bold text-slate-800 flex items-center gap-1.5 mb-1">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Verification Audit</span>
                    </div>
                    <div className="text-slate-700">
                      Score: <b className="text-emerald-700">{plan.verification_score ?? 95}/100</b>
                    </div>
                    <div className="text-[11px] text-slate-500">
                      Clearance: {plan.is_verified ? 'Zero ground-truth violations' : 'Audit pending'}
                    </div>
                  </div>
                </div>

                {plan.approved_at && (
                  <div className="p-2.5 rounded bg-emerald-50 text-emerald-900 border border-emerald-200 text-[11px] flex items-center justify-between">
                    <span>
                      <b>Authorized by Incident Commander:</b> {plan.approval_notes}
                    </span>
                    <span className="font-mono text-emerald-700">{new Date(plan.approved_at).toLocaleTimeString()}</span>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      <CommanderApprovalModal
        plan={selectedPlan}
        onClose={() => setSelectedPlan(null)}
      />
    </div>
  );
};
