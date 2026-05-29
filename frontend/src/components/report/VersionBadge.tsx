import React from 'react';

interface VersionBadgeProps {
  version: number;
  className?: string;
}

export const VersionBadge: React.FC<VersionBadgeProps> = ({ version, className = '' }) => {
  return (
    <span
      className={`inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-label-sm font-semibold tracking-widest bg-clinical-surface-container text-clinical-on-surface-variant border border-clinical-outline-variant ${className}`}
    >
      v{version}
    </span>
  );
};
