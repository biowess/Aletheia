import React, { useState } from 'react';
import { DifferentialDiagnosis, Citation } from '../../types';
import { RichText } from './RichText';
import { ChevronDown, ChevronRight, CheckCircle2, XCircle } from 'lucide-react';

interface ConfidenceBarProps {
  differential: DifferentialDiagnosis;
  citations: Citation[];
}

export const ConfidenceBar: React.FC<ConfidenceBarProps> = ({ differential, citations }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const percent = Math.max(0, Math.min(100, differential.confidence * 100));

  let barColor = 'var(--border-strong)';
  let badgeClass = 'badge-low';

  if (differential.confidence >= 0.75) {
    barColor = 'var(--aletheia-navy)'; // deep navy for high
    badgeClass = 'badge-high';
  } else if (differential.confidence >= 0.5) {
    barColor = 'var(--aletheia-slate)'; // slate for medium
    badgeClass = 'badge-medium';
  }

  const getLikelihoodLabel = (conf: number) => {
    if (conf >= 0.75) return 'High Likelihood';
    if (conf >= 0.5) return 'Moderate Likelihood';
    if (conf >= 0.25) return 'Possible';
    return 'Unlikely';
  };

  return (
    <div
      className="mb-4 bg-white overflow-hidden transition-all"
      style={{
        border: '1px solid var(--border-default)',
        borderRadius: 'var(--radius-1)',
      }}
    >
      <div
        className="p-4 cursor-pointer select-none transition-colors"
        style={{
          backgroundColor: isExpanded ? 'var(--surface-secondary)' : 'var(--surface-primary)',
        }}
        onClick={() => setIsExpanded(!isExpanded)}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.backgroundColor = 'var(--surface-secondary)';
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.backgroundColor = isExpanded ? 'var(--surface-secondary)' : 'var(--surface-primary)';
        }}
      >
        <div className="flex justify-between items-start mb-3 gap-4">
          <div className="flex items-center gap-2">
            <button className="text-[var(--text-muted)] focus:outline-none focus-visible:ring-1 ring-[var(--state-info)] rounded-sm">
              {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </button>
            <h4
              className="font-semibold text-sm leading-tight"
              style={{ color: 'var(--text-primary)', letterSpacing: '-0.01em' }}
            >
              {differential.diagnosis}
            </h4>
          </div>
          <span className={`${badgeClass} whitespace-nowrap`}>
            {getLikelihoodLabel(differential.confidence)} <span className="ml-1 num-tabular">({percent.toFixed(0)}%)</span>
          </span>
        </div>

        {/* Clinical Confidence Bar */}
        <div
          className="h-1.5 overflow-hidden ml-6"
          style={{
            backgroundColor: 'var(--surface-muted)',
            borderRadius: 'var(--radius-1)',
          }}
        >
          <div
            className="h-full transition-all"
            style={{
              width: `${percent}%`,
              backgroundColor: barColor,
              borderRadius: 'var(--radius-1)',
              transitionDuration: 'var(--motion-slow)',
              transitionTimingFunction: 'var(--ease-soft)',
            }}
          />
        </div>
      </div>

      {isExpanded && (
        <div
          className="px-5 pb-5 ml-6 pt-4 animate-fade-in"
          style={{ borderTop: '1px solid var(--border-subtle)' }}
        >
          <div className="mb-5">
            <h5 className="text-[10px] font-semibold mb-2 uppercase tracking-widest text-[var(--text-muted)]">
              Clinical Reasoning
            </h5>
            <div className="text-[13px] leading-relaxed text-[var(--text-primary)]">
              <RichText text={differential.reasoning} citations={citations} />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {differential.supporting_evidence && differential.supporting_evidence.length > 0 && (
              <div>
                <h5 className="text-[10px] font-semibold mb-2 uppercase tracking-widest flex items-center gap-1.5" style={{ color: 'var(--state-stable)' }}>
                  <CheckCircle2 className="w-3 h-3" /> Supporting
                </h5>
                <ul className="list-disc list-outside ml-4 text-[13px] leading-relaxed space-y-1 text-[var(--text-secondary)]">
                  {differential.supporting_evidence.map((ev, i) => (
                    <li key={i} className="pl-1">{ev}</li>
                  ))}
                </ul>
              </div>
            )}

            {differential.contradictory_evidence && differential.contradictory_evidence.length > 0 && (
              <div>
                <h5 className="text-[10px] font-semibold mb-2 uppercase tracking-widest flex items-center gap-1.5" style={{ color: 'var(--state-declined)' }}>
                  <XCircle className="w-3 h-3" /> Contradictory
                </h5>
                <ul className="list-disc list-outside ml-4 text-[13px] leading-relaxed space-y-1 text-[var(--text-secondary)]">
                  {differential.contradictory_evidence.map((ev, i) => (
                    <li key={i} className="pl-1">{ev}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
