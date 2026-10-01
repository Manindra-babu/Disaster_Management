import React from 'react';
import { useApp } from '../context/AppContext';
import { AlertCircle, Users, Truck, Home, Cpu } from 'lucide-react';

export const KpiStrip: React.FC = () => {
  const { kpis, plans } = useApp();

  const activePlansCount = plans.filter(p => p.status !== 'COMPLETED' && p.status !== 'REJECTED').length;
  const verifiedPlansCount = plans.filter(p => p.is_verified).length;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 p-4 bg-[#F8FAFC] border-b border-slate-200">
      {/* 1. Incidents */}
      <div className="bg-white p-3 rounded border border-slate-200 shadow-xs flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
          <span>ACTIVE INCIDENTS</span>
          <AlertCircle className="w-4 h-4 text-red-600" />
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-black text-slate-900">{kpis?.active_incidents ?? 0}</span>
          <span className="text-xs font-bold text-red-600 px-1.5 py-0.5 rounded bg-red-50 border border-red-100">
            {kpis?.critical_incidents ?? 0} Critical
          </span>
        </div>
        <div className="mt-1 text-[11px] text-slate-500">Authoritative triage queue</div>
      </div>

      {/* 2. Population At Risk */}
      <div className="bg-white p-3 rounded border border-slate-200 shadow-xs flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
          <span>PEOPLE AFFECTED</span>
          <Users className="w-4 h-4 text-amber-600" />
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-black text-slate-900">{kpis?.people_affected ?? 0}</span>
          <span className="text-xs font-semibold text-amber-700">
            ({kpis?.people_trapped ?? 0} trapped)
          </span>
        </div>
        <div className="mt-1 text-[11px] text-slate-500">
          {kpis?.medical_critical ?? 0} high-acuity medical
        </div>
      </div>

      {/* 3. Resources Deployment */}
      <div className="bg-white p-3 rounded border border-slate-200 shadow-xs flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
          <span>FLEET READINESS</span>
          <Truck className="w-4 h-4 text-blue-600" />
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-black text-slate-900">{kpis?.available_resources ?? 0}</span>
          <span className="text-xs text-slate-500">
            / {kpis?.total_resources ?? 0} Available
          </span>
        </div>
        <div className="mt-1 text-[11px] text-emerald-600 font-medium">
          {kpis?.deployed_resources ?? 0} units currently deployed
        </div>
      </div>

      {/* 4. Shelter Headroom */}
      <div className="bg-white p-3 rounded border border-slate-200 shadow-xs flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
          <span>SHELTER CAPACITY</span>
          <Home className="w-4 h-4 text-indigo-600" />
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-black text-slate-900">{kpis?.shelter_occupancy_pct ?? 0}%</span>
          <span className="text-xs text-slate-500">
            ({kpis?.shelter_occupancy ?? 0}/{kpis?.shelter_total_capacity ?? 0})
          </span>
        </div>
        <div className="mt-1 text-[11px] text-slate-500">
          {(kpis?.shelter_total_capacity ?? 0) - (kpis?.shelter_occupancy ?? 0)} beds headroom
        </div>
      </div>

      {/* 5. Agent Planning Status */}
      <div className="bg-white p-3 rounded border border-slate-200 shadow-xs flex flex-col justify-between col-span-2 lg:col-span-1">
        <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
          <span>MULTI-AGENT VERIFICATION</span>
          <Cpu className="w-4 h-4 text-emerald-600" />
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-black text-emerald-600">{verifiedPlansCount}</span>
          <span className="text-xs font-semibold text-slate-600">
            / {activePlansCount} Verified
          </span>
        </div>
        <div className="mt-1 text-[11px] text-slate-500">
          7 specialized agents online
        </div>
      </div>
    </div>
  );
};
