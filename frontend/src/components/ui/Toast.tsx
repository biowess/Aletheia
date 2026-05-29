import React from 'react';
import { useToastStore } from '../../hooks/useToast';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

export const ToastContainer: React.FC = () => {
  const toasts = useToastStore((state) => state.toasts);
  const dismissToast = useToastStore((state) => state.dismissToast);

  return (
    <div className="fixed right-5 flex flex-col gap-2.5 pointer-events-none" style={{ bottom: '76px', zIndex: 1001 }}>
      {toasts.map((toast) => {
        const isSuccess = toast.type === 'success';
        const isError   = toast.type === 'error';
        const isInfo    = toast.type === 'info';

        const containerClass = isSuccess
          ? 'bg-clinical-secondary-container border-clinical-secondary'
          : isError
          ? 'bg-clinical-error-container border-clinical-error'
          : 'bg-clinical-primary-container border-clinical-primary';

        const textClass = isSuccess
          ? 'text-clinical-on-secondary-container'
          : isError
          ? 'text-clinical-on-error-container'
          : 'text-clinical-on-primary-container';

        const iconClass = isSuccess
          ? 'text-clinical-on-secondary-container'
          : isError
          ? 'text-clinical-error'
          : 'text-clinical-inverse-primary';

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-center justify-between w-80 px-4 py-3 rounded-lg border shadow-card-elevated animate-fade-up ${containerClass}`}
          >
            <div className="flex items-center gap-3 overflow-hidden">
              {isSuccess && <CheckCircle className={`w-5 h-5 flex-shrink-0 ${iconClass}`} />}
              {isError   && <AlertCircle className={`w-5 h-5 flex-shrink-0 ${iconClass}`} />}
              {isInfo    && <Info        className={`w-5 h-5 flex-shrink-0 ${iconClass}`} />}
              <p className={`text-body-md font-medium truncate ${textClass}`}>
                {toast.message}
              </p>
            </div>
            <button
              onClick={() => dismissToast(toast.id)}
              className={`ml-3 flex-shrink-0 p-1 rounded-md transition-colors duration-fast ease-clinical focus:outline-none ${textClass} hover:bg-clinical-outline-variant/30`}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
