import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Truck, CheckCircle2, Navigation, AlertCircle, Filter } from 'lucide-react';
import { api } from '../services/api';

export const ResourceCommand: React.FC = () => {
  const { resources, refreshAll } = useApp();
  const [filterType, setFilterType] = useState<string>('ALL');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const resourceTypes = Array.from(new Set(resources.map(r => r.resource_type)));

  const filtered = resources.filter(r => {
    if (filterType !== 'ALL' && r.resource_type !== filterType) return false;
    if (filterStatus !== 'ALL' && r.status !== filterStatus) return false;
    return true;
  });

  const handleStatusChange = async (id: string, newStatus: string) => {
    await api.updateResourceStatus(id, newStatus);
    refreshAll();
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Truck className="w-6 h-6 text-blue-600" />
            <span>Resource Command & Fleet Registry</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Authoritative fleet inventory across Suryanagar. Double-booking prevention enforced across all response units.
          </p>
        </div>

        {/* Filter Toolbar */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <div className="flex items-center gap-1.5 bg-white border border-slate-200 rounded px-2.5 py-1.5 shadow-xs">
            <Filter className="w-3.5 h-3.5 text-slate-500" />
            <select
              value={filterType}
              onChange={e => setFilterType(e.target.value)}
              className="bg-transparent border-none text-slate-800 focus:outline-none"
            >
              <option value="ALL">All Categories ({resources.length})</option>
              {resourceTypes.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-1.5 bg-white border border-slate-200 rounded px-2.5 py-1.5 shadow-xs">
            <select
              value={filterStatus}
              onChange={e => setFilterStatus(e.target.value)}
              className="bg-transparent border-none text-slate-800 focus:outline-none"
            >
              <option value="ALL">All Statuses</option>
              <option value="AVAILABLE">AVAILABLE</option>
              <option value="ASSIGNED">ASSIGNED</option>
              <option value="IN_TRANSIT">IN_TRANSIT</option>
              <option value="ON_SCENE">ON_SCENE</option>
            </select>
          </div>
        </div>
      </div>

      {/* Fleet Inventory Table */}
      <div className="bg-white rounded-md border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 font-bold text-slate-600 text-[11px] uppercase tracking-wider">
                <th className="py-3 px-4">Callsign / Name</th>
                <th className="py-3 px-4">Capability Type</th>
                <th className="py-3 px-4">Base Station</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Speed / Fuel</th>
                <th className="py-3 px-4">Capacity</th>
                <th className="py-3 px-4 text-right">Operational State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map(r => {
                const isAvailable = r.status === 'AVAILABLE';
                const isDispatched = r.status === 'IN_TRANSIT' || r.status === 'ASSIGNED';

                return (
                  <tr key={r.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4">
                      <div className="font-bold text-slate-900">{r.callsign}</div>
                      <div className="text-[11px] text-slate-500">{r.name}</div>
                    </td>

                    <td className="py-3 px-4 font-mono text-[11px] text-slate-700">
                      {r.resource_type}
                    </td>

                    <td className="py-3 px-4 text-slate-600">
                      {r.base_station}
                    </td>

                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                        isAvailable
                          ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                          : isDispatched
                          ? 'bg-blue-50 text-blue-800 border border-blue-200'
                          : 'bg-amber-50 text-amber-800 border border-amber-200'
                      }`}>
                        {r.status}
                      </span>
                    </td>

                    <td className="py-3 px-4 text-slate-600">
                      <div>{r.speed_kmh} km/h</div>
                      <div className="text-[11px] text-slate-400">Fuel: {r.fuel_percent}%</div>
                    </td>

                    <td className="py-3 px-4 text-slate-700 font-semibold">
                      {r.capacity} pax
                    </td>

                    <td className="py-3 px-4 text-right">
                      <select
                        value={r.status}
                        onChange={e => handleStatusChange(r.id, e.target.value)}
                        className="border border-slate-200 rounded px-2 py-1 text-[11px] bg-white text-slate-800 cursor-pointer focus:outline-blue-500"
                      >
                        <option value="AVAILABLE">AVAILABLE</option>
                        <option value="ASSIGNED">ASSIGNED</option>
                        <option value="IN_TRANSIT">IN_TRANSIT</option>
                        <option value="ON_SCENE">ON_SCENE</option>
                        <option value="RETURNING">RETURNING</option>
                        <option value="OUT_OF_SERVICE">OUT_OF_SERVICE</option>
                      </select>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
