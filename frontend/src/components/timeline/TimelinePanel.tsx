import React, { useEffect, useState } from 'react';
import { Plus, Clock } from 'lucide-react';
import { FollowUpEntry } from '../../types';
import { listFollowUps } from '../../api/followUps';
import { useReportStore } from '../../stores/reportStore';
import { TimelineEntry } from './TimelineEntry';
import { AddFollowUpModal } from './AddFollowUpModal';

interface TimelinePanelProps {
  caseId: string;
}

export function TimelinePanel({ caseId }: TimelinePanelProps) {
  const [entries, setEntries] = useState<FollowUpEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const reports = useReportStore((state) => state.reports);
  const setActiveReport = useReportStore((state) => state.setActiveReport);

  const fetchEntries = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listFollowUps(caseId);
      const sortedData = data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setEntries(sortedData);
    } catch (err: any) {
      setError(err.message || 'Failed to load timeline entries.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (caseId) fetchEntries();
  }, [caseId]);

  const handleViewReport = (reportId: string) => {
    const report = reports.find(r => r.id === reportId);
    if (report) {
      setActiveReport(report);
    } else {
      console.warn(`Report with ID ${reportId} not found in store.`);
    }
  };

  return (
    <div
      className="flex flex-col h-full bg-white overflow-hidden"
      style={{ borderLeft: '1px solid var(--border-subtle)' }}
    >
      {/* Panel Header */}
      <div
        className="px-5 py-3 flex items-center justify-between"
        style={{
          backgroundColor: 'var(--surface-primary)',
          borderBottom: '1px solid var(--border-subtle)',
        }}
      >
        <div className="flex items-center gap-2.5">
          <Clock className="w-4 h-4" style={{ color: 'var(--text-muted)' }} />
          <h2
            className="text-sm font-semibold tracking-tight leading-tight"
            style={{ color: 'var(--text-primary)' }}
          >
            Evolution Timeline
          </h2>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="btn-ghost"
          style={{ height: '28px', padding: '0 10px', fontSize: '11px' }}
        >
          <Plus className="w-3.5 h-3.5" />
          Add Event
        </button>
      </div>

      {/* Panel Body */}
      <div
        className="flex-1 overflow-y-auto p-5"
        style={{ backgroundColor: 'var(--bg-primary)' }}
      >
        {isLoading ? (
          <div className="flex justify-center items-center h-40">
            <div
              className="animate-spin rounded-full h-6 w-6 border-b-2"
              style={{ borderColor: 'var(--state-info)' }}
            />
          </div>
        ) : error ? (
          <div
            className="p-3 text-xs text-center"
            style={{
              backgroundColor: 'var(--cf-error-container)',
              color: 'var(--cf-on-error-container)',
              border: '1px solid var(--state-declined)',
              borderRadius: 'var(--radius-1)',
            }}
          >
            {error}
          </div>
        ) : entries.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-10 px-4">
            <div
              className="w-14 h-14 rounded-xl flex items-center justify-center mb-5 shadow-sm mx-auto"
              style={{
                backgroundColor: 'var(--surface-secondary)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--text-muted)' }}>
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <h3 className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>No Timeline Events</h3>
            <p className="text-xs max-w-[240px] leading-relaxed mb-5" style={{ color: 'var(--text-muted)' }}>
              Track disease progression and clinical follow-ups sequentially over time.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="btn-primary"
              style={{ height: '32px' }}
            >
              Add First Event
            </button>
          </div>
        ) : (
          <div className="pl-1">
            {entries.map((entry) => (
              <TimelineEntry
                key={entry.id}
                entry={entry}
                onViewReport={handleViewReport}
              />
            ))}
          </div>
        )}
      </div>

      <AddFollowUpModal
        caseId={caseId}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={fetchEntries}
      />
    </div>
  );
}
