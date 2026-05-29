import React from 'react';
import { Citation } from '../../types';
import { BookOpen, ExternalLink, Fingerprint, Globe } from 'lucide-react';

interface ReferencesFooterProps {
  citations: Citation[];
}

export const ReferencesFooter: React.FC<ReferencesFooterProps> = ({ citations }) => {
  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'pubmed': return <BookOpen className="w-3.5 h-3.5 flex-shrink-0 mt-1" style={{ color: 'var(--text-muted)' }} />;
      case 'doi': return <Fingerprint className="w-3.5 h-3.5 flex-shrink-0 mt-1" style={{ color: 'var(--text-muted)' }} />;
      default: return <Globe className="w-3.5 h-3.5 flex-shrink-0 mt-1" style={{ color: 'var(--text-muted)' }} />;
    }
  };

  const safeCitations = citations || [];

  return (
    <div
      className="p-6"
      style={{
        backgroundColor: 'var(--surface-secondary)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-1)',
      }}
    >
      {safeCitations.length === 0 ? (
        <p className="text-sm italic" style={{ color: 'var(--text-muted)' }}>No verified citations were matched for this report.</p>
      ) : (
        <ol className="space-y-4">
          {safeCitations.map((ref, idx) => (
            <li key={ref.id || idx} className="flex items-start gap-3">
              <span
                className="font-semibold min-w-[1.5rem] mt-0.5 text-right num-tabular"
                style={{ color: 'var(--text-muted)', fontSize: '13px' }}
              >
                [{idx + 1}]
              </span>
              <div className="flex-1 text-[13px] leading-relaxed">
                <div className="mb-1 flex items-start gap-2">
                  {getSourceIcon(ref.sourceType)}
                  <span style={{ color: 'var(--text-primary)' }}>
                    {ref.vancouverString ? (
                      ref.vancouverString.replace(/^\[\d+\]\s*/, '')
                    ) : (
                      <span className="font-medium">{ref.title}</span>
                    )}
                  </span>
                </div>
                
                <div className="space-y-1 mt-1.5" style={{ color: 'var(--text-secondary)' }}>
                  {!ref.vancouverString && ref.authors && ref.authors.length > 0 && (
                    <div>{ref.authors.join(', ')}</div>
                  )}
                  <div className="flex flex-wrap items-center gap-2 text-[11px]">
                    {!ref.vancouverString && ref.journal && <span>{ref.journal}</span>}
                    {!ref.vancouverString && ref.year && <span className="font-semibold">{ref.year}</span>}
                    {ref.id && (
                      <span className="font-mono px-1.5 py-0.5 num-tabular" style={{ backgroundColor: 'var(--surface-primary)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-1)' }}>
                        ID: {ref.id}
                      </span>
                    )}
                    {ref.pmid && (
                      <span className="px-1.5 py-0.5 num-tabular" style={{ backgroundColor: 'var(--surface-primary)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-1)' }}>
                        PMID: {ref.pmid}
                      </span>
                    )}
                  </div>
                  {ref.canonicalUrl && (
                    <div className="mt-1">
                      <a
                        href={ref.canonicalUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 font-medium hover:underline"
                        style={{ color: 'var(--state-info)' }}
                      >
                        {ref.canonicalUrl} <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  )}
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}

      {/* Temporary Debug UI */}
      <div className="mt-8">
        <details className="bg-gray-900 rounded-sm p-2" style={{ borderRadius: 'var(--radius-1)' }}>
          <summary className="text-xs font-mono text-gray-400 cursor-pointer select-none">
            [DEBUG] View Raw Citations JSON
          </summary>
          <pre className="mt-2 p-4 text-green-400 text-xs overflow-auto font-mono max-h-60 rounded bg-black">
            {JSON.stringify(safeCitations, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
};
