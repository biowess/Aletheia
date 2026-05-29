import React from 'react';
import { Loader2 } from 'lucide-react';

interface SpinnerProps {
  className?: string;
  style?: React.CSSProperties;
}

export const Spinner: React.FC<SpinnerProps> = ({ className = '', style }) => {
  return (
    <Loader2
      className={`animate-spin text-clinical-inverse-primary ${className}`}
      style={style}
    />
  );
};
