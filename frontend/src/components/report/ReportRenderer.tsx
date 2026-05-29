import React from 'react';
import { ReportVersion } from '../../types/report';
import { SectionBlock } from './SectionBlock';
import { RichText } from './RichText';
import { SeverityBadge } from './SeverityBadge';
import { FindingCard } from './FindingCard';
import { ConfidenceBar } from './ConfidenceBar';
import { NextStepCard } from './NextStepCard';
import { MissingInfoCard } from './MissingInfoCard';
import { ReferencesFooter } from './ReferencesFooter';
import {
  FileText,
  Activity,
  CheckCircle,
  AlertTriangle,
  HelpCircle,
  List,
  BookOpen,
  Shield,
} from 'lucide-react';

interface ReportRendererProps {
  report?: ReportVersion | null;
}

export const ReportRenderer: React.FC<ReportRendererProps> = ({ report }) => {
  if (!report) {
    return (
      <div
        className="h-full flex items-center justify-center animate-fade-in"
        style={{
          backgroundColor: 'var(--surface-secondary)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-2)',
        }}
      >
        <div className="text-center p-8 max-w-sm">
          <FileText className="w-10 h-10 mx-auto mb-4" style={{ color: 'var(--border-strong)' }} />
          <h3 className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>No Report Selected</h3>
          <p className="text-[13px] leading-relaxed" style={{ color: 'var(--text-muted)' }}>
            Select a case or generate a new reasoning report to view clinical insights.
          </p>
        </div>
      </div>
    );
  }

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Unknown Date';
    try {
      return new Date(dateStr).toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  const citations = report.citations || [];

  return (
    <div
      className="bg-white overflow-hidden flex flex-col h-full max-h-full animate-fade-up"
      style={{
        border: '1px solid var(--border-default)',
        borderRadius: 'var(--radius-1)', // sharp corners for clinical feel
        boxShadow: 'var(--cf-shadow-card)',
      }}
    >
      {/* ── Report Header ────────────────────────────────────────── */}
      <div
        className="p-6 sm:p-8 shrink-0"
        style={{
          backgroundColor: 'var(--surface-primary)',
          borderBottom: '1px solid var(--border-subtle)',
        }}
      >
        <div className="flex justify-between items-start gap-4">
          <div>
            <h2
              className="text-2xl font-report font-semibold tracking-tight mb-2"
              style={{ color: 'var(--aletheia-navy)' }}
            >
              Clinical Reasoning Report
            </h2>
            <div className="flex items-center gap-3 text-[11px] font-medium tracking-widest uppercase" style={{ color: 'var(--text-muted)' }}>
              <span className="badge-secondary">v{report.version_number || 1}</span>
              <span>Generated: {formatDate(report.created_at)}</span>
            </div>
          </div>

          <div className="flex flex-col items-end gap-2 shrink-0 mt-1">
            {report.ai_provider && report.ai_model && (
              <div className="badge-primary" style={{ fontSize: '10px' }}>
                {report.ai_provider} · {report.ai_model}
              </div>
            )}
            {report.grounding_used && (
              <div className="badge-stable flex items-center gap-1" style={{ fontSize: '10px' }}>
                <Shield className="w-2.5 h-2.5" /> Grounded
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Report Body (Editorial Mode) ─────────────────────────── */}
      <div className="p-6 sm:p-8 overflow-y-auto flex-1 space-y-10 bg-white">
        
        {/* 1. Clinical Summary */}
        {report.summary && (
          <SectionBlock 
            title="Clinical Summary" 
            icon={<FileText className="w-4 h-4" style={{ color: 'var(--state-info)' }} />}
          >
            <div
              className="p-6 relative text-justify report-body"
              style={{
                backgroundColor: 'var(--surface-primary)',
                border: '1px solid var(--border-default)',
                borderRadius: 'var(--radius-1)',
              }}
            >
              <div className="float-right ml-4 mb-2">
                <SeverityBadge severity={report.summary.severity} />
              </div>
              <RichText 
                text={report.summary.overview} 
                citations={citations} 
                className="mt-0"
              />
            </div>
          </SectionBlock>
        )}

        {/* Findings Grid */}
        {(report.supporting_findings?.length > 0 || report.contradictory_findings?.length > 0) && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            
            {/* 2. Supporting Findings */}
            {report.supporting_findings?.length > 0 && (
              <SectionBlock
                title="Supporting Findings"
                icon={<CheckCircle className="w-4 h-4" style={{ color: 'var(--state-stable)' }} />}
              >
                <div className="space-y-3">
                  {report.supporting_findings.map((finding, idx) => (
                    <FindingCard key={idx} finding={finding} type="supporting" citations={citations} />
                  ))}
                </div>
              </SectionBlock>
            )}

            {/* 3. Contradictory Findings */}
            {report.contradictory_findings?.length > 0 && (
              <SectionBlock
                title="Contradictory Findings"
                icon={<AlertTriangle className="w-4 h-4" style={{ color: 'var(--state-declined)' }} />}
              >
                <div className="space-y-3">
                  {report.contradictory_findings.map((finding, idx) => (
                    <FindingCard key={idx} finding={finding} type="contradictory" citations={citations} />
                  ))}
                </div>
              </SectionBlock>
            )}

          </div>
        )}

        {/* 4. Assessment & Differentials */}
        {report.differentials?.length > 0 && (
          <SectionBlock 
            title="Assessment & Differentials" 
            icon={<Activity className="w-4 h-4" style={{ color: 'var(--state-info)' }} />}
          >
            <div className="space-y-3 mt-2">
              {report.differentials.map((dx, idx) => (
                <ConfidenceBar key={idx} differential={dx} citations={citations} />
              ))}
            </div>
          </SectionBlock>
        )}

        {/* 5. Suggested Next Steps */}
        {report.next_steps?.length > 0 && (
          <div id="suggested-next-steps">
          <SectionBlock 
            title="Suggested Next Steps" 
            icon={<List className="w-4 h-4" style={{ color: 'var(--state-info)' }} />}
          >
            <div className="space-y-3">
              {report.next_steps.map((step, idx) => (
                <NextStepCard key={idx} step={step} index={idx} citations={citations} />
              ))}
            </div>
          </SectionBlock>
          </div>
        )}

        {/* 6. Missing Information */}
        {report.missing_information?.length > 0 && (
          <SectionBlock
            title="Missing Information"
            icon={<HelpCircle className="w-4 h-4" style={{ color: 'var(--text-secondary)' }} />}
          >
            <div className="space-y-3">
              {report.missing_information.map((item, idx) => (
                <MissingInfoCard key={idx} item={item} citations={citations} />
              ))}
            </div>
          </SectionBlock>
        )}

        {/* 7. References */}
        {report.citations?.length > 0 && (
          <SectionBlock 
            title="References" 
            icon={<BookOpen className="w-4 h-4" style={{ color: 'var(--state-info)' }} />}
          >
            <ReferencesFooter citations={report.citations} />
          </SectionBlock>
        )}

      </div>
    </div>
  );
};
