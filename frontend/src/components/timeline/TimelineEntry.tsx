import React from 'react';
import { FollowUpEntry } from '../../types';
import { FileText, Activity, Droplet, Search, Syringe, File, ChevronRight } from 'lucide-react';

interface TimelineEntryProps {
  entry: FollowUpEntry;
  onViewReport?: (reportId: string) => void;
}

const getTypeBadgeClass = (type: string): string => {
  switch (type) {
    case 'anamnesis':    return 'badge-secondary';
    case 'physical_exam': return 'badge-tertiary';
    case 'laboratory':   return 'badge-primary';
    case 'imaging':      return 'badge-primary';
    case 'procedure':    return 'badge-tertiary';
    case 'general_note': return 'badge-low';
    default:             return 'badge-low';
  }
};

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'anamnesis':    return <FileText className="w-3 h-3" />;
    case 'physical_exam': return <Activity className="w-3 h-3" />;
    case 'laboratory':   return <Droplet className="w-3 h-3" />;
    case 'imaging':      return <Search className="w-3 h-3" />;
    case 'procedure':    return <Syringe className="w-3 h-3" />;
    default:             return <File className="w-3 h-3" />;
  }
};

const formatLabel = (type: string) =>
  type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

export function TimelineEntry({ entry, onViewReport }: TimelineEntryProps) {
  const dateStr = new Date(entry.created_at).toLocaleString();

  return (
    <div className="relative pl-7 py-3 group">
      {/* Connector line */}
      <div
        className="absolute left-[11px] top-0 bottom-0 w-px group-last:bottom-auto group-last:h-full"
        style={{ backgroundColor: 'var(--border-default)' }}
      />

      {/* Node indicator */}
      <div
        className="absolute left-[8px] top-5 w-[7px] h-[7px] rounded-full border-2"
        style={{
          backgroundColor: 'var(--aletheia-navy)',
          borderColor: 'var(--surface-primary)',
          boxShadow: '0 0 0 1px var(--border-strong)',
        }}
      />

      {/* Entry Card */}
      <div
        className="bg-white rounded-sm transition-all duration-fast ease-standard"
        style={{
          border: '1px solid var(--border-subtle)',
          padding: '12px',
          boxShadow: 'var(--shadow-soft)',
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-default)';
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-subtle)';
        }}
      >
        <div className="flex justify-between items-start mb-2.5 gap-3">
          <div className="flex flex-col gap-0.5 min-w-0">
            <h4
              className="text-[13px] font-semibold truncate leading-tight"
              style={{ color: 'var(--text-primary)', letterSpacing: '-0.01em' }}
            >
              {entry.title}
            </h4>
            <span
              className="text-[10px] tracking-wide num-tabular"
              style={{ color: 'var(--text-muted)' }}
            >
              {dateStr}
            </span>
          </div>
          <span
            className={`${getTypeBadgeClass(entry.entry_type)} flex items-center gap-1 flex-shrink-0`}
            style={{ fontSize: '9px', padding: '1px 4px' }}
          >
            {getTypeIcon(entry.entry_type)}
            {formatLabel(entry.entry_type)}
          </span>
        </div>

        {entry.free_text_note && (
          <p
            className="text-[12px] leading-relaxed mt-2 p-2 rounded-sm whitespace-pre-wrap"
            style={{
              backgroundColor: 'var(--surface-muted)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-secondary)',
            }}
          >
            {entry.free_text_note}
          </p>
        )}

        {entry.triggered_report_id && onViewReport && (
          <div
            className="mt-3 pt-2"
            style={{ borderTop: '1px dashed var(--border-subtle)' }}
          >
            <button
              onClick={() => onViewReport(entry.triggered_report_id!)}
              className="text-[10px] font-semibold flex items-center gap-0.5 tracking-widest uppercase outline-none"
              style={{
                color: 'var(--state-info)',
                transitionDuration: 'var(--motion-fast)',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.color = 'var(--aletheia-navy)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.color = 'var(--state-info)';
              }}
            >
              View Generated Report <ChevronRight className="w-3 h-3 -mt-px" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
