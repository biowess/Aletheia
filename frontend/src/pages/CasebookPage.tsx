import { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, AlertCircle, FolderOpen, ArchiveX } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useCaseStore } from '../stores/caseStore';
import { CaseCard } from '../components/casebook/CaseCard';
import { EmptyState } from '../components/casebook/EmptyState';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

// ─── Motion constants ──────────────────────────────────────────────────────────
const EASING: [number, number, number, number] = [0.25, 0.46, 0.45, 0.94]; // silky ease-out
const DURATION = 0.45;                                                        // unhurried

const layoutTransition = { duration: DURATION, ease: EASING };

const exitVariant = {
  opacity: 0,
  x: 24,
  transition: { duration: 0.32, ease: EASING },
};

// ─── Animated count label ──────────────────────────────────────────────────────
// Crossfades between count strings so the number never hard-cuts.
const CountLabel = ({ text }: { text: string }) => (
  <div className="relative overflow-hidden" style={{ height: '16px' }}>
    <AnimatePresence mode="wait">
      <motion.p
        key={text}
        className="text-xs absolute inset-0"
        style={{ color: 'var(--text-muted)' }}
        initial={{ opacity: 0, y: 5 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -5 }}
        transition={{ duration: 0.28, ease: EASING }}
      >
        {text}
      </motion.p>
    </AnimatePresence>
  </div>
);

// ─── CasebookPage ─────────────────────────────────────────────────────────────
export const CasebookPage = () => {
  const { cases, isLoading, error, fetchCases } = useCaseStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [showArchived, setShowArchived] = useState(false);

  useEffect(() => {
    fetchCases(showArchived);
  }, [fetchCases, showArchived]);

  const filteredCases = useMemo(() => {
    if (!searchQuery.trim()) return cases;
    const q = searchQuery.toLowerCase();
    return cases.filter((c) => c.title.toLowerCase().includes(q));
  }, [cases, searchQuery]);

  const countText = isLoading
    ? 'Loading…'
    : `${filteredCases.length} case${filteredCases.length !== 1 ? 's' : ''}`;

  const handleRefresh = () => fetchCases(showArchived);

  return (
    <div
      className="flex flex-col h-full animate-fade-in"
      style={{ backgroundColor: 'var(--bg-primary)' }}
    >
      {/* ── Page Header ──────────────────────────────────────── */}
      <div
        className="px-8 py-5 flex items-center justify-between"
        style={{
          backgroundColor: 'var(--surface-primary)',
          borderBottom: '1px solid var(--border-subtle)',
          boxShadow: 'var(--cf-shadow-card)',
        }}
      >
        <div className="flex items-center gap-3">
          <FolderOpen
            className="w-5 h-5 flex-shrink-0"
            style={{ color: 'var(--text-muted)' }}
          />
          <div>
            <h1
              className="text-base font-semibold leading-tight tracking-tight"
              style={{ color: 'var(--text-primary)', letterSpacing: '-0.01em' }}
            >
              Casebook
            </h1>
            {/* Gracefully crossfades whenever the count string changes */}
            <CountLabel text={countText} />
          </div>
        </div>

        <Link to="/cases/new" className="btn-primary" id="btn-new-case">
          <Plus className="h-3.5 w-3.5" />
          New Case
        </Link>
      </div>

      {/* ── Toolbar ──────────────────────────────────────────── */}
      <div
        className="px-8 py-3 flex items-center gap-4"
        style={{
          backgroundColor: 'var(--surface-secondary)',
          borderBottom: '1px solid var(--border-subtle)',
        }}
      >
        <div className="relative flex-1 max-w-sm">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 pointer-events-none"
            style={{ color: 'var(--text-muted)' }}
          />
          <input
            id="search-cases"
            type="text"
            className="input-field pl-9"
            placeholder="Search cases…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-2 select-none">
          <label className="flex items-center cursor-pointer relative" htmlFor="toggle-archived">
            <input
              type="checkbox"
              id="toggle-archived"
              checked={showArchived}
              onChange={(e) => setShowArchived(e.target.checked)}
              className="sr-only peer"
            />
            <div
              className="relative w-8 h-4 rounded-sm transition-all"
              style={{
                backgroundColor: showArchived ? 'var(--state-info)' : 'var(--border-default)',
                transitionDuration: 'var(--motion-fast)',
              }}
            >
              <div
                className="absolute top-0.5 h-3 w-3 bg-white rounded-sm transition-all"
                style={{
                  left: showArchived ? 'calc(100% - 14px)' : '2px',
                  transitionDuration: 'var(--motion-fast)',
                }}
              />
            </div>
          </label>
          <span
            className="text-xs font-medium flex items-center gap-1.5"
            style={{ color: 'var(--text-secondary)' }}
          >
            <ArchiveX className="w-3.5 h-3.5" />
            Show archived
          </span>
        </div>
      </div>

      {/* ── Error Banner ─────────────────────────────────────── */}
      {error && (
        <div
          className="mx-8 mt-4 p-3 flex items-start gap-2 text-xs"
          style={{
            backgroundColor: 'var(--cf-error-container)',
            borderRadius: 'var(--radius-2)',
            border: '1px solid var(--state-declined)',
            color: 'var(--cf-on-error-container)',
          }}
        >
          <AlertCircle className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* ── Cases Grid ───────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        {isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <div
                key={n}
                className="h-36"
                style={{
                  borderRadius: 'var(--radius-2)',
                  border: '1px solid var(--border-subtle)',
                  backgroundColor: 'var(--surface-secondary)',
                  padding: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '10px',
                }}
              >
                <LoadingSkeleton width="60%" height="16px" />
                <LoadingSkeleton width="35%" height="12px" />
                <div style={{ marginTop: 'auto', display: 'flex', gap: '6px' }}>
                  <LoadingSkeleton width="52px" height="18px" />
                  <LoadingSkeleton width="68px" height="18px" />
                </div>
              </div>
            ))}
          </div>
        ) : filteredCases.length > 0 ? (
          <AnimatePresence mode="wait">
            <motion.div
              key={showArchived ? 'archived' : 'active'}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3, ease: EASING }}
              className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
            >
              {filteredCases.map((caseItem) => (
                <CaseCard key={caseItem.id} caseItem={caseItem} onRefresh={handleRefresh} />
              ))}
            </motion.div>
          </AnimatePresence>
        ) : (
          <EmptyState />
        )}
      </div>
    </div>
  );
};