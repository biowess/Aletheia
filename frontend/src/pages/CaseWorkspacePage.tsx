import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useCaseStore } from '../stores/caseStore';
import { useReportStore } from '../stores/reportStore';
import { WorkspaceSplitPane } from '../components/layout/WorkspaceSplitPane';
import { ClinicalInputPanel } from '../components/layout/ClinicalInputPanel';
import { ReasoningOutputPanel } from '../components/layout/ReasoningOutputPanel';
import { TimelinePanel } from '../components/timeline/TimelinePanel';
import { Loader2, AlertCircle, FileText, Download, ChevronLeft, Presentation } from 'lucide-react';
import { ReasoningRequest, AnamnesisData, PhysicalExamData, LaboratoryData, MorphologicalData } from '../types';
import { useSettingsStore } from '../stores/settingsStore';
import { downloadReportPDF, downloadReportPPTX } from '../api/export';
import { useToast } from '../hooks/useToast';

export const CaseWorkspacePage: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const { activeCase, fetchCase, isLoading: isCaseLoading, error: caseError } = useCaseStore();
  const { fetchReports, generateReport, isGenerating, activeReport } = useReportStore();

  const [showTimeline, setShowTimeline] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const { showToast } = useToast();
  const rightPanelRef = useRef<HTMLDivElement>(null);

  const [anamnesis, setAnamnesis] = useState<AnamnesisData>({});
  const [physicalExam, setPhysicalExam] = useState<PhysicalExamData>({});
  const [labData, setLabData] = useState<LaboratoryData>({});
  const [morphData, setMorphData] = useState<MorphologicalData>({});
  const [notes, setNotes] = useState('');

  const settings = useSettingsStore((state) => state.settings);
  const use_grounding = useMemo(() => {
    const setting = settings.find(s => s.key === 'grounding_enabled');
    if (!setting) return true;
    const val = String(setting.value).toLowerCase().trim();
    return ['true', '1', 'yes'].includes(val);
  }, [settings]);

  useEffect(() => {
    if (activeCase) {
      setAnamnesis(activeCase.anamnesis || {});
      setPhysicalExam(activeCase.physical_exam || {});
      setLabData(activeCase.laboratory_data || {});
      setMorphData(activeCase.morphological_data || {});
      setNotes(activeCase.notes || '');
    }
  }, [activeCase]);

  useEffect(() => {
    if (caseId) {
      fetchCase(caseId);
      fetchReports(caseId);
    }
  }, [caseId, fetchCase, fetchReports]);

  const handleExportPDF = async () => {
    if (!activeReport) return;
    setIsExporting(true);
    try {
      await downloadReportPDF(activeReport.id);
    } catch (err) {
      showToast('Failed to generate PDF. Please try again.', 'error');
    } finally {
      setIsExporting(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!activeCase) return;

    const request: ReasoningRequest = {
      case_id: activeCase.id,
      anamnesis,
      physical_exam: physicalExam,
      laboratory_data: labData,
      morphological_data: morphData,
      use_grounding,
    };

    await generateReport(request, (_report) => {
      showToast('Report generated successfully', 'success');
      rightPanelRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
    });
  };

  if (caseError) {
    return (
      <div className="h-full flex items-center justify-center p-6 bg-[var(--bg-primary)]">
        <div
          className="p-8 max-w-sm w-full text-center animate-fade-in"
          style={{
            backgroundColor: 'var(--surface-primary)',
            border: '1px solid var(--state-declined)',
            borderRadius: 'var(--radius-2)',
            boxShadow: 'var(--cf-shadow-card)',
          }}
        >
          <AlertCircle className="w-10 h-10 mx-auto mb-4" style={{ color: 'var(--state-declined)' }} />
          <h2 className="text-sm font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Error Loading Case</h2>
          <p className="text-[13px] mb-6" style={{ color: 'var(--text-muted)' }}>{caseError}</p>
          <Link
            to="/"
            className="text-[11px] font-semibold tracking-widest uppercase outline-none hover:underline"
            style={{ color: 'var(--aletheia-navy)' }}
          >
            Return to Casebook
          </Link>
        </div>
      </div>
    );
  }

  if (isCaseLoading || !activeCase) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-3 bg-[var(--bg-primary)]">
        <Loader2 className="w-6 h-6 animate-spin" style={{ color: 'var(--state-info)' }} />
        <p className="text-[13px] font-medium tracking-wide uppercase" style={{ color: 'var(--text-muted)' }}>Loading Workspace</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen max-h-screen overflow-hidden bg-[var(--bg-primary)] relative">
      {/* Workspace Header */}
      <header
        className="px-6 py-3 flex items-center justify-between shrink-0"
        style={{
          backgroundColor: 'var(--surface-primary)',
          borderBottom: '1px solid var(--border-strong)',
          boxShadow: 'var(--cf-shadow-card)',
          zIndex: 30,
        }}
      >
        <div className="flex items-center gap-3 min-w-0">
          <Link
            to="/"
            className="flex items-center justify-center w-7 h-7 rounded-sm outline-none transition-colors"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.backgroundColor = 'var(--surface-secondary)';
              (e.currentTarget as HTMLElement).style.color = 'var(--text-primary)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.backgroundColor = 'transparent';
              (e.currentTarget as HTMLElement).style.color = 'var(--text-muted)';
            }}
            title="Back to Casebook"
          >
            <ChevronLeft className="w-4 h-4" />
          </Link>
          <div className="h-5 w-px mr-1" style={{ backgroundColor: 'var(--border-subtle)' }} />
          <h1
            className="text-base font-semibold truncate max-w-lg tracking-tight leading-tight"
            style={{ color: 'var(--aletheia-navy)' }}
          >
            {activeCase.title}
          </h1>
          {activeCase.tags.length > 0 && (
            <div className="flex items-center gap-1.5 flex-shrink-0 ml-2">
              {activeCase.tags.slice(0, 3).map((tag) => (
                <span key={tag} className="badge-secondary text-[10px]">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2.5 flex-shrink-0">
          <button
            onClick={() => setShowTimeline(!showTimeline)}
            className="btn-ghost"
            style={{
              height: '32px',
              padding: '0 12px',
              backgroundColor: showTimeline ? 'var(--surface-muted)' : 'transparent',
              borderColor: showTimeline ? 'var(--border-strong)' : 'var(--border-default)'
            }}
          >
            {showTimeline ? 'Hide Timeline' : 'View Timeline'}
          </button>

          <button
            onClick={handleExportPDF}
            disabled={!activeReport || isExporting}
            className="btn-ghost"
            style={{ height: '32px', padding: '0 12px' }}
          >
            {isExporting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
            {isExporting ? 'Exporting…' : 'Export PDF'}
          </button>

          <button
            onClick={() => {
              if (activeReport) {
                downloadReportPPTX(activeReport.id, activeReport.version_number).catch(() =>
                  showToast('Failed to download PowerPoint', 'error')
                );
              }
            }}
            disabled={!activeReport}
            className="btn-ghost"
            style={{ height: '32px', padding: '0 12px' }}
          >
            <Presentation className="w-3.5 h-3.5" />
            Export PPTX
          </button>

          <button
            onClick={handleGenerateReport}
            disabled={isGenerating}
            className="btn-primary"
            style={{ height: '32px', padding: '0 16px' }}
          >
            {isGenerating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FileText className="w-3.5 h-3.5" />}
            {isGenerating ? 'Generating…' : 'Generate Report'}
          </button>
        </div>
      </header>

      {/* Main Split Layout */}
      <div className="flex-1 overflow-hidden animate-fade-in">
        <WorkspaceSplitPane
          left={
            <ClinicalInputPanel
              anamnesis={anamnesis} setAnamnesis={setAnamnesis}
              physicalExam={physicalExam} setPhysicalExam={setPhysicalExam}
              labData={labData} setLabData={setLabData}
              morphData={morphData} setMorphData={setMorphData}
              notes={notes} setNotes={setNotes}
            />
          }
          right={
            <div ref={rightPanelRef} className="h-full overflow-auto">
              <ReasoningOutputPanel />
            </div>
          }
          showBottom={showTimeline}
          bottomPanel={
            <div className="h-full">
              <TimelinePanel caseId={activeCase.id} />
            </div>
          }
        />
      </div>
    </div>
  );
};
