import React from 'react';

interface ToggleSwitchProps {
  value: boolean;
  onChange: (v: boolean) => void;
}

export const ToggleSwitch: React.FC<ToggleSwitchProps> = ({ value, onChange }) => {
  return (
    <label className="flex items-center gap-2 cursor-pointer select-none">
      <input
        type="checkbox"
        checked={value}
        onChange={(e) => onChange(e.target.checked)}
        className="sr-only peer"
      />
      <div
        className="relative w-8 h-4 cursor-pointer rounded-sm transition-all"
        style={{
          backgroundColor: value ? 'var(--state-info)' : 'var(--border-default)',
          transitionDuration: 'var(--motion-fast)',
        }}
        onClick={(e) => {
          e.preventDefault();
          onChange(!value);
        }}
      >
        <div
          className="absolute top-0.5 h-3 w-3 bg-white rounded-sm transition-all shadow-sm"
          style={{
            left: value ? 'calc(100% - 14px)' : '2px',
            transitionDuration: 'var(--motion-fast)',
          }}
        />
      </div>
    </label>
  );
};
