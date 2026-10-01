import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, ArrowLeft } from 'lucide-react';

export const PrivacyPolicy: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#FBFBFB] text-[#0F172A] py-12 px-6">
      <div className="max-w-3xl mx-auto bg-white p-8 sm:p-12 rounded-md border border-slate-200 shadow-xs">
        <Link to="/" className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800 mb-6">
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Homepage</span>
        </Link>

        <div className="flex items-center gap-2 mb-2">
          <Shield className="w-6 h-6 text-blue-600" />
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">Privacy Policy</h1>
        </div>
        <p className="text-xs text-slate-500 mb-8 font-mono">Last Updated: September 2026 | Document Reference: RESQ-POL-001</p>

        <div className="space-y-6 text-xs text-slate-700 leading-relaxed">
          <section>
            <h2 className="text-sm font-bold text-slate-900 mb-2">1. Scope and Demonstration Environment</h2>
            <p>
              This Privacy Policy governs the RESQ Intelligent Disaster Response Coordination Platform.
              In this demonstration environment, all geographic references to Suryanagar, India,
              and associated emergency reports, casualties, and coordinates represent synthetic simulation data.
              No personally identifiable information (PII) of real private citizens is harvested or retained.
            </p>
          </section>

          <section>
            <h2 className="text-sm font-bold text-slate-900 mb-2">2. Data Collected by the Platform</h2>
            <p>During platform operation, RESQ collects:</p>
            <ul className="list-disc pl-5 mt-1.5 space-y-1">
              <li>Operator credentials (system usernames, work emails, and role entitlements).</li>
              <li>Incident attributes (synthetic geographic coordinates, disaster classification, damage indicators).</li>
              <li>Fleet telemetry (mock vehicle identifiers, base locations, and operational availability).</li>
              <li>Audit trail metadata (timestamps of plan formulations, agent runs, and dispatch authorizations).</li>
            </ul>
          </section>

          <section>
            <h2 className="text-sm font-bold text-slate-900 mb-2">3. Purpose of Processing</h2>
            <p>
              Operational data is processed solely for tactical emergency decision support, including calculating
              safe transit routes, avoiding road obstructions, matching resource capabilities, and verifying shelter headroom.
            </p>
          </section>

          <section>
            <h2 className="text-sm font-bold text-slate-900 mb-2">4. Artificial Intelligence Processing</h2>
            <p>
              RESQ incorporates Google Gemini models via authenticated backend proxies. Only anonymized incident
              summaries and capability parameters are transmitted to the model provider. API keys remain secured
              strictly on the server side and are never exposed to browser clients.
            </p>
          </section>

          <section>
            <h2 className="text-sm font-bold text-slate-900 mb-2">5. Data Retention and Security Practices</h2>
            <p>
              Database records are retained during active scenario execution and may be reset upon administrative command.
              Industry standard cryptographic hashing (bcrypt) is used for stored passwords, and token-based JSON Web Tokens (JWT)
              enforce role-based access control.
            </p>
          </section>

          <section>
            <h2 className="text-sm font-bold text-slate-900 mb-2">6. User Rights and Inquiries</h2>
            <p>
              Authorized system operators may review their audit trail entries and account status through the Command Center.
              For privacy inquiries regarding deployment in production municipal environments, contact the designated
              data governance team at <code>privacy@resq.gov.in</code>.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};
