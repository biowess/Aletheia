import { Link } from 'react-router-dom';
import { Archive, ArchiveRestore, Calendar, ChevronRight } from 'lucide-react';
import { CaseListItem } from '../../types';
import { archiveCase, unarchiveCase } from '../../api/cases';
import { useCaseStore } from '../../stores/caseStore';

interface CaseCardProps {
  caseItem: CaseListItem;
  onRefresh: () => void;
}

export const CaseCard = ({ caseItem, onRefresh }: CaseCardProps) => {
  const { setError } = useCaseStore();

  const handleArchive = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await archiveCase(caseItem.id);
      onRefresh();
    } catch (err: any) {
      setError(err.message || 'Failed to archive case');
    }
  };

  const handleUnarchive = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await unarchiveCase(caseItem.id);
      onRefresh();
    } catch (err: any) {
      setError(err.message || 'Failed to unarchive case');
    }
  };

  const formattedDate = new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: '2-digit',
    year: 'numeric',
  }).format(new Date(caseItem.created_at));

  return (
    <Link
      to={`/cases/${caseItem.id}`}
      className="group relative flex flex-col gap-3 outline-none focus-visible:shadow-focus transition-all animate-fade-in"
      style={{
        borderRadius: 'var(--radius-2)',
        border: '1px solid var(--border-subtle)',
        backgroundColor: caseItem.is_archived ? 'var(--surface-secondary)' : 'var(--surface-primary)',
        padding: '16px',
        opacity: caseItem.is_archived ? 0.7 : 1,
        boxShadow: caseItem.is_archived ? 'none' : 'var(--cf-shadow-card)',
        transitionDuration: 'var(--motion-normal)',
        transitionTimingFunction: 'var(--ease-standard)',
      }}
      onMouseEnter={(e) => {
        if (!caseItem.is_archived) {
          (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-default)';
          (e.currentTarget as HTMLElement).style.boxShadow = 'var(--cf-shadow-elevated)';
        }
      }}
      onMouseLeave={(e) => {
        if (!caseItem.is_archived) {
          (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-subtle)';
          (e.currentTarget as HTMLElement).style.boxShadow = 'var(--cf-shadow-card)';
        }
      }}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 min-w-0">
            <h3
              className="text-sm font-semibold truncate"
              style={{
                color: 'var(--text-primary)',
                letterSpacing: '-0.01em',
                transitionDuration: 'var(--motion-fast)',
              }}
            >
              {caseItem.title}
            </h3>
            {caseItem.is_archived && (
              <span className="badge-secondary flex-shrink-0">Archived</span>
            )}
          </div>
          <div
            className="flex items-center gap-1.5 mt-1.5 text-[11px]"
            style={{ color: 'var(--text-muted)' }}
          >
            <Calendar className="h-3 w-3 flex-shrink-0" />
            <time dateTime={caseItem.created_at}>{formattedDate}</time>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0 mt-0.5">
          {!caseItem.is_archived ? (
            <button
              onClick={handleArchive}
              id={`btn-archive-${caseItem.id}`}
              className="flex items-center justify-center w-7 h-7 opacity-0 group-hover:opacity-100 focus-visible:opacity-100 transition-all outline-none"
              style={{
                borderRadius: 'var(--radius-1)',
                color: 'var(--text-muted)',
                transitionDuration: 'var(--motion-fast)',
                border: '1px solid transparent',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.backgroundColor = 'var(--cf-error-container)';
                (e.currentTarget as HTMLElement).style.color = 'var(--state-declined)';
                (e.currentTarget as HTMLElement).style.borderColor = 'var(--state-declined)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.backgroundColor = 'transparent';
                (e.currentTarget as HTMLElement).style.color = 'var(--text-muted)';
                (e.currentTarget as HTMLElement).style.borderColor = 'transparent';
              }}
              title="Archive Case"
            >
              <Archive className="h-3.5 w-3.5" />
              <span className="sr-only">Archive</span>
            </button>
          ) : (
            <button
              onClick={handleUnarchive}
              id={`btn-unarchive-${caseItem.id}`}
              className="flex items-center justify-center w-7 h-7 opacity-0 group-hover:opacity-100 focus-visible:opacity-100 transition-all outline-none"
              style={{
                borderRadius: 'var(--radius-1)',
                color: 'var(--text-muted)',
                transitionDuration: 'var(--motion-fast)',
                border: '1px solid transparent',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.backgroundColor = 'var(--surface-primary)';
                (e.currentTarget as HTMLElement).style.color = 'var(--text-primary)';
                (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-default)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.backgroundColor = 'transparent';
                (e.currentTarget as HTMLElement).style.color = 'var(--text-muted)';
                (e.currentTarget as HTMLElement).style.borderColor = 'transparent';
              }}
              title="Unarchive Case"
            >
              <ArchiveRestore className="h-3.5 w-3.5" />
              <span className="sr-only">Unarchive</span>
            </button>
          )}
          <ChevronRight
            className="h-3.5 w-3.5 opacity-0 group-hover:opacity-100 transition-opacity -mr-0.5"
            style={{ color: 'var(--text-muted)', transitionDuration: 'var(--motion-fast)' }}
          />
        </div>
      </div>

      {/* Tags */}
      {caseItem.tags && caseItem.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-1">
          {caseItem.tags.map((tag) => (
            <span key={tag} className="badge-secondary text-[10px]">
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Bottom accent rule — appears on hover */}
      <div
        className="absolute bottom-0 left-0 right-0 h-px origin-left scale-x-0 group-hover:scale-x-100 transition-transform"
        style={{
          backgroundColor: 'var(--state-info)',
          borderBottomLeftRadius: 'var(--radius-2)',
          borderBottomRightRadius: 'var(--radius-2)',
          transitionDuration: 'var(--motion-soft)',
          transitionTimingFunction: 'var(--ease-standard)',
        }}
      />
    </Link>
  );
};
