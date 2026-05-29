import React from 'react';
import { ReportVersion } from '../../types';
import { VersionBadge } from './VersionBadge';
import { Database, Cpu } from 'lucide-react';

interface ReportVersionListProps {
  reports: ReportVersion[];
  activeReportId: string | null;
  onSelectReport: (report: ReportVersion) => void;
}

export const ReportVersionList: React.FC<ReportVersionListProps> = ({
  reports,
  activeReportId,
  onSelectReport,
}) => {
  const sortedReports = [...reports].sort((a, b) => b.version_number - a.version_number);

  return (
    <div
      className="flex flex-col p-4 w-64 bg-clinical-surface-bright border-l border-clinical-outline-variant h-full overflow-y-auto flex-shrink-0"
    >
      <h3 className="text-label-sm font-semibold text-clinical-on-surface-variant uppercase tracking-widest mb-4 px-1">
        Version History
      </h3>
      <div className="space-y-2">
        {sortedReports.map((report) => {
          const isActive = report.id === activeReportId;
          return (
            <button
              key={report.id}
              onClick={() => onSelectReport(report)}
              className={`list-item flex-col items-start text-left w-full transition-all duration-fast ease-clinical ${
                isActive
                  ? 'bg-clinical-primary-container border-clinical-primary shadow-card'
                  : 'bg-clinical-surface-bright border-clinical-outline-variant hover:bg-clinical-surface-container-low'
              }`}
            >
              <div className="flex justify-between items-center mb-1 w-full">
                <VersionBadge
                  version={report.version_number}
                  className={isActive ? 'bg-clinical-primary text-clinical-on-primary border-clinical-primary' : ''}
                />
                {report.grounding_used && (
                  <span title="Grounding Used">
                    <Database className="w-3.5 h-3.5 text-clinical-inverse-primary" />
                  </span>
                )}
              </div>
              <div className="text-label-sm text-clinical-on-surface-variant mb-1.5 tracking-widest">
                {new Date(report.created_at).toLocaleString()}
              </div>
              <div className="flex items-center gap-1.5 text-label-sm text-clinical-on-surface-variant tracking-wide">
                <Cpu className="w-3 h-3 flex-shrink-0" />
                <span className="truncate">{report.ai_provider} {report.ai_model}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
