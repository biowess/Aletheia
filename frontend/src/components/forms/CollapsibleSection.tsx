import React, { useState } from 'react';
import { ChevronRight } from 'lucide-react';

interface CollapsibleSectionProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

export function CollapsibleSection({ title, children, defaultOpen = true }: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border border-clinical-outline-variant rounded-lg overflow-hidden bg-clinical-surface-bright shadow-card">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 bg-clinical-surface-container-low hover:bg-clinical-surface-container transition-colors duration-fast ease-clinical text-left focus:outline-none focus-visible:shadow-focus"
      >
        <span className="text-label-sm font-semibold text-clinical-on-surface tracking-widest uppercase">
          {title}
        </span>
        <ChevronRight
          className={`w-4 h-4 text-clinical-on-surface-variant transition-transform duration-fast ease-clinical ${isOpen ? 'rotate-90' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="p-4 border-t border-clinical-outline-variant space-y-4 bg-clinical-surface-bright animate-fade-up">
          {children}
        </div>
      )}
    </div>
  );
}
