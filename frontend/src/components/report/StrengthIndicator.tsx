import React from 'react';
import { FindingStrength } from '../../types';

export const StrengthIndicator: React.FC<{ strength: FindingStrength }> = ({ strength }) => {
  const bars = [
    { active: true, color: 'bg-emerald-400' }, // Always at least weak
    { active: strength === 'moderate' || strength === 'strong', color: 'bg-emerald-500' },
    { active: strength === 'strong', color: 'bg-emerald-600' },
  ];

  return (
    <div className="flex items-end gap-0.5 h-3" title={`Evidence strength: ${strength}`}>
      {bars.map((bar, i) => (
        <div
          key={i}
          className={`w-1 rounded-sm transition-all duration-300 ${
            bar.active ? bar.color : 'bg-clinical-surface-variant'
          }`}
          style={{ height: `${(i + 1) * 33.3}%` }}
        />
      ))}
      <span className="ml-1.5 text-[10px] uppercase font-bold text-clinical-on-surface-variant tracking-wider leading-none">
        {strength}
      </span>
    </div>
  );
};
