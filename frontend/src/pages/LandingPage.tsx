import React from 'react';
import { Link } from 'react-router-dom';
import {
  Shield, Cpu, Network, MapPin, Database,
  ArrowRight, CheckCircle2, Sliders, AlertTriangle, FileText
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#FBFBFB] text-[#0F172A]">
      {/* Hero Section */}
      <section className="relative px-6 py-20 md:py-28 max-w-6xl mx-auto border-b border-slate-200">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded bg-blue-50 border border-blue-200 text-blue-800 text-xs font-bold mb-6">
          <Shield className="w-3.5 h-3.5 text-blue-700" />
          <span>MULTI-AGENT EMERGENCY COORDINATION PLATFORM</span>
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tight text-slate-900 max-w-4xl leading-[1.1]">
          Coordinate the response. Not just the information.
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-slate-600 max-w-3xl leading-relaxed">
          RESQ connects incident intelligence, resource availability, route planning, shelter capacity,
          and verified response workflows in one operational environment.
        </p>

        <div className="mt-8 flex flex-wrap gap-4">
          <Link
            to="/command"
            className="px-6 py-3 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm flex items-center gap-2 transition shadow-sm"
          >
            <span>Explore the Command Center</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/command/simulation"
            className="px-6 py-3 rounded-md bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 font-semibold text-sm flex items-center gap-2 transition"
          >
            <Sliders className="w-4 h-4 text-slate-600" />
            <span>Run a Simulation</span>
          </Link>
        </div>

        <div className="mt-12 flex items-center gap-6 text-xs text-slate-500 font-medium">
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Authoritative Graph Routing</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Seven Specialized AI Agents</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Incident Commander Approval Required</span>
          </div>
        </div>
      </section>

      {/* Core Architectural Pillars */}
      <section className="px-6 py-16 max-w-6xl mx-auto border-b border-slate-200">
        <div className="mb-10">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Designed for High-Consequence Operational Realities
          </h2>
          <p className="mt-2 text-slate-600 text-sm max-w-2xl">
            Generic chatbots fail during emergencies because language models hallucinate asset numbers and road conditions.
            RESQ couples official Google Gemini reasoning with an authoritative deterministic world engine.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="p-6 rounded-md bg-white border border-slate-200 shadow-xs">
            <div className="w-10 h-10 rounded bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700 mb-4">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-base">Seven Specialized Agents</h3>
            <p className="mt-2 text-xs text-slate-600 leading-relaxed">
              Situation Intelligence, Triage Priority, Resource Allocation, Route Optimization, Shelter Headroom,
              Plan Coordination, and Independent Verification.
            </p>
          </div>

          <div className="p-6 rounded-md bg-white border border-slate-200 shadow-xs">
            <div className="w-10 h-10 rounded bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700 mb-4">
              <Database className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-base">Authoritative World Engine</h3>
            <p className="mt-2 text-xs text-slate-600 leading-relaxed">
              State transitions, resource positions, road closures, and shelter counts live in verified database records.
              AI agents inspect through tools, preventing invented facts.
            </p>
          </div>

          <div className="p-6 rounded-md bg-white border border-slate-200 shadow-xs">
            <div className="w-10 h-10 rounded bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700 mb-4">
              <Network className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-base">Continuous Replanning</h3>
            <p className="mt-2 text-xs text-slate-600 leading-relaxed">
              When a bridge collapses or flash floods submerge an arterial, RESQ automatically detects route compromise,
              coordinates recalculation, and requests Commander re-approval.
            </p>
          </div>
        </div>
      </section>

      {/* Five Supported Disaster Scenarios */}
      <section className="px-6 py-16 max-w-6xl mx-auto border-b border-slate-200">
        <div className="mb-10">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Supported Simulation Profiles for Suryanagar, India
          </h2>
          <p className="mt-2 text-slate-600 text-sm">
            Each scenario possesses tailored hydrological, seismic, wind, or terrain dynamics.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4 text-xs">
          <div className="p-4 rounded-md bg-white border border-slate-200 shadow-xs">
            <span className="font-bold text-blue-700 text-sm block mb-1">1. Flood</span>
            <p className="text-slate-600">
              Riverine surge, submerged causeways, boat dispatch, and medical extraction.
            </p>
          </div>

          <div className="p-4 rounded-md bg-white border border-slate-200 shadow-xs">
            <span className="font-bold text-teal-700 text-sm block mb-1">2. Cyclone</span>
            <p className="text-slate-600">
              145 km/h winds, coastal surge, power grid trips, and cyclone shelter intake.
            </p>
          </div>

          <div className="p-4 rounded-md bg-white border border-slate-200 shadow-xs">
            <span className="font-bold text-amber-700 text-sm block mb-1">3. Earthquake</span>
            <p className="text-slate-600">
              Masonry building collapse, trapped survivors, USAR extrication, and aftershocks.
            </p>
          </div>

          <div className="p-4 rounded-md bg-white border border-slate-200 shadow-xs">
            <span className="font-bold text-orange-700 text-sm block mb-1">4. Wildfire</span>
            <p className="text-slate-600">
              Northern ridge flame front, smoke exposure, water tankers, and corridor security.
            </p>
          </div>

          <div className="p-4 rounded-md bg-white border border-slate-200 shadow-xs">
            <span className="font-bold text-rose-700 text-sm block mb-1">5. Landslide</span>
            <p className="text-slate-600">
              Ghat road rockfall, stranded vehicles, high-angle rescue, and western bypass rerouting.
            </p>
          </div>
        </div>
      </section>

      {/* Safety Principles */}
      <section className="px-6 py-16 max-w-6xl mx-auto border-b border-slate-200">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Operational Safety Principles</h2>
        <div className="grid md:grid-cols-2 gap-4 text-xs text-slate-600 leading-relaxed">
          <div className="p-4 bg-slate-50 rounded border border-slate-200">
            <h4 className="font-bold text-slate-900 mb-1">Human-In-The-Loop Command</h4>
            <p>
              AI agents formulate, verify, and monitor plans. However, only an authorized human Incident Commander
              holds the cryptographic authority to execute physical unit dispatch.
            </p>
          </div>
          <div className="p-4 bg-slate-50 rounded border border-slate-200">
            <h4 className="font-bold text-slate-900 mb-1">Zero Double-Booking Guarantee</h4>
            <p>
              The Resource Allocation Agent and Verification Agent enforce deterministic locks on fleet inventory,
              preventing competing disaster zones from assigning the same ambulance or rescue craft.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-10 max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <div>
          <span className="font-bold text-slate-800">RESQ</span> | Intelligent Disaster Response Coordination Platform
          <p className="text-[11px] text-slate-400 mt-0.5">Demo Environment: Suryanagar Municipal Region (Simulation Mode)</p>
        </div>

        <div className="flex items-center gap-6">
          <Link to="/legal/privacy" className="hover:text-slate-800">Privacy Policy</Link>
          <Link to="/legal/terms" className="hover:text-slate-800">Terms and Conditions</Link>
          <Link to="/command" className="font-bold text-blue-600 hover:text-blue-800">Launch EOC</Link>
        </div>
      </footer>
    </div>
  );
};
