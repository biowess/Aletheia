import React from 'react';
import { ArrowUp, ArrowDown, ArrowRight, Plus } from 'lucide-react';

interface EvolutionIndicatorProps {
  direction: 'up' | 'down' | 'same' | 'new';
  delta: number | null;
}

export const EvolutionIndicator: React.FC<EvolutionIndicatorProps> = ({ direction, delta }) => {
  const getIcon = () => {
    switch (direction) {
      case 'up':   return <ArrowUp className="w-4 h-4 text-clinical-inverse-primary" strokeWidth={2.5} />;
      case 'down': return <ArrowDown className="w-4 h-4 text-clinical-error" strokeWidth={2.5} />;
      case 'same': return <ArrowRight className="w-4 h-4 text-clinical-on-surface-variant" strokeWidth={2} />;
      case 'new':  return <Plus className="w-4 h-4 text-clinical-on-primary-container" strokeWidth={2.5} />;
    }
  };

  const getLabel = () => {
    if (direction === 'new') {
      return (
        <span className="text-label-sm font-bold text-clinical-on-primary-container ml-1 tracking-widest">
          NEW
        </span>
      );
    }
    if (delta !== null && direction !== 'same') {
      const sign = delta > 0 ? '+' : '';
      return (
        <span
          className="text-label-sm font-bold ml-1"
          style={{ color: delta > 0 ? 'var(--cf-inverse-primary)' : 'var(--cf-error)' }}
        >
          {sign}{delta.toFixed(2)}
        </span>
      );
    }
    return null;
  };

  return (
    <div className="flex items-center justify-center bg-clinical-surface-container-low px-2.5 py-1 rounded-md border border-clinical-outline-variant min-w-[60px]">
      {getIcon()}
      {getLabel()}
    </div>
  );
};
