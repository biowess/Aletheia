import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertCircle } from 'lucide-react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-clinical-surface p-4">
          <div
            className="max-w-md w-full bg-clinical-surface-bright rounded-xl p-8 text-center border border-clinical-outline-variant animate-fade-up"
            style={{ boxShadow: 'var(--cf-shadow-card-elevated)' }}
          >
            <div className="w-14 h-14 bg-clinical-error-container rounded-full flex items-center justify-center mx-auto mb-5 border border-clinical-error">
              <AlertCircle className="w-7 h-7 text-clinical-error" />
            </div>
            <h2 className="text-headline-md font-semibold text-clinical-on-surface mb-2">
              Something went wrong
            </h2>
            <p className="text-body-md text-clinical-on-surface-variant mb-7">
              An unexpected error occurred. Please refresh the page to continue.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="btn-primary mx-auto"
            >
              Refresh Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
