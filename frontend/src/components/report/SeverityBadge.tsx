import React from 'react';
import { Severity } from '../../types';
import { Activity, AlertTriangle, AlertOctagon, CheckCircle } from 'lucide-react';

interface SeverityBadgeProps {
  severity: Severity;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity }) => {
  let icon = null;
  let label = '';
  let badgeClass = '';

  switch (severity) {
    case 'low':
      icon = <CheckCircle className="w-4 h-4" />;
      label = 'Low Severity';
      badgeClass = 'severity-badge-low';
      break;
    case 'moderate':
      icon = <Activity className="w-4 h-4" />;
      label = 'Moderate Severity';
      badgeClass = 'severity-badge-moderate';
      break;
    case 'high':
      icon = <AlertTriangle className="w-4 h-4" />;
      label = 'High Severity';
      badgeClass = 'severity-badge-high';
      break;
    case 'critical':
      icon = <AlertOctagon className="w-4 h-4" />;
      label = 'Critical Severity';
      badgeClass = 'severity-badge-critical';
      break;
  }

  const handleClick = () => {
    const nextSteps = document.getElementById('suggested-next-steps');
    if (nextSteps) {
      nextSteps.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div 
      onClick={handleClick}
      className={`inline-flex items-center gap-1.5 px-3 py-1 border text-sm font-semibold tracking-wide uppercase cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 ${badgeClass}`}
      style={{ 
        fontFamily: '"IBM Plex Sans", sans-serif',
        borderRadius: 'var(--radius-1)'
      }}
    >
      {icon}
      {label}
    </div>
  );
};
