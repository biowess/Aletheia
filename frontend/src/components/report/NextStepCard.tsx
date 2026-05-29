import React, { useState } from 'react';
import { NextStep, Citation } from '../../types';
import { UrgencyBadge, CategoryBadge } from './Badges';
import { RichText } from './RichText';
import { ChevronDown, ChevronRight, Target, AlertTriangle } from 'lucide-react';

interface NextStepCardProps {
  step: NextStep;
  index: number;
  citations: Citation[];
}

export const NextStepCard: React.FC<NextStepCardProps> = ({ step, index, citations }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="next-step-card">
      <div className="flex items-start gap-3">
        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-clinical-secondary-container text-clinical-on-secondary-container flex items-center justify-center font-bold text-xs mt-0.5">
          {index + 1}
        </span>
        <div className="flex-1">
          <div 
            className="flex flex-wrap items-center justify-between gap-2 mb-2 cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            <h4 className="font-semibold text-clinical-on-surface text-body-md flex items-center gap-2">
              {step.title}
              <button className="text-clinical-outline focus:outline-none hover:text-clinical-on-surface-variant transition-colors">
                {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </button>
            </h4>
            <div className="flex items-center gap-2 flex-shrink-0">
              <CategoryBadge category={step.category} />
              <UrgencyBadge urgency={step.urgency} />
            </div>
          </div>

          <div className="text-sm text-clinical-on-surface-variant mb-3">
            <RichText text={step.rationale} citations={citations} />
          </div>

          {isExpanded && (
            <div className="mt-4 space-y-3 pt-3 border-t border-clinical-surface-container animate-fade-up">
              {step.expected_outcome && (
                <div className="bg-[#f8fbff] p-3 rounded-md border border-clinical-outline-variant">
                  <h5 className="text-xs font-semibold text-clinical-on-surface-variant uppercase tracking-wider mb-1 flex items-center gap-1.5">
                    <Target className="w-3.5 h-3.5" /> Expected Outcome
                  </h5>
                  <p className="text-sm text-clinical-on-surface">
                    <RichText text={step.expected_outcome} citations={citations} />
                  </p>
                </div>
              )}
              
              {step.risks_of_delay && (
                <div className="bg-red-50 p-3 rounded-md border border-red-100">
                  <h5 className="text-xs font-semibold text-red-800 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" /> Risks of Delay
                  </h5>
                  <p className="text-sm text-red-900">
                    <RichText text={step.risks_of_delay} citations={citations} />
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
