import React from 'react';
import { AlertCircle, X } from 'lucide-react';

interface ErrorBannerProps {
  message: string;
  onDismiss: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onDismiss }) => {
  return (
    <div className="w-full bg-clinical-error-container border border-clinical-error rounded-lg p-4 flex items-start justify-between shadow-card">
      <div className="flex gap-3">
        <AlertCircle className="w-5 h-5 text-clinical-error flex-shrink-0 mt-0.5" />
        <p className="text-body-md text-clinical-on-error-container font-medium">{message}</p>
      </div>
      <button
        onClick={onDismiss}
        className="text-clinical-error hover:bg-clinical-error/10 p-1 rounded-md ml-4 flex-shrink-0 transition-colors duration-fast ease-clinical focus:outline-none"
        aria-label="Dismiss error"
      >
        <X className="w-5 h-5" />
      </button>
    </div>
  );
};
