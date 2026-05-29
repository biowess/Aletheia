import React from 'react';
import { ReportVersion } from '../../types';
import { EvolutionIndicator } from './EvolutionIndicator';
import { History, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface DifferentialEvolutionProps {
  currentReport: ReportVersion;
  previousReport: ReportVersion | null;
}

export const DifferentialEvolution: React.FC<DifferentialEvolutionProps> = ({
  currentReport,
  previousReport,
}) => {
  if (!previousReport) {
    return (
      <div className="text-sm text-clinical-on-surface-variant flex items-center gap-2 mb-6 bg-clinical-surface-container-low p-3 rounded-md border border-clinical-outline-variant">
        <History className="w-4 h-4" />
        No previous report versions to compare against.
      </div>
    );
  }

  const prevMap = new Map(previousReport.differentials?.map(d => [d.diagnosis, d]) || []);
  
  // Track diagnoses that were dropped
  const currentDiagnosesNames = new Set(currentReport.differentials?.map(d => d.diagnosis) || []);
  const droppedDiagnoses = previousReport.differentials?.filter(d => !currentDiagnosesNames.has(d.diagnosis)) || [];

  const determineStatus = (prevConf: number, currConf: number) => {
    const diff = currConf - prevConf;
    if (diff > 0.1) return 'increased';
    if (diff < -0.1) return 'decreased';
    return 'stable';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'increased': return <TrendingUp className="w-4 h-4 text-emerald-600" />;
      case 'decreased': return <TrendingDown className="w-4 h-4 text-amber-600" />;
      case 'dropped': return <Minus className="w-4 h-4 text-red-600" />;
      default: return <Minus className="w-4 h-4 text-clinical-on-surface-variant" />;
    }
  };

  return (
    <div className="mb-6">
      <h3 className="text-sm font-semibold text-clinical-on-surface uppercase tracking-wider mb-3 flex items-center gap-2">
        <History className="w-4 h-4 text-clinical-on-surface-variant" />
        Evolution from v{previousReport.version_number}
      </h3>
      
      <div className="space-y-2">
        {/* Current Diagnoses Evolution */}
        {currentReport.differentials?.map((dx, index) => {
          const prevConf = prevMap.get(dx.diagnosis)?.confidence;
          const currConf = dx.confidence;
          
          let status = 'new';
          if (prevConf !== undefined) {
            status = determineStatus(prevConf, currConf);
          }

          return (
            <div
              key={index}
              className="flex items-center justify-between p-3 rounded-lg border border-clinical-outline-variant bg-clinical-surface-bright text-sm hover:shadow-sm transition-shadow"
            >
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-clinical-surface-container flex items-center justify-center font-bold text-clinical-on-surface-variant text-xs">
                  {index + 1}
                </div>
                <div>
                  <span className="font-semibold text-clinical-on-surface">{dx.diagnosis}</span>
                  <div className="text-xs text-clinical-on-surface-variant mt-0.5">
                    Confidence: {(currConf * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {status === 'new' ? (
                  <span className="text-xs font-semibold text-clinical-inverse-primary bg-clinical-primary-container px-2 py-0.5 rounded-full uppercase tracking-wider">
                    New
                  </span>
                ) : (
                  <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-clinical-surface-container-low border border-clinical-outline-variant text-xs font-medium">
                    {getStatusIcon(status)}
                    <span className="capitalize">{status}</span>
                    <span className="text-clinical-on-surface-variant ml-1 font-mono">
                      {(prevConf! * 100).toFixed(0)}% → {(currConf * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Dropped Diagnoses */}
        {droppedDiagnoses.map((dx, index) => (
          <div
            key={`dropped-${index}`}
            className="flex items-center justify-between p-3 rounded-lg border border-red-100 bg-red-50 text-sm opacity-75"
          >
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-full bg-red-100 flex items-center justify-center text-red-500">
                <Minus className="w-3.5 h-3.5" />
              </div>
              <span className="font-semibold text-red-900 line-through">{dx.diagnosis}</span>
            </div>
            
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-red-100 border border-red-200 text-xs font-medium text-red-800">
              {getStatusIcon('dropped')}
              <span className="uppercase tracking-wider text-[10px] font-bold">Dropped</span>
              <span className="text-red-600/70 ml-1 font-mono">
                Was {(dx.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
