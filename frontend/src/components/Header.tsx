import React from 'react';
import { useApp } from '../context/AppContext';
import { Shield, Radio, AlertTriangle, UserCheck, X } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export const Header: React.FC = () => {
  const {
    currentUser,
    switchRole,
    currentScenario,
    isConnected,
    activeNotification,
    clearNotification
  } = useApp();

  const location = useLocation();
  const isPublic = location.pathname === '/' || location.pathname.startsWith('/legal');

  return (
    <header className="border-b border-slate-200 bg-white sticky top-0 z-50">
      {/* Top Banner: SIMULATION MODE Notice */}
      <div className="bg-slate-900 text-slate-200 px-4 py-1 text-xs flex items-center justify-between font-mono">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30">
            <AlertTriangle className="w-3 h-3" />
            SIMULATION MODE
          </span>
          <span className="text-slate-400 hidden sm:inline">
            Fictional Geography: Suryanagar, India. Not a live emergency dispatcher.
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-amber-400 animate-pulse'}`} />
            <span className="text-slate-300">{isConnected ? 'TELEMETRY LIVE' : 'CONNECTING...'}</span>
          </div>
          <span className="text-slate-400">TICK: {currentScenario?.current_tick ?? 0}</span>
        </div>
      </div>

      {/* Main Bar */}
      <div className="px-4 py-2.5 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2 text-decoration-none">
            <img src="/favicon.svg" alt="RESQ" className="w-8 h-8 rounded" />
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold tracking-tight text-slate-900 text-lg leading-none">RESQ</span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                  COMMAND
                </span>
              </div>
              <p className="text-[11px] text-slate-500 leading-tight hidden md:block">
                Intelligent Disaster Response Coordination Platform
              </p>
            </div>
          </Link>

          {/* Active Scenario Badge */}
          {currentScenario && (
            <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-50 border border-slate-200 text-xs">
              <Radio className="w-3.5 h-3.5 text-blue-600" />
              <span className="text-slate-500">Scenario:</span>
              <span className="font-semibold text-slate-800 capitalize">{currentScenario.disaster_type}</span>
              <span className="text-slate-400">({currentScenario.name})</span>
            </div>
          )}
        </div>

        {/* Navigation & Role Controls */}
        <div className="flex items-center gap-3">
          {!isPublic && (
            <Link
              to="/"
              className="text-xs text-slate-600 hover:text-slate-900 px-2 py-1 rounded hover:bg-slate-100 hidden sm:inline"
            >
              Public Overview
            </Link>
          )}

          {isPublic && (
            <Link
              to="/command"
              className="text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded transition shadow-sm"
            >
              Enter Command Center
            </Link>
          )}

          {/* Role Switcher */}
          <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-md border border-slate-200 text-xs">
            <div className="flex items-center gap-1 px-1.5 text-slate-500 font-medium">
              <UserCheck className="w-3.5 h-3.5 text-slate-700" />
              <span className="hidden md:inline">Role:</span>
            </div>
            {(['INCIDENT_COMMANDER', 'OPERATOR', 'VIEWER'] as const).map((r) => {
              const active = currentUser?.role_name === r;
              return (
                <button
                  key={r}
                  onClick={() => switchRole(r)}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition cursor-pointer ${
                    active
                      ? 'bg-white text-blue-700 font-bold shadow-xs border border-slate-200'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  title={`Switch active session role to ${r}`}
                >
                  {r === 'INCIDENT_COMMANDER' ? 'Commander' : r === 'OPERATOR' ? 'Operator' : 'Viewer'}
                </button>
              );
            })}
          </div>

          {/* Commander Authority Badge */}
          {currentUser?.can_approve_dispatch && (
            <div className="hidden xl:flex items-center gap-1 px-2 py-1 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 text-[11px] font-semibold">
              <Shield className="w-3.5 h-3.5 text-emerald-600" />
              <span>Dispatch Authority Active</span>
            </div>
          )}
        </div>
      </div>

      {/* Real-time Notification Banner */}
      {activeNotification && (
        <div className="bg-blue-50 border-t border-b border-blue-200 px-4 py-1.5 flex items-center justify-between text-xs text-blue-900 animate-fadeIn">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping" />
            <span className="font-medium">{activeNotification}</span>
          </div>
          <button
            onClick={clearNotification}
            className="text-blue-500 hover:text-blue-800 p-0.5 cursor-pointer"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </header>
  );
};
