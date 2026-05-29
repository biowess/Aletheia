import { Link } from 'react-router-dom';

export const EmptyState = () => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border-2 border-dashed border-clinical-outline-variant rounded-xl bg-clinical-surface-container-low animate-fade-up">
      <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-clinical-surface-container-highest border border-clinical-outline-variant/50 mb-5 shadow-sm">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-clinical-on-surface-variant">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
          <path d="M8 7h6" />
          <path d="M8 11h8" />
        </svg>
      </div>
      <h3 className="text-headline-md font-semibold text-clinical-on-surface mb-2">No cases yet</h3>
      <p className="text-body-md text-clinical-on-surface-variant mb-8 max-w-sm">
        Get started by creating your first clinical case. You can document anamnesis, physical exams, and lab results.
      </p>
      <Link
        to="/cases/new"
        className="btn-primary"
      >
        Create your first case
      </Link>
    </div>
  );
};
