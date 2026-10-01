import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import {
  Sliders, Play, Pause, RotateCcw, FastForward,
  ShieldAlert, Radio, Wind, Droplets, Compass
} from 'lucide-react';
import { InjectHazardModal } from '../components/Modals/InjectHazardModal';

export const SimulationControl: React.FC = () => {
  const {
    currentScenario,
    startSimulation,
    pauseSimulation,
    resetSimulation,
    advanceTick,
    loadScenario
  } = useApp();

  const [scenarios, setScenarios] = useState<any[]>([]);
  const [speedMultiplier, setSpeedMultiplier] = useState<number>(1.0);
  const [isHazardModalOpen, setIsHazardModalOpen] = useState(false);

  useEffect(() => {
    api.listScenarios().then(setScenarios);
  }, []);

  const handleSpeedChange = async (speed: number) => {
    setSpeedMultiplier(speed);
    await api.setSimulationSpeed(speed);
  };

  const isRunning = currentScenario?.status === 'RUNNING';

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Sliders className="w-6 h-6 text-blue-600" />
          <span>Simulation Engine & Scenario Orchestration</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Deterministic world engine governing world time, weather telemetry, road conditions, and scheduled hazard injections for Suryanagar, India.
        </p>
      </div>

      {/* Main Control Panel */}
      <div className="bg-white rounded-md border border-slate-200 shadow-xs p-6 space-y-6 text-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900 text-base">Active World State:</span>
              <span className="px-2.5 py-0.5 rounded font-black text-xs bg-blue-50 text-blue-800 border border-blue-200 uppercase">
                {currentScenario?.disaster_type} ({currentScenario?.status})
              </span>
            </div>
            <div className="text-slate-500 mt-1">
              Current Simulation Tick: <b>{currentScenario?.current_tick ?? 0}</b> | Location: <b>Suryanagar Municipal Region</b>
            </div>
          </div>

          {/* Clock Operations */}
          <div className="flex flex-wrap items-center gap-2">
            {isRunning ? (
              <button
                onClick={pauseSimulation}
                className="px-4 py-2 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold flex items-center gap-1.5 cursor-pointer shadow-xs"
              >
                <Pause className="w-4 h-4 text-slate-600" />
                <span>Pause</span>
              </button>
            ) : (
              <button
                onClick={startSimulation}
                className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-bold flex items-center gap-1.5 cursor-pointer shadow-xs"
              >
                <Play className="w-4 h-4" />
                <span>Start Clock</span>
              </button>
            )}

            <button
              onClick={advanceTick}
              className="px-4 py-2 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold flex items-center gap-1.5 cursor-pointer shadow-xs"
            >
              <FastForward className="w-4 h-4 text-slate-600" />
              <span>Advance 1 Tick</span>
            </button>

            <button
              onClick={() => setIsHazardModalOpen(true)}
              className="px-4 py-2 rounded-md bg-red-600 hover:bg-red-700 text-white font-bold flex items-center gap-1.5 cursor-pointer shadow-xs"
            >
              <ShieldAlert className="w-4 h-4" />
              <span>Inject Hazard</span>
            </button>

            <button
              onClick={resetSimulation}
              className="px-3 py-2 rounded-md bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 font-medium flex items-center gap-1 cursor-pointer"
            >
              <RotateCcw className="w-4 h-4 text-slate-500" />
              <span>Reset</span>
            </button>
          </div>
        </div>

        {/* Speed Multiplier & Environmental Telemetry */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded bg-slate-50 border border-slate-200 space-y-2">
            <span className="font-bold text-slate-800 block">Simulation Execution Rate:</span>
            <div className="flex gap-2">
              {[1.0, 2.0, 5.0].map((spd) => (
                <button
                  key={spd}
                  onClick={() => handleSpeedChange(spd)}
                  className={`px-3 py-1.5 rounded text-xs font-bold transition cursor-pointer ${
                    speedMultiplier === spd
                      ? 'bg-blue-600 text-white shadow-xs'
                      : 'bg-white border border-slate-300 text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  {spd}x Speed
                </button>
              ))}
            </div>
            <p className="text-[11px] text-slate-500">
              Deterministic event ordering and reproducible seeds ensure consistent replayability.
            </p>
          </div>

          <div className="p-4 rounded bg-slate-50 border border-slate-200 space-y-1.5 text-slate-700">
            <span className="font-bold text-slate-800 block">Environmental Sensors (Suryanagar):</span>
            <div className="flex items-center gap-2">
              <Wind className="w-3.5 h-3.5 text-blue-500" />
              <span>Wind Velocity: <b>{currentScenario?.wind_speed_kmh} km/h</b></span>
            </div>
            <div className="flex items-center gap-2">
              <Droplets className="w-3.5 h-3.5 text-cyan-500" />
              <span>Precipitation Gauge: <b>{currentScenario?.rainfall_mm} mm/24h</b></span>
            </div>
            <div className="text-[11px] text-slate-500 pt-1 font-mono">{currentScenario?.weather_summary}</div>
          </div>
        </div>
      </div>

      {/* Scenario Selection Grid (5 Profiles) */}
      <div className="space-y-3">
        <h2 className="font-bold text-slate-900 text-sm uppercase tracking-wide">
          Select Disaster Scenario Profile
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 text-xs">
          {scenarios.map((sc) => {
            const isSelected = currentScenario?.disaster_type === sc.disaster_type;

            return (
              <div
                key={sc.disaster_type}
                className={`bg-white rounded-md border p-4 shadow-xs flex flex-col justify-between space-y-3 transition ${
                  isSelected ? 'border-blue-500 ring-2 ring-blue-100' : 'border-slate-200'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-slate-900 text-sm capitalize">{sc.disaster_type}</span>
                    {isSelected && (
                      <span className="w-2 h-2 rounded-full bg-blue-600" />
                    )}
                  </div>
                  <p className="text-slate-600 leading-relaxed text-[11px]">{sc.description}</p>
                </div>

                <button
                  onClick={() => loadScenario(sc.disaster_type)}
                  disabled={isSelected}
                  className={`w-full py-1.5 rounded font-bold text-xs transition cursor-pointer ${
                    isSelected
                      ? 'bg-slate-100 text-slate-400 cursor-default'
                      : 'bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200'
                  }`}
                >
                  {isSelected ? 'Loaded Active' : 'Load Scenario'}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      <InjectHazardModal
        isOpen={isHazardModalOpen}
        onClose={() => setIsHazardModalOpen(false)}
      />
    </div>
  );
};
