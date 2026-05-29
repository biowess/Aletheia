import React, { useState } from 'react';
import { MissingInformation, Citation } from '../../types';
import { CategoryBadge } from './Badges';
import { RichText } from './RichText';
import { ChevronDown, ChevronRight, HelpCircle, Activity, Info } from 'lucide-react';

interface MissingInfoCardProps {
  item: MissingInformation;
  citations: Citation[];
}

export const MissingInfoCard: React.FC<MissingInfoCardProps> = ({ item, citations }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="missing-info-card">
      <div className="flex items-start gap-3">
        <span className="flex-shrink-0 w-8 h-8 rounded-full bg-clinical-surface-variant text-clinical-on-surface flex items-center justify-center">
          <HelpCircle className="w-4 h-4" />
        </span>
        <div className="flex-1">
          <div 
            className="flex flex-wrap items-center justify-between gap-2 mb-2 cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            <h4 className="font-semibold text-clinical-on-surface text-body-md flex items-center gap-2">
              {item.item}
              <button className="text-clinical-outline focus:outline-none hover:text-clinical-on-surface-variant transition-colors">
                {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </button>
            </h4>
            <CategoryBadge category={item.category} />
          </div>

          <div className="text-sm text-clinical-on-surface-variant mb-2">
            <span className="font-semibold text-clinical-on-surface block mb-1 flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-clinical-inverse-primary" /> Why it matters
            </span>
            <RichText text={item.why_it_matters} citations={citations} />
          </div>

          {isExpanded && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-clinical-surface-container animate-fade-up">
              <div>
                <h5 className="text-xs font-semibold text-clinical-on-surface uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-amber-600" /> Impact on Assessment
                </h5>
                <div className="text-sm text-clinical-on-surface-variant">
                  <RichText text={item.impact_on_assessment} citations={citations} />
                </div>
              </div>
              
              <div>
                <h5 className="text-xs font-semibold text-clinical-on-surface uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <HelpCircle className="w-3.5 h-3.5 text-emerald-600" /> Implications
                </h5>
                <div className="text-sm text-clinical-on-surface-variant">
                  <RichText text={item.possible_implications} citations={citations} />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
