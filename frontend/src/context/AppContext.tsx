import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import { wsClient } from '../services/websocket';
import type {
  User, Incident, Resource, Shelter, RoadSegment, Route,
  ResponsePlan, AgentRun, SimulationScenario, Alert, AuditLog, OperationalKPIs
} from '../types';

interface AppContextType {
  currentUser: User | null;
  switchRole: (role: string) => Promise<void>;
  kpis: OperationalKPIs | null;
  currentScenario: SimulationScenario | null;
  incidents: Incident[];
  resources: Resource[];
  shelters: Shelter[];
  roadSegments: RoadSegment[];
  routes: Route[];
  plans: ResponsePlan[];
  agentRuns: AgentRun[];
  alerts: Alert[];
  auditLogs: AuditLog[];
  isConnected: boolean;
  activeNotification: string | null;
  clearNotification: () => void;
  // Simulation Controls
  loadScenario: (type: string) => Promise<void>;
  startSimulation: () => Promise<void>;
  pauseSimulation: () => Promise<void>;
  resumeSimulation: () => Promise<void>;
  resetSimulation: () => Promise<void>;
  advanceTick: () => Promise<void>;
  injectHazard: (segmentCode: string, blockageType: string, description: string) => Promise<void>;
  // Operations
  runIncidentPipeline: (incidentId: string) => Promise<void>;
  approvePlan: (planId: string, notes?: string) => Promise<void>;
  rejectPlan: (planId: string, notes?: string) => Promise<void>;
  acknowledgeAlert: (alertId: string) => Promise<void>;
  refreshAll: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [kpis, setKpis] = useState<OperationalKPIs | null>(null);
  const [currentScenario, setCurrentScenario] = useState<SimulationScenario | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [shelters, setShelters] = useState<Shelter[]>([]);
  const [roadSegments, setRoadSegments] = useState<RoadSegment[]>([]);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [plans, setPlans] = useState<ResponsePlan[]>([]);
  const [agentRuns, setAgentRuns] = useState<AgentRun[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [activeNotification, setActiveNotification] = useState<string | null>(null);

  const clearNotification = () => setActiveNotification(null);

  const refreshAll = useCallback(async () => {
    try {
      const [u, k, sc, inc, res, sh, rds, rts, pls, ags, als, aud] = await Promise.all([
        api.getMe().catch(() => null),
        api.getKPIs().catch(() => null),
        api.getCurrentScenario().catch(() => null),
        api.listIncidents().catch(() => []),
        api.listResources().catch(() => []),
        api.listShelters().catch(() => []),
        api.listRoadSegments().catch(() => []),
        api.listRoutes().catch(() => []),
        api.listPlans().catch(() => []),
        api.listAgentRuns().catch(() => []),
        api.listAlerts().catch(() => []),
        api.listAuditLogs().catch(() => [])
      ]);

      if (u) setCurrentUser(u);
      if (k) setKpis(k);
      if (sc) setCurrentScenario(sc);
      setIncidents(inc);
      setResources(res);
      setShelters(sh);
      setRoadSegments(rds);
      setRoutes(rts);
      setPlans(pls);
      setAgentRuns(ags);
      setAlerts(als);
      setAuditLogs(aud);
    } catch (e) {
      console.error('Refresh error:', e);
    }
  }, []);

  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 6000);

    const unsubscribe = wsClient.subscribe((event) => {
      setIsConnected(true);
      if (event.type === 'system.disconnected') {
        setIsConnected(false);
      } else if (event.type === 'system.connected') {
        setIsConnected(true);
      } else if (event.type === 'route.updated' || event.type === 'response_plan.updated') {
        setActiveNotification('Continuous Replanning Active: Route compromise detected. Alternative corridor formulated.');
        refreshAll();
      } else if (event.type === 'dispatch.approved') {
        setActiveNotification(`Commander Dispatch Approved: Units mobilized for ${event.data?.title}.`);
        refreshAll();
      } else {
        refreshAll();
      }
    });

    return () => {
      clearInterval(interval);
      unsubscribe();
    };
  }, [refreshAll]);

  const switchRole = async (roleName: string) => {
    const user = await api.switchRole(roleName);
    setCurrentUser(user);
    setActiveNotification(`Role switched to ${roleName}`);
    refreshAll();
  };

  const loadScenario = async (type: string) => {
    const sc = await api.loadScenario(type);
    setCurrentScenario(sc);
    setActiveNotification(`Disaster scenario loaded: ${sc.name} (Suryanagar)`);
    refreshAll();
  };

  const startSimulation = async () => {
    await api.startSimulation();
    setActiveNotification('Simulation clock running.');
    refreshAll();
  };

  const pauseSimulation = async () => {
    await api.pauseSimulation();
    setActiveNotification('Simulation paused.');
    refreshAll();
  };

  const resumeSimulation = async () => {
    await api.resumeSimulation();
    setActiveNotification('Simulation resumed.');
    refreshAll();
  };

  const resetSimulation = async () => {
    await api.resetSimulation();
    setActiveNotification('Simulation reset to initial scenario baseline.');
    refreshAll();
  };

  const advanceTick = async () => {
    const res = await api.advanceNextEvent();
    setActiveNotification(`Simulation advanced to tick ${res.current_tick}`);
    refreshAll();
  };

  const injectHazard = async (segmentCode: string, blockageType: string, description: string) => {
    await api.injectHazard(segmentCode, blockageType, description);
    setActiveNotification(`Hazard injected on ${segmentCode}: Route Invalidation & Replanning triggered.`);
    refreshAll();
  };

  const runIncidentPipeline = async (incidentId: string) => {
    setActiveNotification('Multi-Agent Pipeline started: Situation -> Triage -> Resource -> Route -> Shelter -> Coordination -> Verification');
    await api.runIncidentPipeline(incidentId);
    setActiveNotification('Multi-Agent Pipeline complete: Verified Response Plan formulated.');
    refreshAll();
  };

  const approvePlan = async (planId: string, notes?: string) => {
    await api.approvePlan(planId, notes);
    setActiveNotification('Response Plan approved by Incident Commander. Resources deployed.');
    refreshAll();
  };

  const rejectPlan = async (planId: string, notes?: string) => {
    await api.rejectPlan(planId, notes);
    setActiveNotification('Response Plan rejected.');
    refreshAll();
  };

  const acknowledgeAlert = async (alertId: string) => {
    await api.acknowledgeAlert(alertId);
    refreshAll();
  };

  return (
    <AppContext.Provider
      value={{
        currentUser,
        switchRole,
        kpis,
        currentScenario,
        incidents,
        resources,
        shelters,
        roadSegments,
        routes,
        plans,
        agentRuns,
        alerts,
        auditLogs,
        isConnected,
        activeNotification,
        clearNotification,
        loadScenario,
        startSimulation,
        pauseSimulation,
        resumeSimulation,
        resetSimulation,
        advanceTick,
        injectHazard,
        runIncidentPipeline,
        approvePlan,
        rejectPlan,
        acknowledgeAlert,
        refreshAll
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within an AppProvider');
  return context;
};
