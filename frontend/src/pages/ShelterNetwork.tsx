import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Home, ShieldCheck, HeartPulse, BatteryCharging, Droplets, Users, Plus } from 'lucide-react';
import { api } from '../services/api';

export const ShelterNetwork: React.FC = () => {
  const { shelters, refreshAll } = useApp();
  const [selectedShelterId, setSelectedShelterId] = useState<string | null>(null);
  const [intakeCount, setIntakeCount] = useState<number>(25);
  const [loading, setLoading] = useState(false);

  const handleRecordIntake = async (id: string) => {
    setLoading(true);
    try {
      await api.recordShelterIntake(id, intakeCount);
      refreshAll();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Home className="w-6 h-6 text-indigo-600" />
          <span>Shelter & Evacuation Network</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Municipal shelter capacities, intake logging, clinical field clinic readiness, and humanitarian provisions.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {shelters.map(s => {
          const occPct = Math.round((s.current_occupancy / s.total_capacity) * 100);
          const freeBeds = s.total_capacity - s.current_occupancy;
          const isFull = s.status === 'FULL' || freeBeds <= 0;

          return (
            <div key={s.id} className="bg-white rounded-md border border-slate-200 shadow-xs p-6 space-y-4 text-xs">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 text-base">{s.name}</span>
                    <span className="px-1.5 py-0.2 rounded bg-indigo-50 text-indigo-700 font-mono text-[10px] font-bold border border-indigo-200">
                      {s.code}
                    </span>
                  </div>
                  <div className="text-slate-500 mt-0.5">{s.address} ({s.sector})</div>
                </div>

                <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                  isFull
                    ? 'bg-red-50 text-red-700 border border-red-200'
                    : s.status === 'NEAR_CAPACITY'
                    ? 'bg-amber-50 text-amber-700 border border-amber-200'
                    : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                }`}>
                  {s.status}
                </span>
              </div>

              {/* Occupancy Bar */}
              <div>
                <div className="flex items-center justify-between text-slate-600 mb-1 font-medium">
                  <span>Occupancy: <b>{s.current_occupancy} / {s.total_capacity} beds</b></span>
                  <span>{occPct}% Filled ({freeBeds} available)</span>
                </div>
                <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      occPct >= 90 ? 'bg-red-500' : occPct >= 70 ? 'bg-amber-500' : 'bg-indigo-600'
                    }`}
                    style={{ width: `${Math.min(100, occPct)}%` }}
                  />
                </div>
              </div>

              {/* Facilities Checklist */}
              <div className="grid grid-cols-2 gap-2 border-t border-b border-slate-100 py-3 text-slate-600">
                <div className="flex items-center gap-1.5">
                  <HeartPulse className={`w-4 h-4 ${s.has_medical_facility ? 'text-emerald-600' : 'text-slate-300'}`} />
                  <span>{s.has_medical_facility ? 'Field Clinic Active' : 'Basic First Aid'}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <BatteryCharging className={`w-4 h-4 ${s.has_power_backup ? 'text-emerald-600' : 'text-slate-300'}`} />
                  <span>{s.has_power_backup ? 'Diesel Generator 500kVA' : 'Grid Dependent'}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Users className="w-4 h-4 text-blue-600" />
                  <span>Rations: {s.food_days_remaining} days</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Droplets className="w-4 h-4 text-cyan-600" />
                  <span>Potable Water: {s.water_liters_available.toLocaleString()} L</span>
                </div>
              </div>

              {/* Intake Action */}
              <div className="flex items-center justify-between pt-1">
                <div className="text-[11px] text-slate-500">
                  Officer: <b>{s.contact_person}</b> ({s.contact_phone})
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={intakeCount}
                    onChange={e => setIntakeCount(parseInt(e.target.value) || 10)}
                    className="w-16 border border-slate-300 rounded px-2 py-1 text-center bg-white text-slate-900"
                  />
                  <button
                    onClick={() => handleRecordIntake(s.id)}
                    disabled={loading || isFull}
                    className="px-3 py-1 rounded bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold border border-indigo-200 flex items-center gap-1 cursor-pointer disabled:opacity-50"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Admit</span>
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
