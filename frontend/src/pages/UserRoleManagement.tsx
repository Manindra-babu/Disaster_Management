import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { Users, Shield, UserCheck, Key, Lock, Check } from 'lucide-react';
import { api } from '../services/api';
import type { User } from '../types';

export const UserRoleManagement: React.FC = () => {
  const { currentUser, switchRole } = useApp();
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    api.listUsers().then(setUsers);
  }, [currentUser]);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Users className="w-6 h-6 text-blue-600" />
          <span>User & Role-Based Access Control (RBAC)</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Strict cryptographic permissions governing the platform. Only authenticated Incident Commanders possess dispatch authority.
        </p>
      </div>

      {/* Role Entitlement Matrix */}
      <div className="bg-white rounded-md border border-slate-200 shadow-xs p-6 space-y-4 text-xs">
        <h2 className="font-bold text-slate-900 text-sm uppercase tracking-wide">
          Role Capability Matrix
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded border border-slate-200 bg-slate-50 space-y-2">
            <div className="font-bold text-slate-900 text-sm">Viewer</div>
            <p className="text-slate-600 text-[11px]">Read-only observational access to GIS maps, KPIs, and agent runs.</p>
            <div className="text-[11px] text-slate-500 space-y-1 pt-2 border-t border-slate-200">
              <div>✓ View Live GIS Map</div>
              <div>✓ Inspect Agent Traces</div>
              <div className="text-red-600">✗ Cannot Modify State</div>
              <div className="text-red-600">✗ Cannot Authorize Dispatch</div>
            </div>
          </div>

          <div className="p-4 rounded border border-slate-200 bg-slate-50 space-y-2">
            <div className="font-bold text-slate-900 text-sm">Operator</div>
            <p className="text-slate-600 text-[11px]">Submits incident reports, adjusts resource status, and runs agent pipelines.</p>
            <div className="text-[11px] text-slate-500 space-y-1 pt-2 border-t border-slate-200">
              <div>✓ Ingest Caller Distress Reports</div>
              <div>✓ Run Multi-Agent Pipelines</div>
              <div>✓ Advance Simulation Clocks</div>
              <div className="text-red-600">✗ Cannot Authorize Dispatch</div>
            </div>
          </div>

          <div className="p-4 rounded border-2 border-blue-400 bg-blue-50/40 space-y-2">
            <div className="font-bold text-blue-900 text-sm flex items-center gap-1.5">
              <Shield className="w-4 h-4 text-blue-600" />
              <span>Incident Commander</span>
            </div>
            <p className="text-slate-700 text-[11px]">Authoritative emergency director holding exclusive dispatch sign-off rights.</p>
            <div className="text-[11px] text-slate-600 space-y-1 pt-2 border-t border-blue-200 font-semibold">
              <div className="text-emerald-700">✓ Cryptographic Dispatch Approval</div>
              <div>✓ Override Agent Plan Directives</div>
              <div>✓ Authorize Evacuation Corridors</div>
              <div>✓ Re-Approve Continuous Replans</div>
            </div>
          </div>

          <div className="p-4 rounded border border-slate-200 bg-slate-50 space-y-2">
            <div className="font-bold text-slate-900 text-sm">Administrator</div>
            <p className="text-slate-600 text-[11px]">Full platform administrative jurisdiction and cryptographic key management.</p>
            <div className="text-[11px] text-slate-500 space-y-1 pt-2 border-t border-slate-200">
              <div>✓ System-Wide Privileges</div>
              <div>✓ API Key Configuration</div>
              <div>✓ Seed Data World Resets</div>
              <div>✓ User Role Assignment</div>
            </div>
          </div>
        </div>
      </div>

      {/* User Accounts Registry */}
      <div className="bg-white rounded-md border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <span className="font-bold text-slate-900 text-sm">Registered Operations Staff</span>
          <span className="text-xs text-slate-500">Active Session: <b>{currentUser?.full_name}</b> ({currentUser?.role_name})</span>
        </div>

        <table className="w-full text-left text-xs border-collapse">
          <thead className="bg-slate-50 border-b border-slate-200 font-bold text-slate-600 text-[11px] uppercase tracking-wider">
            <tr>
              <th className="py-3 px-4">Name / Official</th>
              <th className="py-3 px-4">Work Email</th>
              <th className="py-3 px-4">Assigned Role</th>
              <th className="py-3 px-4">Dispatch Clearance</th>
              <th className="py-3 px-4 text-right">Switch Active Role</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {users.map(u => {
              const isCurrent = currentUser?.id === u.id;
              const isCmd = u.role_name === 'INCIDENT_COMMANDER';

              return (
                <tr key={u.id} className="hover:bg-slate-50/70 transition">
                  <td className="py-3 px-4 font-bold text-slate-900">
                    {u.full_name}
                  </td>
                  <td className="py-3 px-4 text-slate-600 font-mono text-[11px]">
                    {u.email}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                      isCmd ? 'bg-blue-50 text-blue-800 border border-blue-200' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {u.role_name}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    {u.can_approve_dispatch ? (
                      <span className="text-emerald-700 font-semibold flex items-center gap-1">
                        <Check className="w-3.5 h-3.5" />
                        Authorized
                      </span>
                    ) : (
                      <span className="text-slate-400">Restricted</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => switchRole(u.role_name)}
                      className="px-3 py-1 rounded border border-slate-200 bg-white hover:bg-slate-100 text-slate-700 text-[11px] font-semibold cursor-pointer shadow-xs"
                    >
                      {isCurrent ? 'Active Session' : `Switch to ${u.role_name}`}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
