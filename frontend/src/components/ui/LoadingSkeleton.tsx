import React from 'react';

interface LoadingSkeletonProps {
  width: string;
  height: string;
  className?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ width, height, className = '' }) => {
  return (
    <div
      style={{
        width,
        height,
        background: 'linear-gradient(90deg, var(--cf-surface-container-high) 25%, var(--cf-surface-container) 50%, var(--cf-surface-container-high) 75%)',
        backgroundSize: '200% 100%',
      }}
      className={`rounded-md animate-shimmer ${className}`}
    />
  );
};
