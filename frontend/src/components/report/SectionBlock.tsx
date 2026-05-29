import React, { ReactNode } from 'react';

interface SectionBlockProps {
  title: string;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
}

export const SectionBlock: React.FC<SectionBlockProps> = ({ title, icon, children, className = '' }) => {
  return (
    <div className={`mb-8 ${className}`}>
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-clinical-outline-variant">
        {icon && (
          <span className="text-clinical-on-surface-variant flex-shrink-0">
            {icon}
          </span>
        )}
        <h3 className="text-headline-md font-semibold text-clinical-on-surface tracking-tight">
          {title}
        </h3>
      </div>
      <div className="text-clinical-on-surface space-y-2">
        {children}
      </div>
    </div>
  );
};
