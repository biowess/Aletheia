import React from 'react';

interface TabNavProps {
  tabs: string[];
  activeTab: number;
  onTabChange: (index: number) => void;
}

export const TabNav: React.FC<TabNavProps> = ({ tabs, activeTab, onTabChange }) => {
  return (
    <div
      className="flex w-full overflow-x-auto"
      style={{ borderBottom: '1px solid var(--border-subtle)' }}
      role="tablist"
    >
      {tabs.map((tab, index) => {
        const isActive = activeTab === index;
        return (
          <button
            key={tab}
            type="button"
            role="tab"
            aria-selected={isActive}
            onClick={() => onTabChange(index)}
            className="relative outline-none select-none cursor-pointer whitespace-nowrap transition-all"
            style={{
              padding: '8px 14px',
              fontSize: '12px',
              fontWeight: isActive ? 600 : 500,
              letterSpacing: '0.01em',
              color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
              backgroundColor: 'transparent',
              border: 'none',
              borderBottom: isActive
                ? '2px solid var(--aletheia-navy)'
                : '2px solid transparent',
              marginBottom: '-1px',
              transitionDuration: 'var(--motion-fast)',
              transitionTimingFunction: 'var(--ease-standard)',
            }}
            onMouseEnter={(e) => {
              if (!isActive) {
                (e.currentTarget as HTMLElement).style.color = 'var(--text-secondary)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive) {
                (e.currentTarget as HTMLElement).style.color = 'var(--text-muted)';
              }
            }}
          >
            {tab}
          </button>
        );
      })}
    </div>
  );
};
