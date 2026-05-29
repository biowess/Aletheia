import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useReportStore } from '../../stores/reportStore';
import { FileText, AlertCircle, TrendingUp, Download, History, ChevronRight } from 'lucide-react';
import { ReportRenderer } from '../report/ReportRenderer';
import { DifferentialEvolution } from '../report/DifferentialEvolution';
import { ReportVersionList } from '../report/ReportVersionList';
import { downloadReportPDF } from '../../api/export';
import { useToast } from '../../hooks/useToast';
import { Spinner } from '../ui/Spinner';
import { ErrorBanner } from '../ui/ErrorBanner';
import { LoadingSkeleton } from '../ui/LoadingSkeleton';

export const ReasoningOutputPanel: React.FC = () => {
  const { reports, activeReport, setActiveReport, isGenerating, generationError } = useReportStore();
  const { showToast } = useToast();

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isEvolutionCollapsed, setIsEvolutionCollapsed] = useState(false);

  useEffect(() => {
    if (reports.length > 0 && !activeReport) {
      const sorted = [...reports].sort((a, b) => b.version_number - a.version_number);
      setActiveReport(sorted[0]);
    }
  }, [reports, activeReport, setActiveReport]);

  const sortedReports = useMemo(() => {
    return [...reports].sort((a, b) => b.version_number - a.version_number);
  }, [reports]);

  const mostRecentReport = sortedReports.length > 0 ? sortedReports[0] : null;

  const hasReports = reports.length > 0;
  const isShowingOlderVersion = !!(activeReport && mostRecentReport && activeReport.id !== mostRecentReport.id);
  const isJustGenerated = !!(activeReport && (Date.now() - new Date(activeReport.created_at).getTime() < 60000) && !isShowingOlderVersion);

  const scrollContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = 0;
    }
  }, [activeReport, isGenerating]);

  return (
    <div className="flex flex-col h-full relative" style={{ backgroundColor: 'var(--bg-secondary)' }}>
      {/* Full-panel loading overlay */}
      {isGenerating && (
        <div className="absolute inset-0 z-50 flex flex-col items-center justify-center backdrop-blur-[2px]" style={{ backgroundColor: 'rgba(249,251,253,0.8)' }}>
          <div
            className="flex flex-col items-center gap-4 p-8 animate-fade-up"
            style={{
              backgroundColor: 'var(--surface-primary)',
              borderRadius: 'var(--radius-2)',
              border: '1px solid var(--border-default)',
              boxShadow: 'var(--cf-shadow-elevated)',
            }}
          >
            <Spinner className="w-8 h-8" style={{ color: 'var(--aletheia-navy)' }} />
            <div className="text-center">
              <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Generating clinical report…</p>
              <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>This may take a few moments.</p>
            </div>
          </div>
        </div>
      )}

      {/* Header Area */}
      <div
        className="sticky top-0 z-20 flex-shrink-0"
        style={{
          backgroundColor: 'var(--surface-primary)',
          borderBottom: '1px solid var(--border-default)',
        }}
      >
        <div className="px-6 py-3 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <FileText className="w-4 h-4" style={{ color: 'var(--state-info)' }} />
            <h2 className="text-sm font-semibold tracking-tight" style={{ color: 'var(--aletheia-navy)' }}>Reasoning Output</h2>

            {isJustGenerated && (
              <span className="badge-primary animate-pulse text-[10px] ml-2">
                Just Generated
              </span>
            )}
          </div>

          {hasReports && (
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="btn-ghost"
              style={{
                height: '28px',
                padding: '0 10px',
                fontSize: '11px',
                backgroundColor: isSidebarOpen ? 'var(--surface-muted)' : 'transparent',
              }}
            >
              <History className="w-3.5 h-3.5" />
              History
              <ChevronRight
                className="w-3.5 h-3.5 transition-transform"
                style={{ transform: isSidebarOpen ? 'rotate(90deg)' : 'none', transitionDuration: 'var(--motion-fast)' }}
              />
            </button>
          )}
        </div>

        {/* Older version warning banner */}
        {isShowingOlderVersion && mostRecentReport && activeReport && (
          <div
            className="px-6 py-2.5 flex justify-between items-center"
            style={{
              backgroundColor: 'var(--bg-tertiary)',
              borderBottom: '1px solid var(--border-strong)',
            }}
          >
            <div className="flex items-center gap-2 text-xs font-medium" style={{ color: 'var(--text-primary)' }}>
              <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" style={{ color: 'var(--state-evolving)' }} />
              <span>
                Viewing historical version {activeReport.version_number}. Latest is v{mostRecentReport.version_number}.
              </span>
            </div>
            <button
              onClick={() => setActiveReport(mostRecentReport)}
              className="btn-ghost"
              style={{ height: '26px', padding: '0 10px', fontSize: '10px' }}
            >
              Return to Latest
            </button>
          </div>
        )}

        {/* Differential Evolution Area */}
        {isShowingOlderVersion && mostRecentReport && activeReport && (
          <div
            className={`px-6 transition-all duration-200 flex flex-col ${isEvolutionCollapsed ? 'py-2 gap-0' : 'py-3.5 gap-3'}`}
            style={{
              backgroundColor: 'var(--surface-muted)',
              borderBottom: '1px solid var(--border-subtle)',
            }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center text-xs font-semibold gap-2 uppercase tracking-widest" style={{ color: 'var(--text-secondary)' }}>
                <TrendingUp className="w-3.5 h-3.5" />
                Evolution: v{activeReport.version_number} → v{mostRecentReport.version_number}
              </div>
              <button
                onClick={() => setIsEvolutionCollapsed(!isEvolutionCollapsed)}
                className="btn-ghost text-[10px] font-medium"
                style={{ height: '20px', padding: '0 8px' }}
              >
                {isEvolutionCollapsed ? 'Show Details' : 'Hide Details'}
              </button>
            </div>
            {!isEvolutionCollapsed && (
              <DifferentialEvolution
                previousReport={activeReport}
                currentReport={mostRecentReport}
              />
            )}
          </div>
        )}
      </div>

      {/* Main Content Area with Sidebar Layout */}
      <div className="flex flex-1 overflow-hidden">
        <div
          ref={scrollContainerRef}
          className="flex-1 overflow-y-auto p-6 lg:p-8"
        >
          {generationError && (
            <div className="mb-6">
              <ErrorBanner
                message={generationError}
                onDismiss={() => useReportStore.getState().setGenerationError(null)}
              />
            </div>
          )}

          {isGenerating ? (
            <div className="space-y-8 animate-fade-in opacity-60">
              <div className="space-y-2">
                <LoadingSkeleton width="40%" height="24px" />
                <LoadingSkeleton width="100%" height="12px" />
                <LoadingSkeleton width="95%" height="12px" />
                <LoadingSkeleton width="80%" height="12px" />
              </div>
              <div className="space-y-2">
                <LoadingSkeleton width="28%" height="16px" />
                <LoadingSkeleton width="100%" height="80px" className="rounded-sm" />
                <LoadingSkeleton width="100%" height="80px" className="rounded-sm" />
              </div>
            </div>
          ) : !hasReports ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-20 px-4">
              <div
                className="w-14 h-14 rounded-sm flex items-center justify-center mb-5"
                style={{
                  backgroundColor: 'var(--surface-secondary)',
                  border: '1px solid var(--border-default)',
                }}
              >
                <FileText className="w-6 h-6" style={{ color: 'var(--text-muted)' }} />
              </div>
              <h3 className="text-base font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>No Reports Generated</h3>
              <p className="text-[13px] leading-relaxed max-w-sm" style={{ color: 'var(--text-muted)' }}>
                Review the clinical data and click "Generate Report" when you are ready to analyse the case and produce a differential diagnosis.
              </p>
            </div>
          ) : activeReport ? (
            <ReportRenderer report={activeReport} />
          ) : null}
        </div>

        {/* Version History Sidebar */}
        {isSidebarOpen && hasReports && (
          <ReportVersionList
            reports={reports}
            activeReportId={activeReport?.id || null}
            onSelectReport={(report) => setActiveReport(report)}
          />
        )}
      </div>
    </div>
  );
};
