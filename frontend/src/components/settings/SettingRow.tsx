import React from 'react';

interface SettingRowProps {
  label: string;
  description?: React.ReactNode;
  children: React.ReactNode;
}

export const SettingRow: React.FC<SettingRowProps> = ({ label, description, children }) => {
  return (
    <div 
      className="flex items-center justify-between py-5 px-6 border-b last:border-0"
      style={{ borderColor: 'var(--border-subtle)' }}
    >
      <div className="flex flex-col flex-grow pr-6">
        <span className="text-body-md font-semibold" style={{ color: 'var(--text-primary)' }}>{label}</span>
        {description && (
          <span className="text-label-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
            {description}
          </span>
        )}
      </div>
      <div className="flex-shrink-0">
        {children}
      </div>
    </div>
  );
};
