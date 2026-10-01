import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Flame, Truck, Home,
  Cpu, FileText, Sliders, History, Bell,
  Users, Settings
} from 'lucide-react';

const MODULES = [
  { path: '/command', label: 'Command Center', icon: LayoutDashboard, exact: true },
  { path: '/command/incidents', label: 'Incident Intelligence', icon: Flame },
  { path: '/command/resources', label: 'Resource Command', icon: Truck },
  { path: '/command/shelters', label: 'Shelter Network', icon: Home },
  { path: '/command/agents', label: 'Agent Observatory', icon: Cpu },
  { path: '/command/plans', label: 'Response Plans', icon: FileText },
  { path: '/command/simulation', label: 'Simulation Control', icon: Sliders },
  { path: '/command/audit', label: 'Audit & History', icon: History },
  { path: '/command/alerts', label: 'Alert Center', icon: Bell },
  { path: '/command/users', label: 'User & Roles', icon: Users },
  { path: '/command/settings', label: 'System Settings', icon: Settings },
];

export const Navbar: React.FC = () => {
  return (
    <nav className="bg-white border-b border-slate-200 px-4 overflow-x-auto scrollbar-none">
      <div className="flex space-x-1 min-w-max py-1.5">
        {MODULES.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.exact}
              className={({ isActive }) => `
                flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition
                ${isActive
                  ? 'bg-blue-50 text-blue-700 font-bold border border-blue-200 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }
              `}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
};
