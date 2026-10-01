import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, ArrowLeft, AlertTriangle } from 'lucide-react';

export const TermsConditions: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#FBFBFB] text-[#0F172A] py-12 px-6">
      <div className="max-w-3xl mx-auto bg-white p-8 sm:p-12 rounded-md border border-slate-200 shadow-xs">
        <Link to="/" className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800 mb-6">
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Homepage</span>
        </Link>

        <div className="flex items-center gap-2 mb-2">
          <FileText className="w-6 h-6 text-blue-600" />
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">Terms and Conditions</h1>
        </div>
        <p className="text-xs text-slate-500 mb-6 font-mono">Last Updated: September 2026 | Document Reference: RESQ-TOS-001</p>

        {/* Warning callout */}
        <div className="mb-8 p-3 rounded bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <b>Operational Notice:</b> RESQ is an intelligent decision-support and coordination system.
            It does not replace statutory emergency response authorities, civil defense directors, or emergency service dispatchers.
          </div>
        </div>

        <div className="space-y-6 text-xs text-slate-700 leading-relaxed">
          <section>
            <h2 className="text-sm font-bold text-slate-900 mb-2">1. Intended Purpose and Simulation Limitations</h2>
            <p>
              RESQ provides computational route optimization, capability matching, and multi-agent plan verification.
              All demonstration scenarios involving Suryanagar, India, are synthetic training exercises designed for
              evaluators, technical stakeholders, and operational planning teams. Fictional scenarios must never be
              represented as live civil emergencies.
            </p>
          </section>

          <section>
            <h2 className="text-sm font-bold text-slate-900 mb-2">2. Human Decision Authority</h2>
            <p>
              Automated multi-agent workflows generate recommendations and verification checks. However, final dispatch
              authorization remains strictly vested in authenticated human Incident Commanders. Automated systems do not
              possess unilateral deployment authority without human sign-off.
            </p>
          </section>

          <section>
            <h2 className="text-sm font-bold text-slate-900 mb-2">3. Continuous Replanning and Invalidation</h2>
            <p>
              When authoritative road state changes (such as flood inundation, bridge structural compromise, or rockfall debris),
              previously approved transit paths are invalidated. Commanders acknowledge that alternative routing recommendations
              must be reviewed upon secondary hazard occurrence.
            </p>
          </section>

          <section>
            <h2 className="text-sm font-bold text-slate-900 mb-2">4. Prohibited Misuse</h2>
            <p>
              Users are prohibited from transmitting fabricated distress calls, tampering with authoritative GIS graphs,
              bypassing cryptographic role checks, or misrepresenting simulation outputs as actual real-world directives.
            </p>
          </section>

          <section>
            <h2 className="text-sm font-bold text-slate-900 mb-2">5. Limitation of Liability</h2>
            <p>
              Under no circumstances shall the platform authors or contributing architects be liable for damages resulting
              from reliance on simulation data, telecommunication outages, or unverified field maneuvers.
            </p>
          </section>

          <section>
            <h2 className="text-sm font-bold text-slate-900 mb-2">6. Contact and Administrative Governance</h2>
            <p>
              Inquiries regarding enterprise licensing, high-availability deployments, or municipal integrations may be directed to{' '}
              <code>operations@resq.gov.in</code>.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};
