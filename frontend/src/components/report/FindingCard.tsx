import React from 'react';
import { SupportingFinding, ContradictoryFinding, Citation } from '../../types';
import { StrengthIndicator } from './StrengthIndicator';
import { RichText } from './RichText';
import { AlertTriangle } from 'lucide-react';

interface FindingCardProps {
  finding: SupportingFinding | ContradictoryFinding;
  type: 'supporting' | 'contradictory';
  citations: Citation[];
}

export const FindingCard: React.FC<FindingCardProps> = ({ finding, type, citations }) => {
  const isSupporting = type === 'supporting';
  const supportingFinding = isSupporting ? finding as SupportingFinding : null;
  const contradictoryFinding = !isSupporting ? finding as ContradictoryFinding : null;

  return (
    <div className={`finding-card finding-card--${type}`}>
      <div className="flex items-start justify-between gap-4 mb-2">
        <h4 className="font-semibold text-clinical-on-surface text-body-md flex items-center gap-2">
          {!isSupporting && <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0" />}
          {finding.finding}
        </h4>
        {isSupporting && supportingFinding && (
          <div className="flex-shrink-0 mt-1">
            <StrengthIndicator strength={supportingFinding.strength} />
          </div>
        )}
      </div>
      
      <div className="text-sm text-clinical-on-surface-variant">
        <RichText text={finding.explanation} citations={citations} />
      </div>

      {!isSupporting && contradictoryFinding && contradictoryFinding.significance && (
        <div className="mt-3 pt-3 border-t border-[#fce3c0] text-sm font-medium text-amber-800">
          Significance: {contradictoryFinding.significance}
        </div>
      )}
    </div>
  );
};
