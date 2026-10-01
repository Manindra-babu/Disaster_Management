import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import {
  ReactFlow,
  Background,
  Controls,
  Node,
  Edge,
  MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Cpu, CheckCircle2, Clock, Terminal, ChevronRight, RefreshCw, Zap } from 'lucide-react';
import type { AgentRun } from '../types';

const INITIAL_NODES: Node[] = [
  {
    id: '1',
    type: 'default',
    position: { x: 50, y: 150 },
    data: { label: '1. Situation Intelligence Agent\n(De-duplication & Extraction)' },
    style: { background: '#EFF6FF', border: '1.5px solid #3B82F6', borderRadius: '6px', fontSize: '11px', fontWeight: 'bold', width: 200 }
  },
  {
    id: '2',
    type: 'default',
    position: { x: 290, y: 150 },
    data: { label: '2. Triage & Priority Agent\n(Deterministic Acuity Score)' },
    style: { background: '#FEF2F2', border: '1.5px solid #EF4444', borderRadius: '6px', fontSize: '11px', fontWeight: 'bold', width: 200 }
  },
  {
    id: '3',
    type: 'default',
    position: { x: 530, y: 70 },
    data: { label: '3. Resource Allocation Agent\n(Zero Double-Booking)' },
    style: { background: '#F0FDF4', border: '1.5px solid #22C55E', borderRadius: '6px', fontSize: '11px', fontWeight: 'bold', width: 200 }
  },
  {
    id: '4',
    type: 'default',
    position: { x: 530, y: 220 },
    data: { label: '4. Route Optimization Agent\n(Closure-Aware Pathfinding)' },
    style: { background: '#FAF5FF', border: '1.5px solid #A855F7', borderRadius: '6px', fontSize: '11px', fontWeight: 'bold', width: 200 }
  },
  {
    id: '5',
    type: 'default',
    position: { x: 770, y: 150 },
    data: { label: '5. Shelter & Capacity Agent\n(Headroom & Field Clinic)' },
    style: { background: '#EEF2FF', border: '1.5px solid #6366F1', borderRadius: '6px', fontSize: '11px', fontWeight: 'bold', width: 200 }
  },
  {
    id: '6',
    type: 'default',
    position: { x: 1010, y: 150 },
    data: { label: '6. Coordination Agent\n(Unified Plan Synthesis)' },
    style: { background: '#FFFBEB', border: '1.5px solid #F59E0B', borderRadius: '6px', fontSize: '11px', fontWeight: 'bold', width: 200 }
  },
  {
    id: '7',
    type: 'default',
    position: { x: 1250, y: 150 },
    data: { label: '7. Verification Agent\n(Ground-Truth Audit)' },
    style: { background: '#ECFDF5', border: '2px solid #059669', borderRadius: '6px', fontSize: '11px', fontWeight: 'bold', width: 200 }
  },
  {
    id: '8',
    type: 'default',
    position: { x: 1490, y: 150 },
    data: { label: 'Incident Commander\n(Dispatch Authorization)' },
    style: { background: '#0F172A', color: 'white', border: '2px solid #1E293B', borderRadius: '6px', fontSize: '11px', fontWeight: 'bold', width: 180 }
  }
];

const INITIAL_EDGES: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e2-3', source: '2', target: '3', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e2-4', source: '2', target: '4', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e3-5', source: '3', target: '5', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e4-5', source: '4', target: '5', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e5-6', source: '5', target: '6', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e6-7', source: '6', target: '7', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e7-8', source: '7', target: '8', animated: true, markerEnd: { type: MarkerType.ArrowClosed } }
];

export const AgentObservatory: React.FC = () => {
  const { agentRuns, refreshAll } = useApp();
  const [selectedRun, setSelectedRun] = useState<AgentRun | null>(agentRuns[0] || null);

  useEffect(() => {
    if (!selectedRun && agentRuns.length > 0) {
      setSelectedRun(agentRuns[0]);
    }
  }, [agentRuns, selectedRun]);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Cpu className="w-6 h-6 text-emerald-600" />
            <span>Agent Observatory & Execution Trace</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time multi-agent execution pipeline. Inspect typed input schemas, invoked tools, structured output payloads, and ground-truth audit verdicts.
          </p>
        </div>

        <button
          onClick={refreshAll}
          className="px-3 py-1.5 rounded border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold flex items-center gap-1.5 shadow-xs cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
          <span>Refresh Runs</span>
        </button>
      </div>

      {/* Interactive React Flow Orchestration Diagram */}
      <div className="bg-white rounded-md border border-slate-200 shadow-xs overflow-hidden">
        <div className="bg-slate-50 px-4 py-2.5 border-b border-slate-200 text-xs font-bold text-slate-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-blue-600" />
            <span>Multi-Agent Directed Orchestration Workflow</span>
          </div>
          <span className="text-[11px] text-slate-500">React Flow Interactive Topology</span>
        </div>

        <div style={{ height: '360px', width: '100%' }}>
          <ReactFlow
            nodes={INITIAL_NODES}
            edges={INITIAL_EDGES}
            fitView
            attributionPosition="bottom-right"
          >
            <Background color="#CBD5E1" gap={16} size={1} />
            <Controls showInteractive={false} />
          </ReactFlow>
        </div>
      </div>

      {/* Execution Telemetry Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Run History List (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-500 px-1">
            Recent Agent Execution Runs ({agentRuns.length})
          </div>

          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
            {agentRuns.map(run => {
              const isSelected = selectedRun?.id === run.id;
              const isLLM = run.execution_mode === 'GEMINI_LLM';

              return (
                <div
                  key={run.id}
                  onClick={() => setSelectedRun(run)}
                  className={`p-3 rounded border text-xs cursor-pointer transition ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50/40 shadow-xs'
                      : 'border-slate-200 bg-white hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{run.agent_name}</span>
                    <span className={`px-1.5 py-0.2 rounded font-bold text-[10px] ${
                      isLLM ? 'bg-purple-50 text-purple-700 border border-purple-200' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {run.execution_mode}
                    </span>
                  </div>

                  <p className="mt-1 text-slate-600 line-clamp-1">{run.decision_explanation}</p>

                  <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-100 pt-1.5">
                    <span className="flex items-center gap-1 text-slate-500">
                      <Clock className="w-3 h-3" />
                      {run.duration_ms.toFixed(1)} ms
                    </span>
                    <span>Tokens: <b>{run.tokens_used}</b></span>
                    <span>{new Date(run.created_at).toLocaleTimeString()}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Run Deep Inspection (7 cols) */}
        <div className="lg:col-span-7">
          {selectedRun ? (
            <div className="bg-white rounded-md border border-slate-200 shadow-xs p-5 space-y-4 text-xs">
              <div className="flex items-start justify-between border-b border-slate-200 pb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 text-base">{selectedRun.agent_name}</span>
                    <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-bold text-[10px] border border-emerald-200">
                      {selectedRun.status}
                    </span>
                  </div>
                  <div className="text-slate-500 text-[11px] mt-0.5">
                    Model: <b>{selectedRun.model_name}</b> | Duration: <b>{selectedRun.duration_ms} ms</b> | Mode: <b>{selectedRun.execution_mode}</b>
                  </div>
                </div>
              </div>

              {/* Decision Explanation */}
              <div>
                <label className="block font-bold text-slate-700 mb-1">Synthesized Decision & Operational Reasoning:</label>
                <div className="p-3 bg-slate-50 rounded border border-slate-200 text-slate-800 leading-relaxed font-sans">
                  {selectedRun.decision_explanation}
                </div>
              </div>

              {/* Structured Output JSON */}
              <div>
                <label className="block font-bold text-slate-700 mb-1 flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-blue-600" />
                  <span>Typed Structured Output Payload:</span>
                </label>
                <pre className="p-3 bg-slate-900 text-slate-200 rounded text-[11px] font-mono overflow-x-auto max-h-[220px]">
                  {(() => {
                    try {
                      return JSON.stringify(JSON.parse(selectedRun.structured_output_json || '{}'), null, 2);
                    } catch {
                      return selectedRun.structured_output_json || '{}';
                    }
                  })()}
                </pre>
              </div>

              {/* Invoked Events / Tools */}
              {selectedRun.events && selectedRun.events.length > 0 && (
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Tool Events & Execution Trace:</label>
                  <div className="space-y-1.5">
                    {selectedRun.events.map(ev => (
                      <div key={ev.id} className="p-2 rounded border border-slate-100 bg-slate-50 flex items-center justify-between text-[11px]">
                        <span className="font-semibold text-slate-700">{ev.event_type}</span>
                        <span className="text-slate-500">{ev.message}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500 bg-white rounded border border-slate-200">
              Select an agent execution trace from the left panel to inspect typed inputs, duration, and output schemas.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
