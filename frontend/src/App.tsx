import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { Header } from './components/Header';
import { Navbar } from './components/Navbar';

import { LandingPage } from './pages/LandingPage';
import { PrivacyPolicy } from './pages/PrivacyPolicy';
import { TermsConditions } from './pages/TermsConditions';

import { CommandCenter } from './pages/CommandCenter';
import { IncidentIntelligence } from './pages/IncidentIntelligence';
import { ResourceCommand } from './pages/ResourceCommand';
import { ShelterNetwork } from './pages/ShelterNetwork';
import { AgentObservatory } from './pages/AgentObservatory';
import { ResponsePlanManagement } from './pages/ResponsePlanManagement';
import { SimulationControl } from './pages/SimulationControl';
import { AuditHistory } from './pages/AuditHistory';
import { AlertCenter } from './pages/AlertCenter';
import { UserRoleManagement } from './pages/UserRoleManagement';
import { SystemSettings } from './pages/SystemSettings';

const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const isPublic = location.pathname === '/' || location.pathname.startsWith('/legal');

  return (
    <div className="min-h-screen bg-[#FBFBFB] flex flex-col text-[#0F172A]">
      <Header />
      {!isPublic && <Navbar />}
      <main className="flex-1">{children}</main>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AppProvider>
      <BrowserRouter>
        <AppLayout>
          <Routes>
            {/* Public Experiences */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/legal/privacy" element={<PrivacyPolicy />} />
            <Route path="/legal/terms" element={<TermsConditions />} />

            {/* Authenticated Emergency Operations Center Modules */}
            <Route path="/command" element={<CommandCenter />} />
            <Route path="/command/incidents" element={<IncidentIntelligence />} />
            <Route path="/command/resources" element={<ResourceCommand />} />
            <Route path="/command/shelters" element={<ShelterNetwork />} />
            <Route path="/command/agents" element={<AgentObservatory />} />
            <Route path="/command/plans" element={<ResponsePlanManagement />} />
            <Route path="/command/simulation" element={<SimulationControl />} />
            <Route path="/command/audit" element={<AuditHistory />} />
            <Route path="/command/alerts" element={<AlertCenter />} />
            <Route path="/command/users" element={<UserRoleManagement />} />
            <Route path="/command/settings" element={<SystemSettings />} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppLayout>
      </BrowserRouter>
    </AppProvider>
  );
};

export default App;
