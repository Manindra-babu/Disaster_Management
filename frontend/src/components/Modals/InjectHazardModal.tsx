import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { AlertTriangle, X, ShieldAlert } from 'lucide-react';

interface InjectHazardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const InjectHazardModal: React.FC<InjectHazardModalProps> = ({ isOpen, onClose }) => {
  const { roadSegments, injectHazard } = useApp();
  const [selectedSegment, setSelectedSegment] = useState<string>('RS-09');
  const [hazardType, setHazardType] = useState<string>('FLOODED');
  const [description, setDescription] = useState<string>(
    'Rapid water level surge breached flood dyke. Carriageway submerged under 80cm torrent.'
  );
  const [loading, setLoading] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await injectHazard(selectedSegment, hazardType, description);
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-md border border-slate-300 shadow-xl max-w-lg w-full overflow-hidden">
        {/* Header */}
        <div className="bg-red-50 border-b border-red-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-red-900 font-bold text-sm">
            <ShieldAlert className="w-5 h-5 text-red-600" />
            <span>Inject Hazard & Test Continuous Replanning</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 cursor-pointer">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4 text-xs">
          <div className="p-2.5 bg-amber-50 rounded border border-amber-200 text-amber-900 text-xs leading-relaxed">
            <b>Demonstration Note:</b> Introducing an unscheduled obstruction on an active transit corridor
            will immediately invalidate the existing response plan, trigger Route & Verification agents,
            calculate an alternative bypass, and request Commander re-approval.
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Target Road Segment:</label>
            <select
              value={selectedSegment}
              onChange={(e) => setSelectedSegment(e.target.value)}
              className="w-full border border-slate-300 rounded px-2.5 py-1.5 text-xs bg-white text-slate-900 focus:outline-blue-500"
            >
              {roadSegments.map((s) => (
                <option key={s.code} value={s.code}>
                  {s.code}: {s.name} ({s.road_type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Obstruction Type:</label>
            <select
              value={hazardType}
              onChange={(e) => setHazardType(e.target.value)}
              className="w-full border border-slate-300 rounded px-2.5 py-1.5 text-xs bg-white text-slate-900 focus:outline-blue-500"
            >
              <option value="FLOODED">Flooded & Submerged Carriageway</option>
              <option value="DEBRIS_BLOCKED">Structural Rubble / Concrete Debris</option>
              <option value="BRIDGE_COLLAPSE">Bridge Causeway Structural Failure</option>
              <option value="FIRE_CORRIDOR">Active Flame Front & Severe Smoke</option>
              <option value="LANDSLIDE_BLOCKED">Boulders & Saturated Mudflow</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Telemetry Sensor Notice:</label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full border border-slate-300 rounded px-2.5 py-1.5 text-xs text-slate-900 focus:outline-blue-500"
            />
          </div>

          <div className="pt-2 flex justify-end gap-2 border-t border-slate-200">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded border border-slate-300 text-slate-700 hover:bg-slate-50 cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-1.5 rounded bg-red-600 hover:bg-red-700 text-white font-semibold flex items-center gap-1.5 cursor-pointer shadow-xs disabled:opacity-50"
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>{loading ? 'Injecting...' : 'Inject Obstruction Now'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
