import React, { useState } from 'react';
import { Citation } from '../../types';
import { ExternalLink, BookOpen, Fingerprint } from 'lucide-react';
import * as HoverCard from '@radix-ui/react-hover-card';
import * as Dialog from '@radix-ui/react-dialog';
import { useToast } from '../../hooks/useToast';

interface CitationChipProps {
  citationId: string;
  citations: Citation[];
}

/**
 * Sanitize a URL from an API response before using it as an href.
 * Only allows http: and https: schemes. Anything else (javascript:,
 * data:, vbscript:, etc.) is replaced with '#' so no code executes.
 */
function sanitizeHref(url: string | undefined | null): string {
  if (!url) return '#';
  try {
    const parsed = new URL(url);
    if (parsed.protocol === 'https:' || parsed.protocol === 'http:') {
      return url;
    }
  } catch {
    // Relative URLs or unparseable strings — block them
  }
  return '#';
}

const generateCitationText = (c: Citation) => {
  const authors = c.authors && c.authors.length > 0 ? c.authors.join(', ') : '';
  const title = c.title || '';
  const journal = c.journal || '';
  const year = c.year || '';
  let text = `${authors}. ${title}. ${journal} ${year};`;
  if (c.pmid) text += ` PMID: ${c.pmid}.`;
  else if (c.doi) text += ` DOI: ${c.doi}.`;
  return text;
};

export const CitationChip: React.FC<CitationChipProps> = ({ citationId, citations }) => {
  const { showToast } = useToast();
  const citationIndex = citations.findIndex(c => c.id === citationId);
  const citation = citationIndex !== -1 ? citations[citationIndex] : undefined;

  const [citationText, setCitationText] = useState(() => citation ? generateCitationText(citation) : '');

  if (!citation) {
    return <span className="citation-chip opacity-50 cursor-help" title={`Missing citation: ${citationId}`}>[{citationId}]</span>;
  }

  const getSourceIcon = () => {
    switch (citation.sourceType) {
      case 'pubmed': return <BookOpen className="w-3 h-3 mr-1" />;
      case 'doi': return <Fingerprint className="w-3 h-3 mr-1" />;
      default: return null;
    }
  };

  const getLabel = () => {
    return `[${citationIndex + 1}]`;
  };

  const targetUrl = sanitizeHref(citation.canonicalUrl) !== '#'
    ? sanitizeHref(citation.canonicalUrl)
    : citation.pmid
      ? `https://pubmed.ncbi.nlm.nih.gov/${citation.pmid}/`
      : '#';

  return (
    <HoverCard.Root openDelay={200} closeDelay={200}>
      <HoverCard.Trigger asChild>
        <a
          href={targetUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="citation-chip align-super text-[0.6em] leading-none text-clinical-primary font-semibold ml-0.5 px-1 py-[3px] border border-clinical-outline rounded-[3px] hover:bg-clinical-primary/10 transition-colors inline-block text-center min-w-[1.4em] shadow-sm bg-clinical-surface-bright hover:shadow-md relative top-[1px]" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}
          aria-label={`Citation: ${citation.title}`}
        >
          {getLabel()}
        </a>
      </HoverCard.Trigger>

      <HoverCard.Portal>
        <HoverCard.Content
          className="w-[22rem] z-50 animate-fade-up shadow-2xl bg-clinical-surface-bright border border-clinical-outline rounded-xl p-5 text-left"
          sideOffset={8}
          collisionPadding={20}
        >
          <div className="flex flex-col gap-4">
            <div>
              <h4 className="text-base font-semibold text-clinical-on-surface leading-tight mb-2">
                {citation.title}
              </h4>
              <div className="text-sm text-clinical-on-surface-variant space-y-1">
                {citation.authors && citation.authors.length > 0 && (
                  <div className="line-clamp-2 font-medium">{citation.authors.join(', ')}</div>
                )}
                <div className="flex items-center gap-1.5 font-medium">
                  {citation.journal && <span>{citation.journal}</span>}
                  {citation.journal && citation.year && <span className="w-1.5 h-1.5 rounded-full bg-clinical-outline" />}
                  {citation.year && <span>{citation.year}</span>}
                </div>
              </div>
            </div>

            {citation.abstractSnippet && (
              <div className="text-sm text-clinical-on-surface line-clamp-3 italic opacity-90 border-l-2 border-clinical-primary/30 pl-3">
                "{citation.abstractSnippet}..."
              </div>
            )}

            <div className="flex flex-col gap-3 mt-1 pt-3 border-t border-clinical-outline">
              <div className="flex items-center justify-between text-xs text-clinical-on-surface-variant font-medium">
                <span className="flex items-center gap-1 px-2 py-1 rounded-md bg-clinical-surface-container">
                  {citation.sourceDomain}
                </span>
                <div className="flex items-center gap-2">
                  {citation.pmid && <span>PMID: {citation.pmid}</span>}
                  {!citation.pmid && citation.doi && <span>DOI: {citation.doi}</span>}
                  {citation.evidenceLevel && (
                    <span className="capitalize px-2 py-1 rounded-md bg-clinical-primary/10 text-clinical-primary border border-clinical-primary/20">
                      {citation.evidenceLevel.replace('_', ' ')}
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 mt-2">
                <Dialog.Root>
                  <Dialog.Trigger asChild>
                    <button
                      onClick={(e) => e.stopPropagation()}
                      className="flex-1 inline-flex items-center justify-center py-2 px-4 bg-clinical-primary text-clinical-on-primary rounded-lg text-xs font-semibold transition-colors hover:bg-clinical-primary/90 shadow-sm"
                    >
                      Cite
                    </button>
                  </Dialog.Trigger>
                  <Dialog.Portal>
                    <Dialog.Overlay className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[100] data-[state=open]:animate-dialog-overlay-show data-[state=closed]:animate-dialog-overlay-hide" />
                    <Dialog.Content
                      className="fixed left-[50%] top-[50%] w-full max-w-lg bg-clinical-surface-bright rounded-2xl shadow-2xl border border-clinical-outline p-6 z-[101] flex flex-col gap-4 focus:outline-none data-[state=open]:animate-dialog-content-show data-[state=closed]:animate-dialog-content-hide"
                    >
                      <Dialog.Title className="text-xl font-bold text-clinical-on-surface">
                        Citation
                      </Dialog.Title>
                      <Dialog.Description className="sr-only">
                        Copy the citation for this article.
                      </Dialog.Description>

                      <textarea
                        className="w-full h-32 p-4 text-sm font-medium rounded-xl border border-clinical-outline bg-clinical-surface-container-lowest text-clinical-on-surface focus:outline-none focus:ring-2 focus:ring-clinical-primary resize-none shadow-inner leading-relaxed"
                        value={citationText}
                        onChange={(e) => setCitationText(e.target.value)}
                      />

                      <div className="flex justify-end gap-3 mt-4">
                        <Dialog.Close asChild>
                          <button className="px-5 py-2.5 text-sm font-semibold rounded-lg border border-clinical-outline text-clinical-on-surface hover:bg-clinical-surface-container transition-colors focus:ring-2 focus:ring-clinical-primary/30">
                            Cancel
                          </button>
                        </Dialog.Close>
                        <Dialog.Close asChild>
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(citationText);
                              showToast('Citation copied to clipboard', 'success');
                            }}
                            className="px-5 py-2.5 text-sm font-semibold rounded-lg bg-clinical-primary text-clinical-on-primary hover:bg-clinical-primary/90 transition-colors shadow-md focus:ring-2 focus:ring-clinical-primary/30 focus:ring-offset-2"
                          >
                            Copy Citation
                          </button>
                        </Dialog.Close>
                      </div>
                    </Dialog.Content>
                  </Dialog.Portal>
                </Dialog.Root>

                {citation.pmid && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigator.clipboard.writeText(citation.pmid!);
                    }}
                    className="flex-1 inline-flex items-center justify-center py-2 px-4 bg-clinical-surface-container-low hover:bg-clinical-surface-container text-clinical-inverse-primary rounded-lg text-xs font-semibold transition-colors border border-clinical-outline shadow-sm"
                    title="Copy PMID"
                  >
                    Copy PMID
                  </button>
                )}
                {citation.doi && !citation.pmid && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigator.clipboard.writeText(citation.doi!);
                    }}
                    className="flex-1 inline-flex items-center justify-center py-2 px-4 bg-clinical-surface-container-low hover:bg-clinical-surface-container text-clinical-inverse-primary rounded-lg text-xs font-semibold transition-colors border border-clinical-outline shadow-sm"
                    title="Copy DOI"
                  >
                    Copy DOI
                  </button>
                )}
              </div>
            </div>
          </div>
          <HoverCard.Arrow className="fill-clinical-surface-bright" width={16} height={8} />
        </HoverCard.Content>
      </HoverCard.Portal>
    </HoverCard.Root>
  );
};
