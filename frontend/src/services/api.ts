import type {
  User, Incident, Resource, Shelter, RoadSegment, Route,
  ResponsePlan, AgentRun, AgentDefinition, SimulationScenario,
  Alert, AuditLog, OperationalKPIs
} from '../types';

let RAW_API_URL = import.meta.env.VITE_API_URL || '';
if (RAW_API_URL && !RAW_API_URL.startsWith('http://') && !RAW_API_URL.startsWith('https://')) {
  RAW_API_URL = `https://${RAW_API_URL}`;
}
const API_BASE = RAW_API_URL ? `${RAW_API_URL.replace(/\/$/, '')}/api` : '/api';

export const api = {
  // Auth
  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`);
    if (!res.ok) throw new Error('Failed to fetch current user');
    return res.json();
  },

  async switchRole(roleName: string): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/switch-demo-role`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role_name: roleName })
    });
    if (!res.ok) throw new Error('Failed to switch demo role');
    const data = await res.json();
    return data.user;
  },

  async listUsers(): Promise<User[]> {
    const res = await fetch(`${API_BASE}/auth/users`);
    if (!res.ok) return [];
    return res.json();
  },

  // Operational KPIs & Alerts
  async getKPIs(): Promise<OperationalKPIs> {
    const res = await fetch(`${API_BASE}/operational/kpis`);
    if (!res.ok) throw new Error('Failed to fetch KPIs');
    return res.json();
  },

  async listAlerts(): Promise<Alert[]> {
    const res = await fetch(`${API_BASE}/operational/alerts`);
    if (!res.ok) return [];
    return res.json();
  },

  async acknowledgeAlert(alertId: string): Promise<Alert> {
    const res = await fetch(`${API_BASE}/operational/alerts/${alertId}/acknowledge`, { method: 'POST' });
    return res.json();
  },

  async listAuditLogs(): Promise<AuditLog[]> {
    const res = await fetch(`${API_BASE}/operational/audit-logs`);
    if (!res.ok) return [];
    return res.json();
  },

  // Incidents
  async listIncidents(): Promise<Incident[]> {
    const res = await fetch(`${API_BASE}/incidents`);
    if (!res.ok) return [];
    return res.json();
  },

  async getIncident(id: string): Promise<Incident> {
    const res = await fetch(`${API_BASE}/incidents/${id}`);
    return res.json();
  },

  async runIncidentPipeline(incidentId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/incidents/${incidentId}/run-pipeline`, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Pipeline execution failed');
    }
    return res.json();
  },

  // Resources
  async listResources(): Promise<Resource[]> {
    const res = await fetch(`${API_BASE}/resources`);
    if (!res.ok) return [];
    return res.json();
  },

  async updateResourceStatus(id: string, status: string): Promise<Resource> {
    const res = await fetch(`${API_BASE}/resources/${id}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    return res.json();
  },

  // Shelters
  async listShelters(): Promise<Shelter[]> {
    const res = await fetch(`${API_BASE}/shelters`);
    if (!res.ok) return [];
    return res.json();
  },

  async recordShelterIntake(id: string, intake_count: number): Promise<Shelter> {
    const res = await fetch(`${API_BASE}/shelters/${id}/intake`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ intake_count })
    });
    return res.json();
  },

  // Roads & Routes
  async listRoadSegments(): Promise<RoadSegment[]> {
    const res = await fetch(`${API_BASE}/roads/segments`);
    if (!res.ok) return [];
    return res.json();
  },

  async listRoutes(): Promise<Route[]> {
    const res = await fetch(`${API_BASE}/roads/routes`);
    if (!res.ok) return [];
    return res.json();
  },

  // Response Plans
  async listPlans(): Promise<ResponsePlan[]> {
    const res = await fetch(`${API_BASE}/plans`);
    if (!res.ok) return [];
    return res.json();
  },

  async approvePlan(planId: string, notes?: string): Promise<ResponsePlan> {
    const res = await fetch(`${API_BASE}/plans/${planId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Dispatch approval rejected');
    }
    return res.json();
  },

  async rejectPlan(planId: string, notes?: string): Promise<ResponsePlan> {
    const res = await fetch(`${API_BASE}/plans/${planId}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes })
    });
    return res.json();
  },

  // Agent Observatory
  async getAgentDefinitions(): Promise<AgentDefinition[]> {
    const res = await fetch(`${API_BASE}/agents/definitions`);
    if (!res.ok) return [];
    return res.json();
  },

  async listAgentRuns(): Promise<AgentRun[]> {
    const res = await fetch(`${API_BASE}/agents/runs`);
    if (!res.ok) return [];
    return res.json();
  },

  // Simulation Control
  async listScenarios(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/simulation/scenarios/available`);
    return res.json();
  },

  async getCurrentScenario(): Promise<SimulationScenario | null> {
    const res = await fetch(`${API_BASE}/simulation/current`);
    if (!res.ok) return null;
    return res.json();
  },

  async loadScenario(disasterType: string): Promise<SimulationScenario> {
    const res = await fetch(`${API_BASE}/simulation/load`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ disaster_type: disasterType })
    });
    return res.json();
  },

  async startSimulation(): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/start`, { method: 'POST' });
    return res.json();
  },

  async pauseSimulation(): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/pause`, { method: 'POST' });
    return res.json();
  },

  async resumeSimulation(): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/resume`, { method: 'POST' });
    return res.json();
  },

  async resetSimulation(): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/reset`, { method: 'POST' });
    return res.json();
  },

  async advanceNextEvent(): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/next-event`, { method: 'POST' });
    return res.json();
  },

  async setSimulationSpeed(multiplier: number): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/speed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ multiplier })
    });
    return res.json();
  },

  async injectHazard(segmentCode: string, blockageType: string, description: string): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/inject-hazard`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        segment_code: segmentCode,
        blockage_type: blockageType,
        description
      })
    });
    return res.json();
  }
};
