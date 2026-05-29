import React from 'react';
import { Urgency, StepCategory, MissingCategory } from '../../types';

export const UrgencyBadge: React.FC<{ urgency: Urgency }> = ({ urgency }) => {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-xs font-semibold uppercase tracking-wider rounded border ${`urgency-badge-${urgency}`}`}>
      {urgency}
    </span>
  );
};

export const CategoryBadge: React.FC<{ category: StepCategory | MissingCategory }> = ({ category }) => {
  const displayLabel = category.replace('_', ' ');
  return (
    <span className="category-badge">
      {displayLabel}
    </span>
  );
};
