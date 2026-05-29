import React from 'react';

interface WorkspaceSplitPaneProps {
  left: React.ReactNode;
  right: React.ReactNode;
  bottomPanel?: React.ReactNode;
  showBottom?: boolean;
}

export const WorkspaceSplitPane: React.FC<WorkspaceSplitPaneProps> = ({
  left,
  right,
  bottomPanel,
  showBottom = false,
}) => {
  return (
    <div
      className="flex flex-col h-full overflow-hidden"
      style={{ backgroundColor: 'var(--bg-primary)' }}
    >
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel – clinical input */}
        <div
          className="w-2/5 min-w-[360px] h-full overflow-y-auto"
          style={{
            borderRight: '1px solid var(--border-strong)',
            backgroundColor: 'var(--surface-primary)',
          }}
        >
          {left}
        </div>

        {/* Right Panel – reasoning output */}
        <div
          className="w-3/5 h-full overflow-y-auto"
          style={{ backgroundColor: 'var(--bg-secondary)' }}
        >
          {right}
        </div>
      </div>

      {/* Optional Bottom Panel (Timeline) */}
      {showBottom && bottomPanel && (
        <div
          className="h-72 overflow-y-auto"
          style={{
            borderTop: '1px solid var(--border-strong)',
            backgroundColor: 'var(--surface-primary)',
          }}
        >
          {bottomPanel}
        </div>
      )}
    </div>
  );
};
