import React, { useMemo } from 'react';
import { Citation } from '../../types';
import { CitationChip } from './CitationChip';

interface RichTextProps {
  text: string;
  citations: Citation[];
  className?: string;
}

type RichTextNode = 
  | { type: 'text'; content: string }
  | { type: 'citation'; citationId: string };

export const RichText: React.FC<RichTextProps> = ({ text, citations, className = '' }) => {
  const nodes = useMemo(() => {
    if (!text) return [];
    
    const parts = text.split(/\{\{cite:([^}]+)\}\}/g);
    const parsedNodes: RichTextNode[] = [];
    
    parts.forEach((part, index) => {
      if (index % 2 === 0) {
        if (part) {
          parsedNodes.push({ type: 'text', content: part });
        }
      } else {
        if (part) {
          parsedNodes.push({ type: 'citation', citationId: part });
        }
      }
    });
    
    return parsedNodes;
  }, [text]);

  if (!text) return null;

  return (
    <div className={`text-clinical-on-surface leading-relaxed text-body-md ${className}`}>
      {nodes.map((node, index) => {
        if (node.type === 'text') {
          const lines = node.content.split('\n');
          return (
            <React.Fragment key={index}>
              {lines.map((line, i) => (
                <React.Fragment key={i}>
                  {line}
                  {i < lines.length - 1 && <br />}
                </React.Fragment>
              ))}
            </React.Fragment>
          );
        } else {
          return <CitationChip key={index} citationId={node.citationId} citations={citations || []} />;
        }
      })}
    </div>
  );
};
